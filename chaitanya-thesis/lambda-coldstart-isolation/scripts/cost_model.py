#!/usr/bin/env python
"""Add per-invocation cost to the processed dataset.

    python scripts/cost_model.py --in data/processed/mock/metrics.csv --out data/processed/mock/costs.csv

cost = effective billed ms / 1000 x memory GB x arm64 price per GB-s + request charge
(configs/pricing.yaml, price date recorded in the output's header comment).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coldstart.config import ROOT, load_config  # noqa: E402
from coldstart.cost_model import effective_billed_ms, invocation_cost, load_prices  # noqa: E402


def add_costs(m: pd.DataFrame, prices: dict, arch: str) -> pd.DataFrame:
    m = m.copy()
    ok = m["billed_ms"].notna() & m["memory_mb"].notna()
    m["effective_billed_ms"] = [
        effective_billed_ms(b, d, i, prices["bill_init_phase"]) if good else float("nan")
        for b, d, i, good in zip(m["billed_ms"], m["duration_ms"], m["init_ms"], ok, strict=True)
    ]
    m["cost_usd"] = [
        invocation_cost(b, int(mem), arch, prices) if good else float("nan")
        for b, mem, good in zip(m["effective_billed_ms"], m["memory_mb"], ok, strict=True)
    ]
    return m


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prices", default=str(ROOT / "configs/pricing.yaml"))
    ap.add_argument("--config", default="configs/experiment.yaml")
    args = ap.parse_args(argv)
    cfg = load_config(args.config)
    prices = load_prices(args.prices)
    src = Path(args.inp)
    m = pd.read_parquet(src) if src.suffix == ".parquet" else pd.read_csv(src)
    m = add_costs(m, prices, cfg["arch"])
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    m.to_csv(out, index=False)
    by_phase = m.groupby("phase")["cost_usd"].agg(["count", "sum"])
    print(f"prices as of: {prices['as_of']}  arch={cfg['arch']}  bill_init_phase={prices['bill_init_phase']}")
    print(by_phase.to_string(float_format=lambda v: f"{v:.6f}"))
    label = "(SYNTHETIC mock - hypothetical)" if set(m["data_mode"].dropna()) == {"mock"} else ""
    print(f"total ${m['cost_usd'].sum():.4f} {label} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
