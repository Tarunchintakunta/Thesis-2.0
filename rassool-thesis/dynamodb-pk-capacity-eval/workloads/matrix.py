"""The run matrix: blocks x 24 cells (6 configurations x 4 workloads).

Every block holds each cell once, in a new random order (fixed seed), so time
of day and slow drift hit every configuration equally. A cell in block b is
replicate b of that configuration x workload.
"""
from __future__ import annotations

import hashlib
import random

from workloads.generator import keys
from workloads.generator.profiles import PROFILES

MODES = ("on_demand", "provisioned")
CONFIGS = [(k, m) for k in keys.DESIGNS for m in MODES]


def table_name(prefix: str, design: str, mode: str) -> str:
    return f"{prefix}-{design.lower()}-{'ondemand' if mode == 'on_demand' else 'provisioned'}"


def stable_seed(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)


def schedule(cfg: dict, blocks: int | None = None, workloads: list[str] | None = None) -> list[dict]:
    rng = random.Random(cfg["schedule"]["seed"])
    blocks = blocks if blocks is not None else cfg["schedule"]["blocks"]
    workloads = workloads or cfg["factors"]["workload"]
    out = []
    for b in range(blocks):
        cells = [(k, m, w) for (k, m) in CONFIGS for w in workloads]
        rng.shuffle(cells)
        for pos, (k, m, w) in enumerate(cells):
            bid = f"b{b:02d}-{k}-{m}-{w}"
            out.append({"block": b, "pos": pos, "key_design": k, "capacity_mode": m, "workload": w,
                        "configuration": f"{k}-{m}", "replicate": b, "batch_id": bid,
                        "table": table_name(cfg["table_prefix"], k, m), "seed": stable_seed(bid)})
    return out


def scaled_profile(workload: str, rate_scale: float = 1.0, time_scale: float = 1.0) -> dict:
    """Pilot / smoke version of a profile: fewer ops per second and / or shorter phases."""
    p = PROFILES[workload]
    return {**p, "cycle": [(r * rate_scale, s * time_scale) for r, s in p["cycle"]]}


def lambda_events(cell: dict, cfg: dict, mode: str, lambdas: int, profile: dict | None = None,
                  settle_seconds: float | None = None, extra: dict | None = None) -> list[dict]:
    """One event per load-generator Lambda; each takes 1/lambdas of the rate with its own seed."""
    base = {"mode": mode, "table": cell["table"], "key_design": cell["key_design"], "workload": cell["workload"],
            "zipf_s": cfg["zipf"]["s"], "orders": cfg["dataset"]["orders"], "perm_seed": cfg["zipf"]["perm_seed"],
            "k3_shards": cfg["k3_shards"], "item_size_kb": cfg["dataset"]["item_size_kb"],
            "threads": cfg["driver"]["threads_per_lambda"], "scale": 1.0 / lambdas}
    if profile is not None:
        base["profile"] = profile
    if settle_seconds is not None:
        base["seconds"] = settle_seconds
    events = []
    for i in range(lambdas):
        ev = {**base, "seed": cell["seed"] * 10 + i + (5 if mode == "settle" else 0),
              "batch_id": f"{cell['batch_id']}-l{i}"}
        ev.update(extra or {})
        events.append(ev)
    return events
