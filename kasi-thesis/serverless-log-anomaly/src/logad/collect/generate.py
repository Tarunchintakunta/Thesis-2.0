"""Generate phases A, B and C for one seed with the local runtime emulator.

    python -m logad.collect.generate --config configs/experiment.yaml --seed 2025

Writes to data/raw/seed_<seed>/:
  phase_A.log / phase_B.log / phase_C.log   "<ISO time>\\t<message>" per line, as CloudWatch holds them
  metrics_<phase>.csv                        one row per request (what CloudWatch metrics are built from)
  bursts_<phase>.csv                         scale-up bursts (to tag elasticity false alarms)
  ground_truth.csv                           phase B injections = the labels
  meta.json                                  phase boundaries, counts, config hash

Phase A has no injections at all; that is checked again later by the clean
window certification (Albert, 2024: contamination ruins source-free training).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import random
from pathlib import Path

from logad.collect.runtime import LambdaEmulator, iso
from logad.collect.workload import Burst, arrivals, make_event, pick_route, regular_bursts
from logad.config import PROJECT_ROOT, dict_hash, load_experiment
from logad.inject.schedule import active_at, build_schedule, schedule_end, write_ground_truth

METRIC_FIELDS = ["t", "route", "throttled", "status", "error", "duration_ms", "cold", "timeout", "killed"]


def parse_start(value: str) -> float:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def _run(em: LambdaEmulator, t0: float, t1: float, cfg: dict, bursts: list[Burst], rng: random.Random,
         order_ids: list[str], schedule=None) -> tuple[list, list]:
    em.lines = []
    em.metrics = []
    wl = cfg["workload"]
    for t in arrivals(t0, t1, wl["base_rate"], wl["diurnal_amplitude"], bursts, rng):
        inj = active_at(schedule, t) if schedule else None
        em.set_fault(inj.category if inj else None)
        em.invoke(t, make_event(pick_route(wl["route_mix"], rng), rng, order_ids))
    em.set_fault(None)
    return em.sorted_lines(), em.metrics


def _write_log(lines, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for t, message in lines:
            fh.write(f"{iso(t)}\t{message}\n")


def _write_csv(rows, fields, path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def generate(cfg: dict, seed: int, out_root: Path) -> dict:
    out = out_root / f"seed_{seed}"
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    t0 = parse_start(cfg["start_utc"])
    em = LambdaEmulator(cfg["runtime"], cfg["db"], cfg["faults"], random.Random(seed + 1), start=t0)
    order_ids: list[str] = []
    phases = cfg["phases"]
    meta = {"seed": seed, "config": cfg.get("name", "?"), "config_hash": dict_hash(cfg), "phases": {}}

    # phase A - clean
    a0, a1 = t0, t0 + phases["A"]["hours"] * 3600
    b = phases["A"]["bursts"]
    bursts_a = regular_bursts(a0, a1, b["every_s"], b["len_s"], b["factor"], rng)
    lines, metrics = _run(em, a0, a1, cfg, bursts_a, rng, order_ids)
    _write_log(lines, out / "phase_A.log")
    _write_csv(metrics, METRIC_FIELDS, out / "metrics_A.csv")
    _write_csv([vars(x) for x in bursts_a], ["start", "length", "factor"], out / "bursts_A.csv")
    meta["phases"]["A"] = {"start": a0, "end": a1, "lines": len(lines), "requests": len(metrics)}

    # phase B - injections
    pb = phases["B"]
    schedule = build_schedule(a1, pb["injections_per_category"], pb["block_size"], tuple(pb["gap_s"]),
                              tuple(pb["duration_s"]), rng)
    b0, b1 = a1, schedule_end(schedule, pb["tail_s"])
    b = pb["bursts"]
    bursts_b = regular_bursts(b0, b1, b["every_s"], b["len_s"], b["factor"], rng)
    lines, metrics = _run(em, b0, b1, cfg, bursts_b, rng, order_ids, schedule)
    _write_log(lines, out / "phase_B.log")
    _write_csv(metrics, METRIC_FIELDS, out / "metrics_B.csv")
    _write_csv([vars(x) for x in bursts_b], ["start", "length", "factor"], out / "bursts_B.csv")
    write_ground_truth(schedule, out / "ground_truth.csv")
    meta["phases"]["B"] = {"start": b0, "end": b1, "lines": len(lines), "requests": len(metrics),
                           "injections": len(schedule)}

    # phase C - elasticity control, no faults
    c0, c1 = b1, b1 + phases["C"]["hours"] * 3600
    b = phases["C"]["bursts"]
    bursts_c = regular_bursts(c0, c1, b["every_s"], b["len_s"], b["factor"], rng)
    lines, metrics = _run(em, c0, c1, cfg, bursts_c, rng, order_ids)
    _write_log(lines, out / "phase_C.log")
    _write_csv(metrics, METRIC_FIELDS, out / "metrics_C.csv")
    _write_csv([vars(x) for x in bursts_c], ["start", "length", "factor"], out / "bursts_C.csv")
    meta["phases"]["C"] = {"start": c0, "end": c1, "lines": len(lines), "requests": len(metrics)}

    (out / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="generate phase A/B/C logs with the Lambda emulator")
    p.add_argument("--config", default=str(PROJECT_ROOT / "configs" / "experiment.yaml"))
    p.add_argument("--seed", type=int, action="append", help="default: all seeds in the config")
    p.add_argument("--out", default=str(PROJECT_ROOT / "data" / "raw"))
    args = p.parse_args(argv)
    cfg = load_experiment(args.config)
    for seed in args.seed or cfg["seeds"]:
        meta = generate(cfg, seed, Path(args.out))
        counts = {k: v["lines"] for k, v in meta["phases"].items()}
        print(f"seed {seed}: lines {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
