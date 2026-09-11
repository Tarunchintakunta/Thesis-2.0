#!/usr/bin/env python
"""Pre-registered analysis of results/batches.csv -> tables, figures and hypotheses.json.

    python analysis/analyse.py --results results/ --out report/generated/
    python analysis/analyse.py --results results_smoke/ --out results_smoke/analysis/

Per workload: H_key (mean latency, key-design term), H_cap (throttle rate,
capacity-mode term), H_joint (latency-optimal vs cost-optimal configuration),
Holm over all twelve. The two-way model (with interaction) or its aligned-rank
version is picked by analysis/stats.py. Rows that are not `data_source = live`
are stamped with their source everywhere - moto smoke numbers are not DynamoDB
measurements. Without a batches.csv the result tables are written as
[TO BE FILLED FROM EXPERIMENT] placeholders in the 6 x 4 cell layout.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis import stats  # noqa: E402
from analysis.cost_model import add_costs, load_prices  # noqa: E402
from workloads.matrix import CONFIGS  # noqa: E402

PLACEHOLDER = "[TO BE FILLED FROM EXPERIMENT]"
CONFIG_IDS = [f"{k}-{m}" for k, m in CONFIGS]
WORKLOADS = ["W1", "W2", "W3", "W4"]
SUMMARY_COLS = ["latency_mean_ms", "latency_p95_ms", "latency_p99_ms", "throughput_ops_s", "throttle_rate",
                "cost_per_10k"]


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, list | tuple):
        return [_clean(v) for v in o]
    if isinstance(o, np.integer | np.bool_):
        return o.item()
    if isinstance(o, float | np.floating):
        return None if math.isnan(o) else round(float(o), 6)
    return o


def md(df: pd.DataFrame) -> str:
    def f(v):
        return f"{v:.4g}" if isinstance(v, float) else str(v)
    return "\n".join(["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)] +
                     ["| " + " | ".join(f(v) for v in r) + " |" for r in df.itertuples(index=False)])


def placeholders(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    rows = [{"workload": w, "configuration": c, **{k: PLACEHOLDER for k in SUMMARY_COLS}}
            for w in WORKLOADS for c in CONFIG_IDS]
    (out / "cell_summary.md").write_text("# Cell summary (6 configurations x 4 workloads)\n\n"
                                         f"No results/batches.csv yet - every value is {PLACEHOLDER}.\n\n"
                                         + md(pd.DataFrame(rows)) + "\n")


def cell_summary(b: pd.DataFrame) -> pd.DataFrame:
    g = b.groupby(["workload", "configuration"])
    s = g[SUMMARY_COLS].mean()
    s["n"] = g.size()
    s["rcu_per_10k"] = g["rcu"].sum() / g["succeeded"].sum() * 10_000
    s["wcu_per_10k"] = g["wcu"].sum() / g["succeeded"].sum() * 10_000
    return s.reset_index()


def pareto(cs: pd.DataFrame) -> pd.DataFrame:
    """Configurations nobody beats on latency, throttle rate and cost at once (per workload)."""
    rows = []
    for w, g in cs.groupby("workload"):
        v = g[["latency_mean_ms", "throttle_rate", "cost_per_10k"]].to_numpy(float)
        for i, r in enumerate(g.itertuples()):
            dominated = any(np.all(v[j] <= v[i]) and np.any(v[j] < v[i]) for j in range(len(v)) if j != i)
            rows.append({"workload": w, "configuration": r.configuration, "on_front": not dominated})
    return pd.DataFrame(rows)


def run_tests(b: pd.DataFrame, cfg: dict) -> dict:
    a = cfg["analysis"]
    tests = {}
    for w in WORKLOADS:
        d = b[b["workload"] == w]
        if d.empty or d["configuration"].nunique() < len(CONFIG_IDS):
            continue
        tests[f"H_key_{w}"] = {"dv": "latency_mean_ms", "term": "key", **stats.factorial(d, "latency_mean_ms", a["alpha"])}
        tests[f"H_cap_{w}"] = {"dv": "throttle_rate", "term": "capacity", **stats.factorial(d, "throttle_rate", a["alpha"])}
        tests[f"H_joint_{w}"] = {"dv": "latency_mean_ms+cost_per_10k",
                                 **stats.joint_divergence(d, "latency_mean_ms", "cost_per_10k", a["bootstrap"])}
        ref = d[d["configuration"] == a["reference_configuration"]]["latency_mean_ms"].mean()
        by_key = d.groupby("key_design")["latency_mean_ms"].mean()
        tests[f"H_key_{w}"]["practical"] = bool((by_key.max() - by_key.min()) >= a["practical_latency_pct"] / 100 * ref)
        by_cfg_cost = d.groupby("configuration")["cost_per_10k"].mean()
        ref_cost = by_cfg_cost.get(a["reference_configuration"], float("nan"))
        tests[f"H_joint_{w}"]["practical"] = bool((by_cfg_cost.max() - by_cfg_cost.min()) >= a["practical_cost_pct"] / 100 * ref_cost)
    primary = {}
    for k, t in tests.items():
        primary[k] = t["p"] if k.startswith("H_joint") else t["terms"][t["term"]]["p"]
    for k, p_adj in stats.holm(primary).items():
        tests[k]["p_primary"] = primary[k]
        tests[k]["p_holm"] = p_adj
        tests[k]["reject"] = bool(p_adj < a["alpha"])
    return tests


def figures(cs: pd.DataFrame, front: pd.DataFrame, out: Path, label: str, live: bool) -> list[str]:
    made = []

    def stamp(fig):
        fig.text(0.01, 0.005, label, fontsize=7, color="#555555")
        if not live:
            fig.text(0.5, 0.5, "NOT DynamoDB DATA", fontsize=32, color="red", alpha=0.15, rotation=25,
                     ha="center", va="center")

    for col, name, ylab in [("latency_mean_ms", "latency_by_configuration.png", "mean latency (ms)"),
                            ("throttle_rate", "throttle_rate.png", "throttled / attempted"),
                            ("cost_per_10k", "cost_per_10k.png", "USD per 10,000 successful ops")]:
        fig, axes = plt.subplots(1, len(cs["workload"].unique()), figsize=(12, 3.4), sharey=False, squeeze=False)
        for ax, (w, g) in zip(axes[0], cs.groupby("workload"), strict=False):
            ax.bar(range(len(g)), g[col], color=["#4c72b0" if "on_demand" in c else "#dd8452" for c in g["configuration"]])
            ax.set_xticks(range(len(g)), [c.replace("-on_demand", "\nOD").replace("-provisioned", "\nPR") for c in g["configuration"]],
                          fontsize=7)
            ax.set_title(w)
        axes[0][0].set_ylabel(ylab)
        stamp(fig)
        fig.tight_layout(rect=(0, 0.04, 1, 1))
        fig.savefig(out / name, dpi=120)
        plt.close(fig)
        made.append(name)
    fig, axes = plt.subplots(1, len(cs["workload"].unique()), figsize=(12, 3.6), squeeze=False)
    merged = cs.merge(front, on=["workload", "configuration"])
    for ax, (w, g) in zip(axes[0], merged.groupby("workload"), strict=False):
        size = 30 + 400 * g["throttle_rate"].fillna(0)
        ax.scatter(g["latency_mean_ms"], g["cost_per_10k"], s=size, c=np.where(g["on_front"], "#2a9d8f", "#bbbbbb"),
                   edgecolors="black")
        for r in g.itertuples():
            ax.annotate(r.configuration.replace("on_demand", "OD").replace("provisioned", "PR"),
                        (r.latency_mean_ms, r.cost_per_10k), fontsize=6, xytext=(3, 3), textcoords="offset points")
        ax.set(title=f"{w} (size = throttle rate)", xlabel="mean latency (ms)")
    axes[0][0].set_ylabel("USD per 10k ops")
    stamp(fig)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(out / "tradeoff_surface.png", dpi=120)
    plt.close(fig)
    made.append("tradeoff_surface.png")
    return made


def analyse(results: Path, out: Path, cfg: dict) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    path = results / "batches.csv"
    if not path.exists():
        placeholders(out)
        return {"status": "no data - placeholders written"}
    b = add_costs(pd.read_csv(path), load_prices())
    sources = sorted(b["data_source"].dropna().unique())
    if len(sources) != 1:
        raise ValueError(f"mixed data sources {sources} - never analyse them together")
    live = sources[0] == "live"
    label = "measured on Amazon DynamoDB (eu-west-1)" if live else f"{sources[0]} - NOT DynamoDB measurements"
    excluded = int(b["cold_contaminated"].astype(str).str.lower().eq("true").sum())
    b = b[~b["cold_contaminated"].astype(str).str.lower().eq("true")]
    cs = cell_summary(b)
    front = pareto(cs)
    tests = run_tests(b, cfg)
    cs.to_csv(out / "cell_summary.csv", index=False)
    (out / "cell_summary.md").write_text(f"# Cell summary\n\n**Data: {label}.** {excluded} cold-contaminated batches excluded.\n\n"
                                         + md(cs.round(6)) + "\n")
    front.to_csv(out / "pareto.csv", index=False)
    figs = figures(cs, front, out, label, live)
    result = {"label": label, "data_source": sources[0], "batches": len(b), "cold_contaminated_excluded": excluded,
              "tests": tests, "figures": figs}
    (out / "hypotheses.json").write_text(json.dumps(_clean(result), indent=2) + "\n")
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default=str(ROOT / "results"))
    ap.add_argument("--out", default=str(ROOT / "report/generated"))
    ap.add_argument("--config", default=str(ROOT / "config/experiment.yaml"))
    args = ap.parse_args(argv)
    with open(args.config, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    res = analyse(Path(args.results), Path(args.out), cfg)
    print(res.get("label", res.get("status")))
    for k, t in res.get("tests", {}).items():
        print(f"  {k:12s} {t.get('method', t.get('test')):18s} p={t['p_primary']:.4g} p_holm={t['p_holm']:.4g} reject={t['reject']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
