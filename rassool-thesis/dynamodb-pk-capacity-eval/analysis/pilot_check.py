#!/usr/bin/env python
"""Pilot checks (ANALYSIS_PLAN.md, "Pilot"): settling, power, skew.

    python analysis/pilot_check.py --results results_pilot/

1. settling - mean latency of the first vs the last third of every batch; if more
   than 10% of batches drift by more than 10%, lengthen settling_seconds (amendment)
2. power - with the pilot's spread, the power of the two-way model's terms for
   f = 0.25 and n = 30 per cell (noncentral F)
3. skew - hot_rank_share should be about 0.90 in every batch
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.batch_metrics import read_raw  # noqa: E402


def drift(raw: pd.DataFrame) -> float:
    ok = raw[raw["ok"] == 1].sort_values("t_start_s")
    n = len(ok)
    if n < 30:
        return float("nan")
    first = ok["latency_ms"].iloc[: n // 3].mean()
    last = ok["latency_ms"].iloc[-(n // 3):].mean()
    return float(abs(last - first) / first) if first > 0 else float("nan")


def anova_power(f: float, n_per_cell: int, cells: int = 6, df1: int = 2, alpha: float = 0.05) -> float:
    """Power of one term (numerator df1) of a two-way model with `cells` cells."""
    n = n_per_cell * cells
    df2 = n - cells
    crit = st.f.ppf(1 - alpha, df1, df2)
    return float(1 - st.ncf.cdf(crit, df1, df2, f * f * n))


def check(results: Path) -> dict:
    b = pd.read_csv(results / "batches.csv")
    drifts = {}
    for bid in b["batch_id"]:
        p = results / "raw" / f"{bid}.csv.gz"
        if p.exists():
            drifts[bid] = drift(read_raw(str(p)))
    d = pd.Series(drifts, dtype=float).dropna()
    share_drifting = float((d > 0.10).mean()) if len(d) else float("nan")
    return {
        "batches": int(len(b)),
        "settling": {"median_drift": float(d.median()) if len(d) else None, "share_over_10pct": share_drifting,
                     "lengthen_settling": bool(share_drifting > 0.10) if len(d) else None},
        "power_f025_n30": {"key (df 2)": anova_power(0.25, 30, df1=2), "capacity (df 1)": anova_power(0.25, 30, df1=1),
                           "interaction (df 2)": anova_power(0.25, 30, df1=2)},
        "hot_rank_share": {"min": float(b["hot_rank_share"].min()), "mean": float(b["hot_rank_share"].mean())},
        "latency_sd_by_cell": b.groupby(["workload", "configuration"])["latency_mean_ms"].std().round(4).to_dict(),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default="results_pilot")
    args = ap.parse_args(argv)
    res = check(Path(args.results))
    res["latency_sd_by_cell"] = {f"{w}/{c}": v for (w, c), v in res["latency_sd_by_cell"].items()}
    (Path(args.results) / "pilot_check.json").write_text(json.dumps(res, indent=2, default=float) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "latency_sd_by_cell"}, indent=2, default=float))
    return 0


if __name__ == "__main__":
    np.seterr(all="ignore")
    raise SystemExit(main())
