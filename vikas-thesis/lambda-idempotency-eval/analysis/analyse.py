"""Campaign analysis: duplicate mutation, latency and capacity with 95 % CIs,
Holm-corrected tests, the pre-registered expectations E1-E3 and the
correctness-cost surface.

    python analysis/analyse.py --campaign data/runs/live/campaign \
        --sensitivity data/runs/live/sensitivity --out results/live --figures figures/live

Everything written carries the run source (live / moto / local); only `live`
results are AWS measurements.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402
from scipy import stats as st  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis import metrics, stats  # noqa: E402
from analysis.tables import SIGN, md_table, short_label, source_label  # noqa: E402

PATHS = ["P1", "P2", "P3"]
COLORS = {"P1": "#c0392b", "P2": "#2874a6", "P3": "#239b56"}
PAIRS = [("P1", "P2"), ("P1", "P3"), ("P2", "P3")]


# ---------- tests ----------

def dup_tests(cells: pd.DataFrame, alpha: float) -> pd.DataFrame:
    """H1 (directional): guarded paths have a lower duplicate rate than P1. P2 vs P3 is exploratory."""
    c = cells.set_index(["path", "multiplicity"])
    rows = []
    for m in sorted(cells.loc[cells["injected_retries"] > 0, "multiplicity"].unique()):
        for a, b, alt in (("P1", "P2", "greater"), ("P1", "P3", "greater"), ("P2", "P3", "two-sided")):
            if (a, m) not in c.index or (b, m) not in c.index:
                continue
            x, y = c.loc[(a, m)], c.loc[(b, m)]
            k1, n1, k2, n2 = (int(x["dup_mutations"]), int(x["injected_retries"]), int(y["dup_mutations"]),
                              int(y["injected_retries"]))
            z, p = stats.two_prop_z(k1, n1, k2, n2, alt)
            d, lo, hi = stats.newcombe_diff(k1, n1, k2, n2, alpha)
            rows.append({"multiplicity": int(m), "comparison": f"{a} vs {b}",
                         "alternative": "one-sided (P1 higher)" if alt == "greater" else "two-sided (exploratory)",
                         "rate_a": k1 / n1, "rate_b": k2 / n2, "diff": d, "ci_lo": lo, "ci_hi": hi, "z": z, "p": p})
    df = pd.DataFrame(rows)
    if len(df):
        df["p_holm"] = stats.holm(df["p"])
        df["reject_h0"] = df["p_holm"] < alpha
    return df


def chi2_tests(cells: pd.DataFrame) -> pd.DataFrame:
    sub = cells[cells["injected_retries"] > 0]
    tables = [("path x multiplicity", sub)] + [(f"paths at multiplicity {m}", s) for m, s in sub.groupby("multiplicity")]
    rows = []
    for name, s in tables:
        t = [[r.dup_mutations, r.injected_retries - r.dup_mutations] for r in s.itertuples()]
        rows.append({"table": name, "cells": len(s), **stats.chi2_table(t)})
    return pd.DataFrame(rows)


def cont_tests(req: pd.DataFrame, metric: str, alpha: float, B: int, seed: int) -> pd.DataFrame:
    """H1 (two-sided): the paths differ. Welch t or Mann-Whitney U, chosen by Shapiro-Wilk."""
    rows = []
    for m in sorted(req["multiplicity"].unique()):
        for a, b in PAIRS:
            x = req.loc[(req["path"] == a) & (req["multiplicity"] == m), metric].dropna()
            y = req.loc[(req["path"] == b) & (req["multiplicity"] == m), metric].dropna()
            if len(x) < 2 or len(y) < 2:
                continue
            rows.append({"metric": metric, "multiplicity": int(m), "comparison": f"{a} vs {b}",
                         **stats.compare(x, y, alpha=alpha, B=B, seed=seed)})
    df = pd.DataFrame(rows)
    if len(df):
        df["p_holm"] = stats.holm(df["p"])
        df["reject_h0"] = df["p_holm"] < alpha
    return df


def _decide(ok: bool, point_ok: bool) -> str:
    return "supported" if ok else ("inconclusive (point estimate meets it, CI does not)" if point_ok else "not supported")


def expectations(cells: pd.DataFrame, cap: pd.DataFrame, alpha: float) -> pd.DataFrame:
    c = cells.set_index(["path", "multiplicity"])
    rows = []
    retried = sorted(cells.loc[cells["injected_retries"] > 0, "multiplicity"].unique())
    for m in retried:  # E1: P1 duplicates on a majority of injected retries
        if ("P1", m) not in c.index:
            continue
        r = c.loc[("P1", m)]
        bt = st.binomtest(int(r["dup_mutations"]), int(r["injected_retries"]), 0.5, alternative="greater")
        ok = r["dup_ci_lo"] > 0.5 and r["dup_cluster_ci_lo"] > 0.5
        rows.append({"expectation": "E1", "multiplicity": int(m), "subject": "P1 duplicate rate",
                     "estimate": r["dup_rate"], "ci_lo": r["dup_ci_lo"], "ci_hi": r["dup_ci_hi"], "p": bt.pvalue,
                     "rule": "Wilson and cluster-bootstrap lower bounds > 0.5",
                     "decision": _decide(ok, r["dup_rate"] > 0.5)})
    for m in retried:  # E2: P2 and P3 cut the P1 rate by more than 90 %
        for g in ("P2", "P3"):
            if ("P1", m) not in c.index or (g, m) not in c.index:
                continue
            b, x = c.loc[("P1", m)], c.loc[(g, m)]
            red, lo, hi = stats.relative_reduction(int(b["dup_mutations"]), int(b["injected_retries"]),
                                                   int(x["dup_mutations"]), int(x["injected_retries"]), alpha)
            rows.append({"expectation": "E2", "multiplicity": int(m), "subject": f"{g} reduction vs P1",
                         "estimate": red, "ci_lo": lo, "ci_hi": hi, "p": np.nan,
                         "rule": "lower bound of the relative reduction > 0.90",
                         "decision": _decide(lo > 0.90, red > 0.90) if not np.isnan(red) else "not testable (P1 had no duplicates)"})
    for m in sorted(cells["multiplicity"].unique()):  # E3: P3 costs more capacity than P2
        t = cap[(cap["multiplicity"] == m) & (cap["comparison"] == "P2 vs P3")] if len(cap) else cap
        if not len(t):
            continue
        t = t.iloc[0]
        diff, lo, hi = -t["diff"], -t["ci_hi"], -t["ci_lo"]  # P3 - P2
        ok = lo > 0 and t["p_holm"] < alpha
        rows.append({"expectation": "E3", "multiplicity": int(m), "subject": "P3 - P2 capacity per request",
                     "estimate": diff, "ci_lo": lo, "ci_hi": hi, "p": t["p_holm"],
                     "rule": "CI of P3 - P2 above 0 and Holm p < alpha",
                     "decision": "supported" if ok else ("not supported (P3 cheaper)" if hi < 0 else "not supported")})
    return pd.DataFrame(rows)


def checks(req: pd.DataFrame, dl: pd.DataFrame) -> pd.DataFrame:
    inj = dl[dl["inject"] == "after_commit"]
    items = [
        ("planned deliveries", int(req["multiplicity"].sum())),
        ("observed deliveries", len(dl)),
        ("missing deliveries", int(req["missing_deliveries"].sum())),
        ("deliveries with status error", int((dl["status"] == "error").sum())),
        ("after-commit injections that did not time out", int((inj["status"] != "timeout").sum())),
        ("deliveries whose record was lost (no capacity)", int(pd.to_numeric(dl["consumed_capacity"]).isna().sum())),
        ("requests with no business mutation", int(req["no_mutation"].sum())),
        ("requests where stream and self-report disagree", int(req["stream_self_mismatch"].sum())),
        ("final deliveries that were cold starts", int((req["cold_final"] == True).sum())),  # noqa: E712
        ("mutation ground truth", req["mutation_source"].iloc[0]),
    ]
    return pd.DataFrame(items, columns=["check", "value"])


# ---------- figures ----------

def _pos(a) -> np.ndarray:
    """Error-bar lengths; a bootstrap bound can sit a rounding error past the estimate."""
    return np.clip(np.asarray(a, dtype=float), 0, None)


def fig_dup(cells: pd.DataFrame, path: Path, tag: str) -> None:
    sub = cells[cells["injected_retries"] > 0]
    ms = sorted(sub["multiplicity"].unique())
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    for i, p in enumerate(PATHS):
        s = sub[sub["path"] == p].set_index("multiplicity").reindex(ms)
        x = np.arange(len(ms)) + (i - 1) * 0.26
        ax.bar(x, s["dup_rate"] * 100, 0.26, color=COLORS[p], label=p)
        ax.errorbar(x, s["dup_rate"] * 100, yerr=[_pos((s["dup_rate"] - s["dup_ci_lo"]) * 100),
                                                  _pos((s["dup_ci_hi"] - s["dup_rate"]) * 100)],
                    fmt="none", ecolor="black", capsize=3, lw=1)
        for xi, v in zip(x, s["dup_rate"], strict=True):  # a 0 % bar is invisible without its label
            if not np.isnan(v):
                ax.text(xi, v * 100 + 3, f"{v * 100:.1f}%", ha="center", fontsize=7)
    ax.set_xticks(range(len(ms)), [f"{m} deliveries" for m in ms])
    ax.set_ylabel("duplicate-mutation rate (%)")
    ax.set_ylim(0, 112)
    ax.set_title(f"Duplicate mutation per injected retry, 95 % Wilson CI\n[{tag}]", fontsize=9)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_latency(req: pd.DataFrame, path: Path, tag: str) -> None:
    ms = sorted(req["multiplicity"].unique())
    data, labels, colors = [], [], []
    for m in ms:
        for p in PATHS:
            x = req.loc[(req["path"] == p) & (req["multiplicity"] == m), "latency_ms"].dropna()
            data.append(x.to_numpy() if len(x) else np.array([np.nan]))
            labels.append(f"{p}\nx{m}")
            colors.append(COLORS[p])
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    bp = ax.boxplot(data, patch_artist=True, showfliers=False)
    for patch, col in zip(bp["boxes"], colors, strict=True):
        patch.set_facecolor(col)
        patch.set_alpha(0.6)
    ax.set_xticks(range(1, len(labels) + 1), labels, fontsize=8)
    ax.set_ylabel("final-delivery latency (ms)")
    ax.set_title(f"End-to-end latency of the delivery that succeeds (outliers hidden)\n[{tag}]", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_capacity(cells: pd.DataFrame, path: Path, tag: str) -> None:
    c = cells.sort_values(["multiplicity", "path"])
    x = np.arange(len(c))
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.bar(x, c["capacity_reported_mean"], color=[COLORS[p] for p in c["path"]], label="reported by DynamoDB")
    ax.bar(x, c["capacity_rule_mean"], bottom=c["capacity_reported_mean"], color="lightgrey", hatch="//",
           label="failed conditions (documented rule)")
    ax.set_xticks(x, [f"{p}\nx{m}" for p, m in zip(c["path"], c["multiplicity"], strict=True)], fontsize=8)
    ax.set_ylabel("capacity units per request")
    ax.set_title(f"Consumed capacity per request (all deliveries)\n[{tag}]", fontsize=9)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_surface(cells: pd.DataFrame, path: Path, tag: str) -> None:
    sub = cells[cells["injected_retries"] > 0]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), sharey=True)
    for ax, (col, lo, hi, label) in zip(axes, (
            ("capacity_mean", "capacity_mean_ci_lo", "capacity_mean_ci_hi", "capacity units per request"),
            ("latency_mean_ms", "latency_mean_ms_ci_lo", "latency_mean_ms_ci_hi", "mean final-delivery latency (ms)")),
            strict=True):
        for r in sub.itertuples():
            v = getattr(r, col)
            ax.errorbar(v, r.dup_rate * 100, xerr=_pos([[v - getattr(r, lo)], [getattr(r, hi) - v]]),
                        yerr=_pos([[(r.dup_rate - r.dup_ci_lo) * 100], [(r.dup_ci_hi - r.dup_rate) * 100]]),
                        fmt="o", color=COLORS[r.path], capsize=2, ms=6 + 2 * r.multiplicity)
            ax.annotate(f"{r.path} x{r.multiplicity}", (v, r.dup_rate * 100), textcoords="offset points",
                        xytext=(6, 4), fontsize=7)
        ax.set_xlabel(label)
    axes[0].set_ylabel("duplicate-mutation rate (%)")
    fig.suptitle(f"Correctness-cost surface (lower left is better)  [{tag}]", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------- main ----------

DUP_COLS = ["path", "multiplicity", "requests", "injected_retries", "dup_mutations", "dup_rate", "dup_ci_lo",
            "dup_ci_hi", "dup_cluster_ci_lo", "dup_cluster_ci_hi", "ccf_per_retry", "successful_retry_rate"]
COST_COLS = ["path", "multiplicity", "capacity_mean", "capacity_mean_ci_lo", "capacity_mean_ci_hi",
             "capacity_rule_mean", "latency_mean_ms", "latency_mean_ms_ci_lo", "latency_mean_ms_ci_hi",
             "latency_p95_ms", "latency_p95_ms_ci_lo", "latency_p95_ms_ci_hi", "latency_warm_mean_ms",
             "cold_final_share", "ddb_mean_ms"]
TEST_COLS = ["multiplicity", "comparison", "test", "mean_x", "mean_y", "diff", "ci_lo", "ci_hi", "effect_name",
             "effect", "p", "p_holm", "reject_h0"]


def analyse(campaign, out, figures, sensitivity=None, alpha: float = 0.05, B: int = 2000, seed: int = 0) -> dict:
    out, figures = Path(out), Path(figures)
    out.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    gt, dl, st_, info = metrics.load_run(campaign)
    tag = source_label(info.get("backend"))
    req = metrics.per_request(gt, dl, st_)
    cells = metrics.cell_summary(req, alpha, B, seed)
    dups, chi = dup_tests(cells, alpha), chi2_tests(cells)
    cap = cont_tests(req, "capacity_total", alpha, B, seed)
    lat = cont_tests(req, "latency_ms", alpha, B, seed)
    exp = expectations(cells, cap, alpha)
    chk = checks(req, dl)
    for name, df in (("requests", req), ("cells", cells), ("dup_tests", dups), ("chi2", chi),
                     ("capacity_tests", cap), ("latency_tests", lat), ("expectations", exp), ("checks", chk)):
        df.to_csv(out / f"{name}.csv", index=False)
    ftag = short_label(info.get("backend"))
    fig_dup(cells, figures / "dup_rate.png", ftag)
    fig_latency(req, figures / "latency.png", ftag)
    fig_capacity(cells, figures / "capacity.png", ftag)
    fig_surface(cells, figures / "surface.png", ftag)

    sens_md = ["Not run."]
    if sensitivity:
        sg, sd, ss, sinfo = metrics.load_run(sensitivity)
        sreq = metrics.per_request(sg, sd, ss)
        scells = metrics.cell_summary(sreq, alpha, B, seed)
        souts = sreq.groupby(["multiplicity", "final_outcome"]).size().rename("requests").reset_index()
        scells.to_csv(out / "sensitivity_cells.csv", index=False)
        souts.to_csv(out / "sensitivity_outcomes.csv", index=False)
        sens_md = [f"Source: {source_label(sinfo.get('backend'))}. P3 only, timeout between the business write "
                   "and marking the key COMPLETED.", "", md_table(scells[DUP_COLS]), "", md_table(souts)]

    fam = lambda df: f"{len(df)} tests, Holm-Bonferroni within this family"  # noqa: E731
    md = [
        "# Campaign analysis", "", "Generated by `analysis/analyse.py`.", "",
        f"- Source: **{tag}**",
        f"- Run: {info.get('t_start_utc', '?')}, {info.get('requests', '?')} requests, "
        f"{info.get('invocations', '?')} invocations, workers: {info.get('workers', '?')}",
        f"- alpha = {alpha}, bootstrap B = {B}, seed = {seed}", "",
        "## Data checks", "", md_table(chk), "",
        "## Duplicate mutation per injected retry (95 % Wilson and cluster-bootstrap CIs)", "",
        md_table(cells[DUP_COLS]), "",
        f"### Two-proportion z-tests ({fam(dups)})", "",
        md_table(dups) if len(dups) else "No retried cells.", "",
        "### Chi-square, duplicate yes/no by cell", "", md_table(chi), "",
        "## Capacity and latency per request (95 % bootstrap CIs)", "", md_table(cells[COST_COLS]), "",
        f"### Capacity tests ({fam(cap)})", "", md_table(cap[TEST_COLS]) if len(cap) else "-", "",
        f"### Latency tests ({fam(lat)})", "", md_table(lat[TEST_COLS]) if len(lat) else "-", "",
        "## Pre-registered expectations", "", md_table(exp), "",
        "## Sensitivity: P3 crash between writes", "", *sens_md, "",
        "## Figures", "",
        *[f"- `{figures / f}`" for f in ("dup_rate.png", "latency.png", "capacity.png", "surface.png")], "",
        SIGN, ""]
    (out / "summary.md").write_text("\n".join(md))
    run = {"source": info.get("backend"), "campaign": str(campaign), "sensitivity": str(sensitivity or ""),
           "alpha": alpha, "B": B, "seed": seed}
    (out / "analysis_info.json").write_text(json.dumps(run, indent=2) + "\n")
    return {"cells": cells, "expectations": exp, "dup_tests": dups}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--campaign", required=True)
    ap.add_argument("--sensitivity")
    ap.add_argument("--out", required=True)
    ap.add_argument("--figures", required=True)
    ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--config", default=str(ROOT / "config/experiment.yaml"))
    args = ap.parse_args(argv)
    cfg = yaml.safe_load(open(args.config))
    res = analyse(args.campaign, args.out, args.figures, args.sensitivity, cfg["alpha"], args.bootstrap)
    print(res["expectations"][["expectation", "multiplicity", "subject", "decision"]].to_string(index=False))
    print("->", Path(args.out) / "summary.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
