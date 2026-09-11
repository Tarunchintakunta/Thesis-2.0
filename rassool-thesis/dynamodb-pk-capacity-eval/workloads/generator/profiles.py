"""Workload profiles W1-W4 and the open-loop operation plan for one batch.

Arrivals are open-loop at a fixed spacing of 1/rate inside each phase: the
generator does not wait for a reply before scheduling the next operation, so a
slow table shows up as latency (and as generator lag, which is recorded)
instead of silently lowering the offered load.
"""
from __future__ import annotations

import numpy as np

from .zipf import Zipf

# read share and (ops/s, seconds) phases of one cycle
PROFILES = {
    "W1": {"name": "read-heavy", "read_fraction": 0.95, "cycle": [(200, 90)], "cycles": 1},
    "W2": {"name": "write-heavy", "read_fraction": 0.30, "cycle": [(200, 90)], "cycles": 1},
    "W3": {"name": "mixed", "read_fraction": 0.50, "cycle": [(200, 90)], "cycles": 1},
    "W4": {"name": "burst", "read_fraction": 0.50, "cycle": [(200, 60), (1000, 30)], "cycles": 2},
}


def phases(profile: dict) -> list[tuple[float, float]]:
    return [p for _ in range(int(profile.get("cycles", 1))) for p in profile["cycle"]]


def send_times(profile: dict) -> np.ndarray:
    """Planned send offsets in seconds from the start of the batch."""
    out, t0 = [], 0.0
    for rate, secs in phases(profile):
        n = int(round(rate * secs))
        out.append(t0 + np.arange(n) / rate)
        t0 += secs
    return np.concatenate(out) if out else np.zeros(0)


def planned_ops(profile: dict) -> int:
    return int(sum(round(r * s) for r, s in phases(profile)))


def duration_s(profile: dict) -> float:
    return float(sum(s for _, s in phases(profile)))


def op_plan(profile: dict, zipf: Zipf, seed: int, scale: float = 1.0) -> dict:
    """Everything the driver needs, decided up front so a batch is reproducible.

    scale < 1 shrinks the rates (pilot / smoke runs) without changing the mix.
    """
    rng = np.random.default_rng(seed)
    prof = {**profile, "cycle": [(r * scale, s) for r, s in profile["cycle"]]}
    t = send_times(prof)
    n = len(t)
    idx, rank = zipf.sample(rng, n)
    is_read = rng.random(n) < profile["read_fraction"]
    shard_draw = rng.integers(0, 1 << 30, n)  # K3 write shard comes from this, mod N
    return {"t": t, "order": idx, "rank": rank, "read": is_read, "shard_draw": shard_draw}
