#!/usr/bin/env python
"""Budget gate: estimate the campaign before running it, and show what was spent.

    python scripts/budget_guard.py --plan configs/experiment.yaml
    python scripts/budget_guard.py --log data/spend_log.csv

The invokers call the same guard (src/coldstart/budget.py) before every
invocation and stop at the daily cap; this script is the up-front check.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coldstart.config import ROOT, load_config, phase_cells  # noqa: E402
from coldstart.cost_model import invocation_cost, load_prices  # noqa: E402

TYPICAL_COLD_MS = 1500   # pessimistic cold call: init + first invoke (Java default at low memory is the slow one)
TYPICAL_WARM_MS = 200


def estimate(cfg: dict, prices: dict) -> pd.DataFrame:
    rows = []
    arch = cfg["arch"]
    for name, ph in cfg["phases"].items():
        kind = ph["kind"]
        if kind == "warming":
            calls = 2 * ph["duration_h"] * 3600 / ph["mean_gap_s"]
            pings = ph["duration_h"] * 60 / ph["warmer_rate_min"]
            mem = [1024]
            cold_calls, warm_calls = calls * 0.5, calls * 0.5 + pings
        else:
            cells = phase_cells(ph)
            mem = [m for _, _, m in cells]
            reps = ph["reps"]
            if kind == "cold":
                cold_calls = len(cells) * reps
                warm_calls = cold_calls * ph.get("follow_up_warm", 0)
            elif kind == "warm":
                cold_calls = len(cells) * reps
                warm_calls = len(cells) * reps * (ph.get("warmup_per_block", 2) + ph.get("measured_per_block", 1) - 1)
            elif kind == "burst":
                cold_calls, warm_calls = len(cells) * reps * ph["concurrency"], 0
            else:  # idle_probe
                cold_calls = warm_calls = len(cells) * len(ph["gaps_min"]) * reps
        m = max(mem)
        typical = cold_calls * invocation_cost(TYPICAL_COLD_MS, m, arch, prices) + \
            warm_calls * invocation_cost(TYPICAL_WARM_MS, m, arch, prices)
        worst = (cold_calls + warm_calls) * invocation_cost(30_000, m, arch, prices)
        rows.append({"phase": name, "calls": int(cold_calls + warm_calls),
                     "typical_usd": typical, "worst_case_usd": worst})
    return pd.DataFrame(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan")
    ap.add_argument("--log")
    ap.add_argument("--prices", default=str(ROOT / "configs/pricing.yaml"))
    args = ap.parse_args(argv)
    if not args.plan and not args.log:
        ap.error("give --plan and/or --log")
    prices = load_prices(args.prices)
    if args.plan:
        cfg = load_config(args.plan)
        est = estimate(cfg, prices)
        print(est.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
        print(f"total calls {est['calls'].sum():,}  typical ${est['typical_usd'].sum():.3f}  "
              f"worst case (every call hits the 30 s timeout at the phase's largest memory) "
              f"${est['worst_case_usd'].sum():.2f}")
        print(f"daily cap in the config: ${cfg['budget']['daily_usd']:.2f} (free tier ignored)")
    if args.log:
        log = Path(args.log)
        if not log.exists():
            print(f"{log}: no spend recorded yet")
        else:
            s = pd.read_csv(log)
            print(s.groupby(["utc_day", "mode"])["usd"].agg(["count", "sum"]).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
