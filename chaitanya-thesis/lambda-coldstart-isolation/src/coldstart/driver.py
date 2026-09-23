"""Phase runners used by scripts/invoke_idle.py, invoke_steady.py and invoke_burst.py.

Every phase writes <out>/<phase>/invocations.jsonl (one client-side row per
invocation, with the REPORT line from the log tail when there is one) and
run_info.json. Configurations are interleaved in randomised blocks - each
block contains every cell once in a fresh random order - so time-of-day drift
hits all cells equally (Wen et al. 2025).
"""
from __future__ import annotations

import datetime as dt
import json
import random
import time
from pathlib import Path

from .backends import FUNCTIONS
from .config import ROOT, phase_cells, resolve
from .report_parser import parse_log_text


def iso(t: float) -> str:
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat(timespec="milliseconds")


def randomised_blocks(cells: list, reps: int, rng: random.Random) -> list[tuple[int, tuple]]:
    order = []
    for rep in range(reps):
        block = list(cells)
        rng.shuffle(block)
        order += [(rep, c) for c in block]
    return order


class Recorder:
    def __init__(self, out_dir: Path, backend, phase: str):
        self.out = Path(out_dir)
        self.out.mkdir(parents=True, exist_ok=True)
        self.path = self.out / "invocations.jsonl"
        self.backend = backend
        self.phase = phase
        self.rows = 0

    def invoke(self, fn: str, payload: dict, **meta) -> dict:
        return self.add(self.backend.invoke(fn, payload), fn, **meta)

    def add(self, res: dict, fn: str, **meta) -> dict:
        reports = parse_log_text(res.get("log_tail") or "")
        rep = reports[-1] if reports else None
        runtime, variant = FUNCTIONS[fn]
        row = {
            "seq": self.rows, "phase": self.phase, "data_mode": self.backend.mode,
            "function": fn, "runtime": runtime, "variant": variant,
            "memory_mb": self.backend.memory_of(fn),
            "t_start": round(res["t_start"], 3), "t_start_utc": iso(res["t_start"]),
            "request_id": res["request_id"], "status": res["status"],
            "function_error": res["function_error"], "rtt_ms": res["rtt_ms"],
            "tail_report": rep.to_dict() if rep else None,
            **meta,
        }
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
        self.rows += 1
        return row


def load_payload(cfg: dict) -> dict:
    with open(resolve(cfg.get("payload", ROOT / "payloads/fixed_payload.json")), encoding="utf-8") as fh:
        return json.load(fh)


def _prepare(backend, fn: str, memory_mb: int) -> bool:
    """Set the memory if needed. Returns True when that already forced new environments."""
    if backend.memory_of(fn) != memory_mb:
        backend.set_memory(fn, memory_mb)
        return True
    return False


def _make_cold(backend, cfg: dict, fn: str, memory_mb: int) -> None:
    changed = _prepare(backend, fn, memory_mb)
    if cfg["force_cold"] == "update_env":
        if not changed:
            backend.force_cold(fn)
    else:
        backend.sleep(cfg["idle_gap_min"] * 60)


def run_cold(backend, cfg, ph, rec, rng, payload):
    for rep, (r, v, m) in randomised_blocks(phase_cells(ph), int(ph["reps"]), rng):
        fn = f"{r}-{v}"
        _make_cold(backend, cfg, fn, m)
        meta = {"rep": rep, "pattern": "idle", "warming": "off", "force_cold": cfg["force_cold"]}
        rec.invoke(fn, payload, role="measure", intended_cold=True, **meta)
        for _ in range(int(ph.get("follow_up_warm", 0))):
            rec.invoke(fn, payload, role="follow_up", intended_cold=False, **meta)


def run_warm(backend, cfg, ph, rec, rng, payload):
    for rep, (r, v, m) in randomised_blocks(phase_cells(ph), int(ph["reps"]), rng):
        fn = f"{r}-{v}"
        _prepare(backend, fn, m)
        meta = {"rep": rep, "pattern": "steady", "warming": "off"}
        for _ in range(int(ph.get("warmup_per_block", 2))):
            rec.invoke(fn, payload, role="warmup", intended_cold=False, **meta)
        for _ in range(int(ph.get("measured_per_block", 1))):
            rec.invoke(fn, payload, role="measure", intended_cold=False, **meta)


