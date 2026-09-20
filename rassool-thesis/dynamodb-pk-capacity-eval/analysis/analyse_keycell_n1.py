#!/usr/bin/env python
"""Stats on the existing W3/W4 live key-cells (no new AWS).

Batch-level two-way ANOVA is unidentified at n=1 per cell (interaction saturates
residual df). This script:

1. Attempts the pre-registered factorial on batches.csv and records identification.
2. Runs exploratory Kruskal-Wallis / KS on request-level latency in results/raw/
   (pseudo-replication; not confirmatory H_key). W1/W2 remain unfilled.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis import stats as S  # noqa: E402
from analysis.cost_model import add_costs, load_prices  # noqa: E402


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, list | tuple):
        return [_clean(v) for v in o]
    if isinstance(o, np.integer | np.bool_):
        return o.item()
    if isinstance(o, float | np.floating):
        return None if math.isnan(v := float(o)) else round(v, 6)
    return o


def batch_factorial(b: pd.DataFrame) -> dict:
    out = {}
    for w in ("W3", "W4"):
        d = b[b["workload"] == w]
        n_cfg = d["configuration"].nunique()
        n_rep = int(d.groupby("configuration").size().min()) if len(d) else 0
        identified = n_rep >= 2 and n_cfg >= 6
        entry = {"workload": w, "n_configs": int(n_cfg), "n_per_config": n_rep,
                 "identified_two_way_with_interaction": identified}
        if not identified:
            entry["note"] = (
                "n=1 per cell: two-way ANOVA with interaction has residual df=0; "
                "not computed as confirmatory"
            )
            # still record main-effect-only OLS if residual df>0 without interaction
            d2 = d.copy()
            if len(d2) >= 4:
                try:
                    import statsmodels.formula.api as smf
                    import statsmodels.api as sm
                    m = smf.ols("latency_mean_ms ~ C(key_design) + C(capacity_mode)", data=d2).fit()
                    tab = sm.stats.anova_lm(m, typ=2)
                    entry["additive_ols_exploratory"] = {
                        "method": "anova2_additive_n1_cells",
                        "residual_df": float(tab.loc["Residual", "df"]),
                        "terms": {
                            "key": {"F": float(tab.loc["C(key_design)", "F"]),
                                    "p": float(tab.loc["C(key_design)", "PR(>F)"])},
                            "capacity": {"F": float(tab.loc["C(capacity_mode)", "F"]),
                                         "p": float(tab.loc["C(capacity_mode)", "PR(>F)"])},
                        },
                        "confirmatory": False,
                    }
                except Exception as exc:  # noqa: BLE001
                    entry["additive_ols_error"] = str(exc)
        else:
            entry["factorial"] = S.factorial(d, "latency_mean_ms")
        out[w] = entry
    return out


def request_level(raw_dir: Path, batches: pd.DataFrame) -> list[dict]:
    rows = []
    if not raw_dir.is_dir():
        return [{"note": f"raw dir missing: {raw_dir}"}]
    for (w, cap), g in batches.groupby(["workload", "capacity_mode"]):
        groups, labels = [], []
        for k, kg in g.groupby("key_design"):
            lat = []
            for bid in kg["batch_id"]:
                p = raw_dir / f"{bid}.csv.gz"
                if not p.exists():
                    continue
                df = pd.read_csv(p)
                ok = df[df["ok"].astype(str).str.lower().isin(["true", "1"])]
                lat.append(ok["latency_ms"].to_numpy(float))
            if lat:
                groups.append(np.concatenate(lat))
                labels.append(k)
        if len(groups) < 2:
            continue
        h = st.kruskal(*groups)
        ks = []
        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                r = st.ks_2samp(groups[i], groups[j])
                ks.append({"a": labels[i], "b": labels[j], "statistic": float(r.statistic),
                           "p": float(r.pvalue)})
        rows.append({
            "stratum": f"{w}-{cap}",
            "workload": w,
            "capacity_mode": cap,
            "keys": labels,
            "n_requests": [int(len(x)) for x in groups],
            "median_latency_ms": [float(np.median(x)) for x in groups],
            "kruskal_h": float(h.statistic),
            "kruskal_p": float(h.pvalue),
            "ks_pairs": ks,
            "confirmatory": False,
            "note": "request-level; pseudo-replication vs batch ANOVA; exploratory only",
        })
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", default=str(ROOT / "results"))
    ap.add_argument("--out", default=str(ROOT / "report/generated"))
    args = ap.parse_args(argv)
    results, out = Path(args.results), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    b = add_costs(pd.read_csv(results / "batches.csv"), load_prices())
    b = b[b["data_source"] == "live"]
    factorial = batch_factorial(b)
    req = request_level(results / "raw", b)
    report = {
        "label": "live DynamoDB key-cells n=1 (W3/W4); exploratory request-level KW/KS",
        "data_source": "live",
        "batches": int(len(b)),
        "workloads_present": sorted(b["workload"].unique().tolist()),
        "workloads_missing": ["W1", "W2"],
        "confirmatory_batch_anova": False,
        "batch_factorial": factorial,
        "request_level_exploratory": req,
    }
    path = out / "hypotheses_keycell_n1.json"
    path.write_text(json.dumps(_clean(report), indent=2) + "\n")
    (results / "hypotheses_keycell_n1.json").write_text(path.read_text())
    lines = ["# Key-cell n=1 stats (not confirmatory ANOVA)", "",
             "W1/W2 **not measured**. Two-way ANOVA with interaction **not identified** (n=1).",
             "Request-level Kruskal-Wallis is exploratory (pseudo-replication).", ""]
    for r in req:
        if "kruskal_p" not in r:
            continue
        lines.append(f"- `{r['stratum']}` H={r['kruskal_h']:.3g} p={r['kruskal_p']:.3g} "
                     f"medians={dict(zip(r['keys'], r['median_latency_ms'], strict=True))}")
    (out / "hypotheses_keycell_n1.md").write_text("\n".join(lines) + "\n")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
