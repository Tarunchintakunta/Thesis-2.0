"""Backends behind the invokers: live AWS (boto3) or the mock.

DATA_MODE=live  -> LiveBackend, real Lambda functions from infra/template.yaml
DATA_MODE=mock  -> MockBackend, synthetic REPORT lines on a virtual clock (default,
                   so nobody spends money by accident)

Both expose the same small interface, so the phase runners in driver.py do not
know which one they are talking to. Every record keeps `data_mode`, so mock rows
can never be mixed up with measured ones later.
"""
from __future__ import annotations

import base64
import json
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .mock import MockLambda, VirtualClock

# logical function name -> (runtime, package variant); the deployed name is "<stack>-<key>"
FUNCTIONS = {
    "python-default": ("python", "default"),
    "python-optimised": ("python", "optimised"),
    "python-bytecode": ("python", "bytecode"),
    "nodejs-default": ("nodejs", "default"),
    "nodejs-optimised": ("nodejs", "optimised"),
    "java-default": ("java", "default"),
    "java-optimised": ("java", "optimised"),
    "warm-target": ("python", "optimised"),
    "warm-control": ("python", "optimised"),
}


def data_mode() -> str:
    mode = os.environ.get("DATA_MODE", "mock").strip().lower()
    if mode not in ("live", "mock"):
        raise ValueError("DATA_MODE must be live or mock")
    return mode


class MockBackend:
    mode = "mock"

    def __init__(self, seed: int = 0, model: dict | None = None, stack: str = "coldstart-study"):
        self.clock = VirtualClock()
        self.lam = MockLambda(FUNCTIONS, model=model, clock=self.clock, seed=seed, stack=stack)

    def now(self) -> float:
        return self.clock.now()

    def sleep(self, seconds: float) -> None:
        self.clock.advance(seconds)
        self.lam.run_due_warmers()

    def memory_of(self, fn: str) -> int:
        return self.lam.memory[fn]

    def set_memory(self, fn: str, memory_mb: int) -> None:
        self.lam.set_memory(fn, memory_mb)

    def force_cold(self, fn: str) -> None:
        self.lam.force_cold(fn)

    def enable_warmer(self, fn: str, interval_s: float) -> None:
        self.lam.enable_warmer(fn, interval_s)

    def disable_warmer(self, fn: str) -> None:
        self.lam.disable_warmer(fn)

    def invoke(self, fn: str, payload: dict) -> dict:
        res = self.lam.invoke(fn, payload)
        self.clock.advance(res["rtt_ms"] / 1000)  # the client waits for the answer
        return res

    def invoke_concurrent(self, fn: str, payload: dict, n: int) -> list[dict]:
        out = self.lam.invoke_concurrent(fn, payload, n)
        self.clock.advance(max(r["rtt_ms"] for r in out) / 1000)
        return out

    def export_logs(self, out_dir: str | Path) -> int:
        """Write the synthetic CloudWatch events like collect_logs.py writes real ones."""
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        events, self.lam.logs = self.lam.logs, []
        with open(out_dir / "events.jsonl", "a", encoding="utf-8") as fh:
            for e in events:
                fh.write(json.dumps(e) + "\n")
        return len(events)


class LiveBackend:
    mode = "live"

    def __init__(self, stack: str, region: str, session=None):
        import boto3  # only needed for live runs

        s = session or boto3.Session(region_name=region)
        self.lam = s.client("lambda")
        self.events = s.client("events")
        self.stack = stack
        self._mem: dict[str, int] = {}

    def name(self, fn: str) -> str:
        return f"{self.stack}-{fn}"

    def now(self) -> float:
        return time.time()

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def memory_of(self, fn: str) -> int:
        if fn not in self._mem:
            self._mem[fn] = self.lam.get_function_configuration(FunctionName=self.name(fn))["MemorySize"]
        return self._mem[fn]

    def _update(self, fn: str, **changes) -> None:
        self.lam.update_function_configuration(FunctionName=self.name(fn), **changes)
        self.lam.get_waiter("function_updated_v2").wait(
            FunctionName=self.name(fn), WaiterConfig={"Delay": 1, "MaxAttempts": 180})

    def set_memory(self, fn: str, memory_mb: int) -> None:
        self._update(fn, MemorySize=int(memory_mb))
        self._mem[fn] = int(memory_mb)

    def force_cold(self, fn: str) -> None:
        # a new configuration version means new execution environments on the next call
        cfg = self.lam.get_function_configuration(FunctionName=self.name(fn))
        env = dict(cfg.get("Environment", {}).get("Variables", {}))
        env["COLD_TOKEN"] = uuid.uuid4().hex
        self._update(fn, Environment={"Variables": env})

    def enable_warmer(self, fn: str, interval_s: float) -> None:
        # the rule and its rate live in the template; here it is only switched on
        self.events.enable_rule(Name=f"{self.stack}-warmer")

    def disable_warmer(self, fn: str) -> None:
        self.events.disable_rule(Name=f"{self.stack}-warmer")

    def invoke(self, fn: str, payload: dict) -> dict:
        t = time.time()
        t0 = time.perf_counter()
        resp = self.lam.invoke(FunctionName=self.name(fn), Payload=json.dumps(payload).encode(), LogType="Tail")
        rtt = (time.perf_counter() - t0) * 1000
        resp["Payload"].read()
        tail = base64.b64decode(resp.get("LogResult") or b"").decode("utf-8", "replace")
        return {"request_id": resp["ResponseMetadata"]["RequestId"], "status": resp["StatusCode"],
                "function_error": resp.get("FunctionError"), "rtt_ms": round(rtt, 3),
                "log_tail": tail, "t_start": t}

    def invoke_concurrent(self, fn: str, payload: dict, n: int) -> list[dict]:
        gate = threading.Barrier(n)

        def one(_):
            gate.wait()  # line all threads up so they really arrive together
            return self.invoke(fn, payload)

        with ThreadPoolExecutor(max_workers=n) as pool:
            return list(pool.map(one, range(n)))

    def export_logs(self, out_dir) -> int:
        return 0  # live logs are pulled from CloudWatch by scripts/collect_logs.py


def get_backend(cfg: dict, seed: int = 0):
    if data_mode() == "live":
        return LiveBackend(cfg["stack_name"], cfg["region"])
    return MockBackend(seed=seed, stack=cfg["stack_name"])
