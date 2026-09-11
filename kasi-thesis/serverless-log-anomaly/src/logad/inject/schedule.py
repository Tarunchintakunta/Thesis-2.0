"""Phase B injection schedule = the ground truth.

60 injections per category (240 in total by default), in blocks of 12 with 3
of each category per block in a random order. Blocks are the unit the paired
statistics use (F1 per block per detector). Every injection gets a recorded
[start, end) interval, so recall is computed, not estimated.
"""
from __future__ import annotations

import csv
import random
from dataclasses import asdict, dataclass
from pathlib import Path

from logad.inject.faults import CATEGORIES


@dataclass(frozen=True)
class Injection:
    injection_id: int
    block: int
    category: str
    start: float
    end: float


def build_schedule(t0: float, per_category: int, block_size: int, gap_s: tuple[float, float],
                   duration_s: tuple[float, float], rng: random.Random) -> list[Injection]:
    n_cat = len(CATEGORIES)
    if block_size % n_cat:
        raise ValueError("block_size must be a multiple of the number of categories")
    per_block = block_size // n_cat
    if per_category % per_block:
        raise ValueError("per_category must be a multiple of block_size / categories")
    n_blocks = per_category // per_block

    out: list[Injection] = []
    t = t0
    for block in range(n_blocks):
        cats = [c for c in CATEGORIES for _ in range(per_block)]
        rng.shuffle(cats)
        for cat in cats:
            t += rng.uniform(*gap_s)  # normal traffic before the fault
            length = rng.uniform(*duration_s)
            out.append(Injection(len(out), block, cat, t, t + length))
            t += length
    return out


def schedule_end(schedule: list[Injection], tail_s: float) -> float:
    return (schedule[-1].end if schedule else 0.0) + tail_s


def active_at(schedule: list[Injection], t: float) -> Injection | None:
    lo, hi = 0, len(schedule) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        inj = schedule[mid]
        if t < inj.start:
            hi = mid - 1
        elif t >= inj.end:
            lo = mid + 1
        else:
            return inj
    return None


def write_ground_truth(schedule: list[Injection], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["injection_id", "block", "category", "start", "end"])
        writer.writeheader()
        for inj in schedule:
            writer.writerow(asdict(inj))
    return path


def read_ground_truth(path: str | Path) -> list[Injection]:
    with open(path, encoding="utf-8") as fh:
        return [Injection(int(r["injection_id"]), int(r["block"]), r["category"], float(r["start"]), float(r["end"]))
                for r in csv.DictReader(fh)]
