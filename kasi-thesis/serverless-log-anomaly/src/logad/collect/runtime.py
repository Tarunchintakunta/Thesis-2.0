"""Local AWS Lambda runtime emulator.

Runs the real ``infra/lambda_app/handler.py`` on a virtual clock and writes the
log lines a Lambda function writes to CloudWatch Logs:

    START RequestId: <id> Version: $LATEST
    [INFO]  2026-06-01T10:00:00.123Z  <id>  {"route": ..., "status": 201, ...}
    END RequestId: <id>
    REPORT RequestId: <id>  Duration: 12.34 ms  Billed Duration: 13 ms  Memory Size: 256 MB  Max Memory Used: 79 MB  [Init Duration: 380.12 ms]

Execution environments are modelled explicitly: a request goes to a free warm
environment if there is one, otherwise a new environment starts (cold start,
Init Duration); above the reserved concurrency the request is throttled.
Idle environments are reclaimed after a random idle time, and every
environment is recycled after a maximum lifetime. A crash or timeout kills
the environment. Memory exhaustion is modelled with a working-set draw per
invocation: if it does not fit the memory size the process is killed.

Besides the log lines it keeps one metrics record per request, which is what
CloudWatch metrics (Invocations, Errors, Throttles, Duration, API 5XX) would
show - the threshold alarms (detector D3) use those.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import logging
import math
import random
from dataclasses import dataclass, field
from pathlib import Path

from logad.collect.fake_dynamo import FakeTable, InvocationTimeout
from logad.config import PROJECT_ROOT

HANDLER_PATH = PROJECT_ROOT / "infra" / "lambda_app" / "handler.py"


class VirtualClock:
    def __init__(self, now: float) -> None:
        self.now = float(now)

    def advance(self, seconds: float) -> None:
        self.now += max(0.0, seconds)

    def __call__(self) -> float:
        return self.now


def iso(ts: float) -> str:
    return dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def load_handler(path: Path = HANDLER_PATH):
    """Import the Lambda handler file as its own module (like the runtime does)."""
    spec = importlib.util.spec_from_file_location("orders_handler", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class _Capture(logging.Handler):
    """Formats handler log records the way the Lambda python runtime does."""

    def __init__(self) -> None:
        super().__init__(logging.DEBUG)
        self.records: list[tuple[str, str]] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append((record.levelname, record.getMessage()))


@dataclass
class Env:
    env_id: int
    created: float
    idle_limit: float
    busy_until: float = 0.0
    last_used: float = 0.0


@dataclass
class Context:
    aws_request_id: str
    memory_limit_in_mb: int
    function_name: str = "orders-api"


@dataclass
class LambdaEmulator:
    runtime_cfg: dict
    db_cfg: dict
    fault_cfg: dict
    rng: random.Random
    start: float
    handler_path: Path = HANDLER_PATH
    lines: list[tuple[float, str]] = field(default_factory=list)
    metrics: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.clock = VirtualClock(self.start)
        self.handler = load_handler(self.handler_path)
        self.handler.clock = self.clock
        self.capture = _Capture()
        self.handler.LOG.handlers = [self.capture]
        self.handler.LOG.propagate = False
        self.table = FakeTable(self.clock, self.rng, self.db_cfg, self.fault_cfg)
        self.envs: list[Env] = []
        self._next_env = 0
        self.fault: str | None = None

    # -- faults ------------------------------------------------------------------
    def set_fault(self, category: str | None) -> None:
        self.fault = category
        self.table.fault = category

    @property
    def memory_mb(self) -> int:
        if self.fault == "resource_exhaustion":
            return int(self.fault_cfg["resource_exhaustion"]["memory_mb"])
        return int(self.runtime_cfg["memory_mb"])

    # -- environments -------------------------------------------------------------
    def _reclaim(self, t: float) -> None:
        keep = []
        for env in self.envs:
            idle = env.busy_until <= t and t - max(env.last_used, env.created) > env.idle_limit
            too_old = env.busy_until <= t and t - env.created > self.runtime_cfg["max_env_lifetime_s"]
            if not (idle or too_old):
                keep.append(env)
        self.envs = keep

    def _acquire(self, t: float) -> tuple[Env | None, bool]:
        self._reclaim(t)
        free = [e for e in self.envs if e.busy_until <= t]
        if free:
            return max(free, key=lambda e: e.last_used), False
        if len(self.envs) >= self.runtime_cfg["reserved_concurrency"]:
            return None, False
        lo, hi = self.runtime_cfg["idle_reclaim_s"]
        env = Env(self._next_env, created=t, idle_limit=self.rng.uniform(lo, hi))
        self._next_env += 1
        self.envs.append(env)
        return env, True

    def _request_id(self) -> str:
        h = f"{self.rng.getrandbits(128):032x}"
        return f"{h[:8]}-{h[8:12]}-4{h[13:16]}-a{h[17:20]}-{h[20:32]}"

    # -- one request ---------------------------------------------------------------
    def invoke(self, t: float, event: dict) -> dict:
        env, cold = self._acquire(t)
        route = event.get("routeKey", "")
        if env is None:
            rec = {"t": t, "route": route, "throttled": True, "status": 429, "error": False,
                   "duration_ms": 0.0, "cold": False, "timeout": False, "killed": False}
            self.metrics.append(rec)
            return rec

        rt = self.runtime_cfg
        rid = self._request_id()
        mem = self.memory_mb
        exhausted = self.fault == "resource_exhaustion"
        init_ms = self.rng.lognormvariate(math.log(rt["cold_init_median_ms"]), 0.25) if cold else 0.0
        begin = t + init_ms / 1000.0
        self.clock.now = begin
        timeout_s = float(rt["timeout_s"])
        self.table.deadline = begin + timeout_s
        gc = self.fault_cfg["resource_exhaustion"]["gc_factor"] if exhausted else 1.0
        self.table.slowdown = gc

        if exhausted:
            re = self.fault_cfg["resource_exhaustion"]
            working_set = self.rng.gauss(re["ws_mean_mb"], re["ws_sd_mb"])
        else:
            working_set = self.rng.gauss(rt["ws_mean_mb"], rt["ws_sd_mb"])
        killed = working_set > mem
        used_mb = int(min(mem, max(40, round(working_set))))

        self.lines.append((t, f"START RequestId: {rid} Version: $LATEST"))
        self.capture.records.clear()
        timed_out = False
        status = 502
        if not killed:
            self.handler._COLD_START = cold
            ctx = Context(aws_request_id=rid, memory_limit_in_mb=mem)
            cpu = self.rng.lognormvariate(math.log(rt["cpu_median_ms"]), 0.3) * gc / 1000.0
            self.clock.advance(cpu / 2)
            try:
                resp = self.handler.lambda_handler(event, ctx, table=self.table)
                status = int(resp["statusCode"])
                self.clock.advance(cpu / 2)
            except InvocationTimeout:
                timed_out = True
                status = 503
        else:
            # the process dies part way through
            self.clock.advance(self.rng.uniform(0.005, 0.05) * gc)

        duration_ms = timeout_s * 1000.0 if timed_out else (self.clock.now - begin) * 1000.0
        end = begin + duration_ms / 1000.0
        app_t = max(begin, end - 0.0005)
        for level, message in self.capture.records:
            self.lines.append((app_t, f"[{level}]\t{iso(app_t)}\t{rid}\t{message}"))
        if timed_out:
            self.lines.append((end, f"{iso(end)} {rid} Task timed out after {timeout_s:.2f} seconds"))
        if killed:
            self.lines.append((end, f"RequestId: {rid} Error: Runtime exited with error: signal: killed"))
            self.lines.append((end, "Runtime.ExitError"))
        self.lines.append((end, f"END RequestId: {rid}"))
        report = (f"REPORT RequestId: {rid}\tDuration: {duration_ms:.2f} ms\t"
                  f"Billed Duration: {math.ceil(duration_ms)} ms\tMemory Size: {mem} MB\t"
                  f"Max Memory Used: {used_mb} MB")
        if cold:
            report += f"\tInit Duration: {init_ms:.2f} ms"
        if timed_out:
            report += "\tStatus: timeout"
        elif killed:
            report += "\tStatus: error\tError Type: Runtime.ExitError"
        self.lines.append((end, report))

        env.busy_until = end
        env.last_used = end
        if timed_out or killed:
            self.envs = [e for e in self.envs if e is not env]  # environment is gone

        rec = {"t": t, "route": route, "throttled": False, "status": status,
               "error": timed_out or killed, "duration_ms": duration_ms, "cold": cold,
               "timeout": timed_out, "killed": killed}
        self.metrics.append(rec)
        return rec

    def sorted_lines(self) -> list[tuple[float, str]]:
        return sorted(self.lines, key=lambda x: x[0])
