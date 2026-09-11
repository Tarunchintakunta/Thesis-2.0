"""Delivery schedule with a known ground truth - written to disk before anything is invoked.

A request with multiplicity N is delivered N times with the same request_id.
Deliveries 1..N-1 carry an injected timeout (after commit, or between the P3
writes in the sensitivity phase); delivery N completes normally. So a request
has exactly N-1 injected retries, and the order of requests is shuffled so the
paths and multiplicities are interleaved in time.
"""
from __future__ import annotations

import csv
import json
import random
import uuid
from pathlib import Path


def payload(rng: random.Random, kb: int = 1) -> dict:
    """Synthetic payment request; `note` pads the business item to just under kb KB."""
    p = {"account": f"ACC-{rng.randint(1, 5000):05d}", "amount_cents": rng.randint(100, 500_000),
         "currency": "EUR", "note": ""}
    p["note"] = "x" * max(0, kb * 1024 - 260)  # the other fields + attribute names take ~250 bytes
    return p


def _rid(rng: random.Random) -> str:
    return str(uuid.UUID(int=rng.getrandbits(128), version=4))


def build(cfg: dict, phase: str, n_per_cell: int | None = None, seed: int | None = None) -> list[dict]:
    rng = random.Random(f"{seed if seed is not None else cfg['campaign']['seed']}-{phase}")
    kb = cfg["payload_kb"]
    cells: list[tuple[str, int, str]] = []
    if phase == "pilot":
        n = n_per_cell or cfg["pilot"]["requests_per_path"]
        cells = [(p, cfg["pilot"]["multiplicity"], cfg["injection"]["primary"]) for p in cfg["paths"]]
    elif phase == "campaign":
        n = n_per_cell or cfg["campaign"]["provisional_requests_per_cell"]
        cells = [(p, m, cfg["injection"]["primary"]) for p in cfg["paths"] for m in cfg["multiplicities"]]
    elif phase == "sensitivity":
        n = n_per_cell or cfg["campaign"]["sensitivity_requests_per_cell"]
        cells = [("P3", m, cfg["injection"]["sensitivity"]) for m in cfg["multiplicities"] if m > 1]
    else:
        raise ValueError(f"unknown phase {phase}")
    reqs = []
    for path, mult, inject in cells:
        for _ in range(n):
            reqs.append({"request_id": _rid(rng), "phase": phase, "path": path, "multiplicity": mult,
                         "inject_mode": inject, "injected_retries": mult - 1, "payload": payload(rng, kb)})
    rng.shuffle(reqs)
    for i, r in enumerate(reqs):
        r["order"] = i
    return reqs


def deliveries(req: dict) -> list[dict]:
    n = req["multiplicity"]
    return [{"delivery": d, "inject": req["inject_mode"] if d < n else "none"} for d in range(1, n + 1)]


def write_schedule(reqs: list[dict], path: str | Path) -> Path:
    """The explicit injection schedule: one row per planned delivery."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["order", "request_id", "path", "multiplicity", "delivery", "inject"])
        for r in reqs:
            for d in deliveries(r):
                w.writerow([r["order"], r["request_id"], r["path"], r["multiplicity"], d["delivery"], d["inject"]])
    return path


def write_ground_truth(reqs: list[dict], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for r in reqs:
            row = {k: v for k, v in r.items() if k != "payload"}
            row["intended_deliveries"] = r["multiplicity"]
            fh.write(json.dumps(row) + "\n")
    return path
