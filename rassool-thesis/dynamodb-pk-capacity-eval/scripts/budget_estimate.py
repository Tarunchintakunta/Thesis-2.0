#!/usr/bin/env python
"""Whole-campaign budget estimate (arithmetic from list prices, before any run).

    python scripts/budget_estimate.py

Adds up what the cost-per-10k figure deliberately leaves out, so the student
knows the real bill: provisioned tables are charged every hour they exist, the
1M-item seed, storage and the driver Lambda.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.cost_model import load_prices  # noqa: E402
from analysis.design_checks import capacity_plan  # noqa: E402
from scripts.run_matrix import estimate  # noqa: E402
from workloads.generator.profiles import PROFILES, duration_s  # noqa: E402
from workloads.matrix import schedule  # noqa: E402

OVERHEAD = 1.25        # warm-ups, S3 downloads, pauses: wall time vs pure load time
SEED_HOURS_PER_TABLE = 1.0


def budget(cfg: dict) -> list[tuple[str, float, str]]:
    prices = load_prices()
    extra = yaml.safe_load(open(ROOT / "config/budget_prices.yaml"))
    cells = schedule(cfg)
    est = estimate(cfg, cells, prices, 1.0, 1.0)
    cap = capacity_plan(cfg).set_index("key_design")
    wall_h = est["hours_of_load"] * OVERHEAD + 3 * SEED_HOURS_PER_TABLE
    prov_hourly = sum(r.read_min * prices["provisioned"]["rcu_hour"] + r.write_min * prices["provisioned"]["wcu_hour"]
                      for r in cap.itertuples())
    orders, kb = cfg["dataset"]["orders"], cfg["dataset"]["item_size_kb"]
    seed_od = 3 * orders * kb * prices["on_demand"]["write_request_unit"]
    seed_prov = 3 * SEED_HOURS_PER_TABLE * cfg_seed_wcu() * prices["provisioned"]["wcu_hour"]
    gb = 6 * orders * kb * 1024 / 1e9 * 1.05  # + a little index overhead
    storage = gb * extra["dynamodb_storage_gb_month"] * (wall_h / 730 + 0.1)
    lam_s = sum((duration_s(PROFILES[c["workload"]]) + cfg["settling_seconds"] + 5) for c in cells) * cfg["driver"]["lambdas_per_batch"]
    lam = lam_s * cfg["driver"]["memory_mb"] / 1024 * extra["lambda_arm_gb_second"] + \
        len(cells) * cfg["driver"]["lambdas_per_batch"] * (2 + cfg["warmup_invocations"]) * extra["lambda_request"]
    return [
        ("request path during batches + settling (the cost-per-10k basis)", est["request_path_usd"], f"{len(cells)} batches"),
        ("provisioned tables between batches (charged every hour they exist)", prov_hourly * wall_h,
         f"{prov_hourly:.3f} $/h x {wall_h:.0f} h"),
        ("seeding 1M items x 3 on-demand tables", seed_od, "WRU"),
        ("seeding the 3 provisioned tables at the seed write floor", seed_prov, f"{SEED_HOURS_PER_TABLE:g} h each"),
        ("storage (6 tables, ~1 GB each)", storage, f"{gb:.1f} GB"),
        ("driver Lambda (arm64)", lam, f"{lam_s / 3600:.0f} Lambda-hours"),
    ]


def cfg_seed_wcu() -> int:
    tf = (ROOT / "iac/variables.tf").read_text()
    block = tf.split('variable "seed_write_capacity"')[1]
    return int(block.split("default =")[1].split()[0])


def main() -> int:
    with open(ROOT / "config/experiment.yaml") as fh:
        cfg = yaml.safe_load(fh)
    rows = budget(cfg)
    print("| item | USD | basis |\n|---|---|---|")
    for name, usd, basis in rows:
        print(f"| {name} | {usd:.2f} | {basis} |")
    print(f"| **total (list prices, free tier ignored)** | **{sum(r[1] for r in rows):.2f}** | |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