def run_warming(backend, cfg, ph, rec, rng, payload):
    target, control = ph["target"], ph["control"]
    interval = float(ph["warmer_rate_min"]) * 60
    backend.enable_warmer(target, interval)
    try:
        backend.sleep(interval)  # let the rule fire once before measuring
        t0 = backend.now()
        end = t0 + float(ph["duration_h"]) * 3600
        block_s = float(ph["block_min"]) * 60
        while True:
            gap = rng.expovariate(1.0 / float(ph["mean_gap_s"]))
            if backend.now() + gap > end:
                break
            backend.sleep(gap)
            pair = [(target, "on"), (control, "off")]
            rng.shuffle(pair)  # neither arm is always first
            block = int((backend.now() - t0) // block_s)
            for fn, warming in pair:
                rec.invoke(fn, payload, role="measure", intended_cold=False, pattern="sparse",
                           warming=warming, block=block)
    finally:
        backend.disable_warmer(target)


def run_burst(backend, cfg, ph, rec, rng, payload):
    n = int(ph["concurrency"])
    for rep, (r, v, m) in randomised_blocks(phase_cells(ph), int(ph["reps"]), rng):
        fn = f"{r}-{v}"
        _make_cold(backend, cfg, fn, m)  # quiet state: no warm environment left
        for i, res in enumerate(backend.invoke_concurrent(fn, payload, n)):
            rec.add(res, fn, role="measure", intended_cold=True, pattern="burst", warming="off",
                    rep=rep, burst_id=f"{fn}-{rep}", burst_slot=i)


def run_idle_probe(backend, cfg, ph, rec, rng, payload):
    cells = [(r, v, m, g) for (r, v, m) in phase_cells(ph) for g in ph["gaps_min"]]
    for rep, (r, v, m, gap) in randomised_blocks(cells, int(ph["reps"]), rng):
        fn = f"{r}-{v}"
        _prepare(backend, fn, m)
        rec.invoke(fn, payload, role="prime", intended_cold=False, rep=rep, pattern="idle", warming="off")
        backend.sleep(float(gap) * 60)
        rec.invoke(fn, payload, role="measure", intended_cold=True, rep=rep, pattern="idle", warming="off",
                   idle_gap_min=gap, force_cold="idle")


RUNNERS = {"cold": run_cold, "warm": run_warm, "warming": run_warming, "burst": run_burst,
           "idle_probe": run_idle_probe}


def run_phase(backend, cfg: dict, name: str, out_root: str | Path, seed: int) -> dict:
    ph = cfg["phases"][name]
    out = Path(out_root) / name
    if (out / "invocations.jsonl").exists():
        raise FileExistsError(f"{out} already has data - use a new --out folder")
    rec = Recorder(out, backend, name)
    rng = random.Random(f"{seed}-{name}")
    info = {"phase": name, "kind": ph["kind"], "data_mode": backend.mode, "seed": seed,
            "phase_config": ph, "force_cold": cfg["force_cold"], "arch": cfg["arch"],
            "region": cfg["region"], "stack_name": cfg["stack_name"],
            "t_start": backend.now(), "t_start_utc": iso(backend.now()),
            "wall_start_utc": iso(time.time())}
    if backend.mode == "mock":
        info["label"] = "SYNTHETIC mock data - not measured"
    RUNNERS[ph["kind"]](backend, cfg, ph, rec, rng, load_payload(cfg))
    info.update(t_end=backend.now(), t_end_utc=iso(backend.now()), wall_end_utc=iso(time.time()),
                invocations=rec.rows, status="complete",
                mock_log_events=backend.export_logs(out / "logs"))
    (out / "run_info.json").write_text(json.dumps(info, indent=2) + "\n")
    return info
