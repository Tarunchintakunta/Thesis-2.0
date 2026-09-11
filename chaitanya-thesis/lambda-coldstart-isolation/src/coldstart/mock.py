"""Mock Lambda + CloudWatch for DATA_MODE=mock.   *** SYNTHETIC - NOT MEASURED ***

Only for exercising the pipeline without an AWS account. Every number comes
from configs/mock_model.yaml, which is a set of placeholder assumptions, so
nothing produced in mock mode is evidence about AWS Lambda.

What the mock does model (because the pipeline has to cope with it):
  * one request per execution environment at a time (bursts need new environments)
  * environments are reused while warm and reclaimed after an idle lifetime
  * a configuration change (env var or memory) retires all environments
  * CPU share grows with memory up to one vCPU at 1769 MB
  * EventBridge warmer pings arrive at a fixed rate and keep one environment alive
  * cold REPORT lines carry "Init Duration", warm ones do not
"""
from __future__ import annotations

import math
import random
import uuid
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "configs" / "mock_model.yaml"
FULL_VCPU_MB = 1769
# 2026-01-01T00:00:00Z - mock runs live on a virtual clock that starts here
EPOCH0 = 1_767_225_600.0


def load_model(path: str | Path = MODEL_PATH) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class VirtualClock:
    def __init__(self, start: float = EPOCH0):
        self.t = float(start)

    def now(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += max(0.0, float(seconds))


@dataclass
class Env:
    created: float
    last_used: float
    busy_until: float
    idle_lifetime_s: float


@dataclass
class Warmer:
    interval_s: float
    next_t: float


class MockLambda:
    """Execution-environment pools for a set of functions on a virtual clock."""

    def __init__(self, functions: dict[str, tuple[str, str]], model: dict | None = None,
                 clock: VirtualClock | None = None, seed: int = 0, memory_mb: int = 1024,
                 stack: str = "coldstart-study"):
        self.m = model or load_model()
        self.clock = clock or VirtualClock()
        self.rng = random.Random(seed)
        self.functions = dict(functions)
        self.memory = {f: memory_mb for f in functions}
        self.pools: dict[str, list[Env]] = {f: [] for f in functions}
        self.warmers: dict[str, Warmer] = {}
        self.logs: list[dict] = []
        self.stack = stack
        self._max_life_s = self.m["lifecycle"]["max_lifetime_min"] * 60

    # ---- sampling -------------------------------------------------------------------------
    def _lognorm(self, median: float, sigma: float) -> float:
        return median * math.exp(self.rng.gauss(0.0, sigma))

    def _cpu_factor(self, memory_mb: int, exponent: float) -> float:
        return max(1.0, FULL_VCPU_MB / memory_mb) ** exponent

    def init_ms(self, runtime: str, variant: str, memory_mb: int) -> float:
        p = self.m["init"]
        cpu = p["runtime_ms"][runtime] + (p["package_extra_ms"][runtime] if variant == "default" else 0.0)
        cpu *= self._cpu_factor(memory_mb, p["memory_exponent"])
        return self._lognorm(p["platform_fixed_ms"] + cpu, p["sigma"])

    def duration_ms(self, runtime: str, memory_mb: int, first: bool) -> float:
        p = self.m["duration"]
        work = p["work_ms_at_1vcpu"][runtime] * self._cpu_factor(memory_mb, p["memory_exponent"])
        if first:
            work *= p["first_invoke_factor"][runtime]
        return self._lognorm(work + p["overhead_ms"], p["sigma"])

    def _lifetime_s(self) -> float:
        p = self.m["lifecycle"]["idle_lifetime_min"]
        return self._lognorm(p["median"], p["sigma"]) * 60

    def _request_id(self) -> str:
        return str(uuid.UUID(int=self.rng.getrandbits(128), version=4))

    # ---- control plane --------------------------------------------------------------------
    def set_memory(self, fn: str, memory_mb: int) -> None:
        self.memory[fn] = int(memory_mb)
        self.pools[fn].clear()  # new configuration -> new environments

    def force_cold(self, fn: str) -> None:
        if self.rng.random() < self.m["lifecycle"]["update_env_cold_probability"]:
            self.pools[fn].clear()

    def enable_warmer(self, fn: str, interval_s: float) -> None:
        first = self.clock.now() + self.rng.uniform(0, interval_s)
        self.warmers[fn] = Warmer(interval_s=interval_s, next_t=first)

    def disable_warmer(self, fn: str) -> None:
        self.warmers.pop(fn, None)

    def run_due_warmers(self) -> None:
        now = self.clock.now()
        while True:
            due = [(w.next_t, fn) for fn, w in self.warmers.items() if w.next_t <= now]
            if not due:
                return
            t, fn = min(due)
            self._invoke_at(fn, {"warmer": True}, t)
            self.warmers[fn].next_t += self.warmers[fn].interval_s

    # ---- data plane -----------------------------------------------------------------------
    def invoke(self, fn: str, payload: dict) -> dict:
        self.run_due_warmers()
        return self._invoke_at(fn, payload, self.clock.now())

    def invoke_concurrent(self, fn: str, payload: dict, n: int) -> list[dict]:
        self.run_due_warmers()
        t = self.clock.now()
        return [self._invoke_at(fn, payload, t) for _ in range(n)]

    def _invoke_at(self, fn: str, payload: dict, t: float) -> dict:
        runtime, variant = self.functions[fn]
        mem = self.memory[fn]
        pool = self.pools[fn]
        pool[:] = [e for e in pool if t - e.last_used <= e.idle_lifetime_s and t - e.created <= self._max_life_s]
        idle = [e for e in pool if e.busy_until <= t]
        warmer = bool(payload.get("warmer"))
        if idle:
            env, init = max(idle, key=lambda e: e.last_used), None
        else:
            env = Env(created=t, last_used=t, busy_until=t, idle_lifetime_s=self._lifetime_s())
            pool.append(env)
            init = self.init_ms(runtime, variant, mem)
        if warmer:
            dur = self._lognorm(self.m["warmer_ping_ms"], 0.2)
        else:
            dur = self.duration_ms(runtime, mem, first=init is not None)
        error = (not warmer) and self.rng.random() < self.m["errors"]["probability"]
        start = t + (init or 0.0) / 1000
        env.busy_until = env.last_used = start + dur / 1000
        rid = self._request_id()
        used = self.m["max_memory_used_mb"][f"{runtime}-{variant}"]
        line = (f"REPORT RequestId: {rid}\tDuration: {dur:.2f} ms\tBilled Duration: {math.ceil(dur)} ms\t"
                f"Memory Size: {mem} MB\tMax Memory Used: {min(used, mem)} MB\t")
        if init is not None:
            line += f"Init Duration: {init:.2f} ms\t"
        group = f"/aws/lambda/{self.stack}-{fn}"
        ts = int(start * 1000)
        self.logs.append({"log_group": group, "timestamp": ts, "message": f"START RequestId: {rid} Version: $LATEST"})
        self.logs.append({"log_group": group, "timestamp": ts + int(dur),
                          "message": f"END RequestId: {rid}"})
        self.logs.append({"log_group": group, "timestamp": ts + int(dur), "message": line})
        rtt = (init or 0.0) + dur + self._lognorm(self.m["network"]["median_ms"], self.m["network"]["sigma"])
        return {"request_id": rid, "status": 200, "function_error": "Unhandled" if error else None,
                "rtt_ms": round(rtt, 3), "log_tail": "\n".join(m["message"] for m in self.logs[-3:]),
                "t_start": t}
