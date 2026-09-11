"""Everything after the pipeline: metrics, H1-H3, decision rule, tables, figures.

    python -m logad.eval.report --results results

Reads only results/metrics/windows_{B,C}_seed_*.csv (written by the pipeline)
and writes:
  results/metrics/summary.csv, d1.csv, d2.csv, d3.csv
  results/metrics/injections.csv
  results/stats/hypotheses.json
  results/tables/summary.md, per_category.md, hypotheses.md
  results/figures/*.png
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from logad.config import PROJECT_ROOT
from logad.eval import plots
from logad.eval.metrics import block_scores, far_blocks, false_alarm_rate, injection_table, per_category, prf
from logad.eval.stats import bootstrap_ci, friedman, holm, mcnemar, paired_power_n, paired_test
from logad.inject.faults import CATEGORIES
from logad.inject.schedule import Injection

DETECTORS = {
    "d1_primary": "D1 source-free (primary)",
    "d1_ocsvm": "D1a OC-SVM",
    "d1_iforest": "D1b Isolation Forest",
    "d2_transfer": "D2 transfer (ELFA-Log style)",
    "d3_thresholds": "D3 threshold alarms",
}
MAIN = ["d1_primary", "d2_transfer", "d3_thresholds"]
PRACTICAL_F1 = 0.10  # pre-registered: 10 F1 points


def load_windows(results: Path, phase: str) -> pd.DataFrame:
    files = sorted((results / "metrics").glob(f"windows_{phase}_seed_*.csv"))
    if not files:
        raise FileNotFoundError(f"no windows_{phase}_seed_*.csv under {results / 'metrics'} - run the pipeline first")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df["category"] = df["category"].fillna("")
    return df


def schedule_from_windows(df: pd.DataFrame, window_s: float = 60.0) -> dict[int, list[Injection]]:
    """Rebuild per-seed injection intervals from the labelled windows (window resolution)."""
    out = {}
    for seed, g in df[df["injection_id"] >= 0].groupby("seed"):
        injs = []
        for iid, gg in g.groupby("injection_id"):
            injs.append(Injection(int(iid), int(gg["block"].iloc[0]), str(gg["category"].iloc[0]),
                                  float(gg["start"].min()), float(gg["start"].max() + window_s)))
        out[seed] = sorted(injs, key=lambda i: i.start)
    return out


def pooled_f1_ci(B: pd.DataFrame, det: str, n: int = 2000, seed: int = 1) -> tuple[float, float]:
    """95 % CI of the pooled F1 by resampling (seed, block) groups."""
    g = B.groupby(["seed", "block"])
    pred, lab = B[f"pred_{det}"].astype(bool), B["label"].astype(bool)
    tp = (pred & lab).groupby([B["seed"], B["block"]]).sum().to_numpy()
    fp = (pred & ~lab).groupby([B["seed"], B["block"]]).sum().to_numpy()
    fn = (~pred & lab).groupby([B["seed"], B["block"]]).sum().to_numpy()
    rng = np.random.default_rng(seed)
    k = len(g)
    f1s = []
    for _ in range(n):
        idx = rng.integers(0, k, k)
        t, f, m = tp[idx].sum(), fp[idx].sum(), fn[idx].sum()
        f1s.append(2 * t / (2 * t + f + m) if t else 0.0)
    lo, hi = np.percentile(f1s, [2.5, 97.5])
    return float(lo), float(hi)


def summary_rows(B: pd.DataFrame, C: pd.DataFrame, inj: pd.DataFrame) -> pd.DataFrame:
    rows = []
    normal_B = ~B["label"].astype(bool)
    for det, label in DETECTORS.items():
        r = prf(B[f"pred_{det}"], B["label"])
        lo, hi = pooled_f1_ci(B, det)
        d = inj[inj["detector"] == det]
        predC = C[f"pred_{det}"].astype(bool)
        rows.append({
            "detector": det, "label": label,
            "precision": r["precision"], "recall": r["recall"], "f1": r["f1"], "f1_ci_low": lo, "f1_ci_high": hi,
            "tp": r["tp"], "fp": r["fp"], "fn": r["fn"],
            "far_B_normal": false_alarm_rate(B.loc[normal_B, f"pred_{det}"]),
            "far_C_elasticity": false_alarm_rate(predC),
            "far_C_burst": false_alarm_rate(predC[C["burst"].astype(bool)]),
            "far_C_no_burst": false_alarm_rate(predC[~C["burst"].astype(bool)]),
            "fp_C_with_cold_start": int((predC & (C["cold_starts"] > 0)).sum()),
            "fp_C_in_burst": int((predC & C["burst"].astype(bool)).sum()),
            "injections_detected": float(d["detected"].mean()) if len(d) else math.nan,
            "median_delay_s": float(d["delay_s"].median()) if d["detected"].any() else math.nan,
        })
    return pd.DataFrame(rows)


def per_category_rows(B: pd.DataFrame, inj: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for det in DETECTORS:
        cats = per_category(B[f"pred_{det}"], B["label"], B["category"])
        for cat in CATEGORIES:
            d = inj[(inj["detector"] == det) & (inj["category"] == cat)]
            res = cats.get(cat, {"f1": math.nan, "recall": math.nan, "precision": math.nan})
            rows.append({"detector": det, "category": cat, "f1": res["f1"], "recall": res["recall"],
                         "precision": res["precision"],
                         "injections_detected": float(d["detected"].mean()) if len(d) else math.nan,
                         "median_delay_s": float(d["delay_s"].median()) if d["detected"].any() else math.nan})
    return pd.DataFrame(rows)


def injection_rows(B: pd.DataFrame) -> pd.DataFrame:
    schedules = schedule_from_windows(B)
    frames = []
    for seed, sched in schedules.items():
        g = B[B["seed"] == seed].sort_values("window")
        for det in DETECTORS:
            t = injection_table(g[f"pred_{det}"].to_numpy(), g["start"].to_numpy(), 60.0, sched)
            t["seed"], t["detector"] = seed, det
            frames.append(t)
    return pd.concat(frames, ignore_index=True)


def hypothesis_tests(B: pd.DataFrame, C: pd.DataFrame, inj: pd.DataFrame, alpha: float = 0.05) -> dict:
    blocks = {det: block_scores(B, f"pred_{det}") for det in MAIN}
    tests: dict[str, dict] = {}

    # H1 - F1 source-free vs transfer, paired by block
    h1 = paired_test(blocks["d1_primary"]["f1"], blocks["d2_transfer"]["f1"], alpha)
    tests["H1"] = {"null": "F1(source-free) = F1(transfer)", "unit": "block (seed x 12 injections)", **h1}

    # H2 - per approach, F1 across the four fault categories (paired by block)
    for det in MAIN:
        cols = [f"f1_{c}" for c in CATEGORIES]
        res = friedman(blocks[det][cols].to_numpy())
        tests[f"H2_{det}"] = {"null": f"F1 does not differ across fault categories for {DETECTORS[det]}",
                             "unit": "block", "categories": list(CATEGORIES), **res}

    # H3 - elasticity false-alarm rate across approaches (phase C, 30 min blocks)
    far = {det: far_blocks(C, f"pred_{det}") for det in MAIN}
    mat = np.column_stack([far[det]["far"].to_numpy() for det in MAIN])
    tests["H3"] = {"null": "elasticity false-alarm rate does not differ between approaches",
                   "unit": "30 min block of phase C", "detectors": MAIN, **friedman(mat)}
    pairwise = {}
    for i, a in enumerate(MAIN):
        for b in MAIN[i + 1:]:
            pairwise[f"{a}_vs_{b}"] = paired_test(far[a]["far"], far[b]["far"], alpha)
    tests["H3"]["pairwise_post_hoc"] = pairwise

    adjusted = holm({k: v["p"] for k, v in tests.items()})
    for name, res in tests.items():
        res["p_holm"] = adjusted[name]
        res["reject_null"] = bool(adjusted[name] < alpha)

    # decision rule (pre-registered)
    f1 = {det: prf(B[f"pred_{det}"], B["label"])["f1"] for det in MAIN}
    gap = f1["d2_transfer"] - f1["d1_primary"]
    decision = {
        "f1_source_free": f1["d1_primary"], "f1_transfer": f1["d2_transfer"], "f1_thresholds": f1["d3_thresholds"],
        "gap_transfer_minus_source_free": gap,
        "within_10_points_of_transfer": bool(gap <= PRACTICAL_F1),
        "beats_threshold_alarms": bool(f1["d1_primary"] > f1["d3_thresholds"]),
    }
    decision["viable_substitute"] = decision["within_10_points_of_transfer"] and decision["beats_threshold_alarms"]

    # secondary: injection level McNemar per category
    mcn = {}
    for cat in CATEGORIES:
        for a, b in (("d1_primary", "d2_transfer"), ("d1_primary", "d3_thresholds"), ("d2_transfer", "d3_thresholds")):
            da = inj[(inj["detector"] == a) & (inj["category"] == cat)].sort_values(["seed", "injection_id"])
            db = inj[(inj["detector"] == b) & (inj["category"] == cat)].sort_values(["seed", "injection_id"])
            mcn[f"{cat}:{a}_vs_{b}"] = mcnemar(da["detected"].to_numpy(), db["detected"].to_numpy())

    diffs = blocks["d1_primary"]["f1"].to_numpy() - blocks["d2_transfer"]["f1"].to_numpy()
    power = {"blocks": int(len(diffs)), "sd_block_f1_difference": float(np.std(diffs, ddof=1)) if len(diffs) > 1 else 0.0,
             "pairs_needed_for_10_points": paired_power_n(float(np.std(diffs, ddof=1)) if len(diffs) > 1 else 0.0,
                                                          PRACTICAL_F1, alpha)}
    return {"alpha": alpha, "family": list(tests), "tests": tests, "decision_rule": decision,
            "secondary_mcnemar": mcn, "power_check": power,
            "block_f1_means": {det: float(b["f1"].mean()) for det, b in blocks.items()},
            "block_f1_ci95": {det: list(bootstrap_ci(b["f1"])) for det, b in blocks.items()}}


def _fmt(x, nd=3) -> str:
    if isinstance(x, (float, np.floating)):
        return "nan" if math.isnan(x) else f"{x:.{nd}f}"
    return str(x)


def to_markdown(df: pd.DataFrame, cols: list[str]) -> str:
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(_fmt(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def hypotheses_markdown(h: dict) -> str:
    lines = ["| test | null hypothesis | test used | statistic | p | p (Holm) | effect | size | reject H0 |",
             "|---|---|---|---|---|---|---|---|---|"]
    for name, r in h["tests"].items():
        lines.append(f"| {name} | {r['null']} | {r['test']} | {_fmt(r['statistic'])} | {_fmt(r['p'], 4)} | "
                     f"{_fmt(r['p_holm'], 4)} | {r['effect']} | {_fmt(r['effect_size'])} | {r['reject_null']} |")
    d = h["decision_rule"]
    lines += ["", "**Decision rule** (source-free is a viable substitute if within 10 F1 points of transfer "
                  "AND better than the threshold alarms):", "",
              f"* F1 source-free = {d['f1_source_free']:.3f}, transfer = {d['f1_transfer']:.3f}, "
              f"thresholds = {d['f1_thresholds']:.3f}",
              f"* gap (transfer - source-free) = {d['gap_transfer_minus_source_free']:+.3f}",
              f"* within 10 points: {d['within_10_points_of_transfer']}; beats alarms: {d['beats_threshold_alarms']}",
              f"* **viable substitute: {d['viable_substitute']}**"]
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="metrics, statistics and figures from the window CSVs")
    p.add_argument("--results", default=str(PROJECT_ROOT / "results"))
    p.add_argument("--alpha", type=float, default=0.05)
    args = p.parse_args(argv)
    res = Path(args.results)
    B, C = load_windows(res, "B"), load_windows(res, "C")

    inj = injection_rows(B)
    inj.to_csv(res / "metrics" / "injections.csv", index=False)
    summary = summary_rows(B, C, inj)
    summary.to_csv(res / "metrics" / "summary.csv", index=False)
    for prefix, dets in (("d1", ["d1_primary", "d1_ocsvm", "d1_iforest"]), ("d2", ["d2_transfer"]), ("d3", ["d3_thresholds"])):
        rows = []
        for seed, g in B.groupby("seed"):
            gc = C[C["seed"] == seed]
            for det in dets:
                rows.append({"seed": seed, "detector": det, **prf(g[f"pred_{det}"], g["label"]),
                             "far_C_elasticity": false_alarm_rate(gc[f"pred_{det}"])})
        pd.DataFrame(rows).to_csv(res / "metrics" / f"{prefix}.csv", index=False)
    cats = per_category_rows(B, inj)
    h = hypothesis_tests(B, C, inj, args.alpha)
    (res / "stats" / "hypotheses.json").write_text(json.dumps(h, indent=2, default=float) + "\n")

    note = "_Logs from the local Lambda runtime emulator (simulated serverless workload), not live AWS._\n\n"
    (res / "tables" / "summary.md").write_text(
        "# Detector summary (phase B evaluation, phase C elasticity)\n\n" + note
        + to_markdown(summary, ["label", "precision", "recall", "f1", "f1_ci_low", "f1_ci_high", "far_B_normal",
                                "far_C_elasticity", "far_C_burst", "far_C_no_burst", "injections_detected",
                                "median_delay_s"]) + "\n")
    (res / "tables" / "per_category.md").write_text(
        "# Per fault category\n\n" + note
        + to_markdown(cats, ["detector", "category", "f1", "recall", "injections_detected", "median_delay_s"]) + "\n")
    (res / "tables" / "hypotheses.md").write_text("# Hypothesis tests (Holm-Bonferroni, alpha 0.05)\n\n" + note
                                                  + hypotheses_markdown(h) + "\n")
    plots.make_all(B, C, summary, cats, inj, res / "figures")
    print(hypotheses_markdown(h))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
