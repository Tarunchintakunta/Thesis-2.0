"""Local process-start benchmark - a PROXY for the Lambda init phase, not Lambda itself.

For every (runtime, variant) a brand-new process is started, the package is
loaded exactly as built for Lambda (build/<runtime>-<variant>/), the fixed
payload is run once and three numbers are kept:

    init_proxy_ms   = handler loaded  - process spawn   (runtime start + module/class loading)
    handler_ms      = invocation done - handler loaded  (the workload itself)
    process_wall_ms = whole child process as seen by the parent

This shows what package pruning and runtime choice cost *on the machine it
runs on*. It has no Firecracker micro-VM, no code download from S3 and no
Lambda runtime API, so the absolute numbers are NOT Lambda Init Durations and
must never be reported as such.
"""
from __future__ import annotations

import json
import os
import platform
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"
BENCH = ROOT / "scripts" / "bench"
PAYLOAD = ROOT / "payloads" / "fixed_payload.json"
VARIANTS = [(r, v) for r in ("python", "nodejs", "java") for v in ("default", "optimised")]


def is_built(runtime: str, variant: str, build: Path = BUILD) -> bool:
    pkg = build / f"{runtime}-{variant}"
    marker = {"python": "handler.py", "nodejs": "index.mjs", "java": "function.jar"}[runtime]
    return (pkg / marker).exists()


def command(runtime: str, variant: str, payload_path: Path = PAYLOAD, build: Path = BUILD) -> list[str]:
    pkg = build / f"{runtime}-{variant}"
    if runtime == "python":
        py = os.environ.get("BENCH_PYTHON", sys.executable)
        # -B: never write .pyc files. /var/task is read-only on Lambda, so a zip without
        # bytecode is compiled from source on every cold start - the bench must do the same
        return [py, "-B", "-s", "-S", str(BENCH / "python_bench.py"), str(pkg), str(payload_path)]
    if runtime == "nodejs":
        return [os.environ.get("BENCH_NODE", "node"), str(BENCH / "node_bench.mjs"), str(pkg), str(payload_path)]
    if runtime == "java":
        payload = json.loads(Path(payload_path).read_text())
        items = ",".join(str(int(i)) for i in payload.get("items", []))
        return [os.environ.get("BENCH_JAVA", "java"), "-cp", str(pkg / "function.jar"), "coldstart.Bench",
                str(payload["seed"]), str(payload["iterations"]), items]
    raise ValueError(f"unknown runtime {runtime}")


def run_once(runtime: str, variant: str, payload_path: Path = PAYLOAD, build: Path = BUILD,
             timeout: float = 120.0) -> dict:
    cmd = command(runtime, variant, payload_path, build)
    row = {"runtime": runtime, "variant": variant}
    t_spawn_us = time.time_ns() // 1000
    t0 = time.perf_counter()
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    row["process_wall_ms"] = round((time.perf_counter() - t0) * 1000, 3)
    if proc.returncode != 0:
        row.update(ok=False, error=(proc.stderr or proc.stdout)[-400:].strip())
        return row
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    row.update(
        ok=True,
        init_proxy_ms=round((out["t_init_us"] - t_spawn_us) / 1000, 3),
        handler_ms=round((out["t_done_us"] - out["t_init_us"]) / 1000, 3),
        digest=out["digest"],
        items_total=int(out["items_total"]),
    )
    return row


def schedule(reps: int, variants, seed: int) -> list[tuple[int, str, str]]:
    """Interleaved randomised blocks: every block holds each variant once, in a new random order."""
    rng = random.Random(seed)
    order = []
    for rep in range(reps):
        block = list(variants)
        rng.shuffle(block)
        order += [(rep, r, v) for r, v in block]
    return order


def run_benchmark(reps: int, variants=None, seed: int = 42, warmup: int = 2,
                  payload_path: Path = PAYLOAD, build: Path = BUILD, progress=None) -> list[dict]:
    variants = [tuple(v) for v in (variants or [v for v in VARIANTS if is_built(*v, build=build)])]
    rows = []
    # warm-up rounds fill the OS file cache; they are kept but flagged and never analysed
    for w in range(warmup):
        for r, v in variants:
            rows.append({**run_once(r, v, payload_path, build), "rep": -1 - w, "warmup": True})
    for seq, (rep, r, v) in enumerate(schedule(reps, variants, seed)):
        row = run_once(r, v, payload_path, build)
        row.update(rep=rep, seq=seq, warmup=False)
        rows.append(row)
        if progress:
            progress(seq, row)
    return rows


def _version(cmd: list[str]) -> str:
    if shutil.which(cmd[0]) is None:
        return "not installed"
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return (p.stdout or p.stderr).strip().splitlines()[0] if (p.stdout or p.stderr).strip() else "unknown"


def machine_info() -> dict:
    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "python": platform.python_version(),
        "node": _version([os.environ.get("BENCH_NODE", "node"), "--version"]),
        "java": _version([os.environ.get("BENCH_JAVA", "java"), "-version"]),
        "github_actions": os.environ.get("GITHUB_ACTIONS") == "true",
        "runner": os.environ.get("RUNNER_OS", "") + " " + os.environ.get("ImageOS", ""),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_sha": os.environ.get("GITHUB_SHA"),
    }
