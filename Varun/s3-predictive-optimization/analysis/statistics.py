"""Statistics: live-lite Wilcoxon re-export + local 3-workload FinOps protocol.

CA2 §3.3: paired Wilcoxon across trial buckets for three workloads
(static/archival, mixed-access, high-churn) vs Lifecycle and Intelligent-Tiering.

This *executes* that protocol on the local simulator (evidence-bound). It does
not invent live-AWS campaign cells. Live-lite Wilcoxon remains in
``results/live/live_lite_summary.json``.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation.metrics import MetricsCalculator
from src.pricing.s3_pricing import S3Pricing
from src.recommendation.baseline import BaselineRecommender
from src.savings.estimator import SavingsEstimator
from src.simulator.workload_generator import WorkloadGenerator

SUMMARY = ROOT / "results" / "live" / "live_lite_summary.json"

# CA2 Table 2 workload types (access-pattern mixes).
WORKLOADS = {
    "static_archival": {"hot": 0.05, "warm": 0.15, "cold": 0.80},
    "mixed_access": {"hot": 0.20, "warm": 0.30, "cold": 0.50},
    "high_churn": {"hot": 0.70, "warm": 0.20, "cold": 0.10},
}
# Stable offsets so trial seeds do not depend on PYTHONHASHSEED.
WORKLOAD_SEED_OFFSET = {
    "static_archival": 1000,
    "mixed_access": 2000,
    "high_churn": 3000,
}

BASELINE_CONFIG = {
    "baseline": {
        "age_threshold_ia": 30,
        "age_threshold_glacier_instant": 90,
        "age_threshold_glacier_deep": 180,
        "access_threshold_ia": 5,
        "access_threshold_glacier": 1,
        "size_threshold_kb": 128,
    }
}


def load_summary(path: Optional[Path] = None) -> Dict[str, Any]:
    with open(path or SUMMARY) as f:
        return json.load(f)


def wilcoxon_from_lite(summary: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    summary = summary or load_summary()
    block = summary.get("wilcoxon")
    if block is None:
        block = (summary.get("stats") or {}).get("wilcoxon")
    if block is None:
        for k, v in summary.items():
            if "wilcoxon" in k.lower() and isinstance(v, dict):
                block = v
                break
    return {
        "source": "live_lite_summary.json",
        "n_per_arm": (summary.get("s3") or {}).get("objects_per_arm"),
        "wilcoxon": block,
        "disclaimer": "Pre-computed on live lite; not a fuller FinOps campaign ANOVA.",
    }


def _trial_costs(
    *,
    n_objects: int,
    patterns: Dict[str, float],
    seed: int,
) -> Dict[str, Any]:
    gen = WorkloadGenerator(seed=seed)
    objects = gen.generate_objects(
        n_objects,
        {
            "access_patterns": [patterns],
            "size_distribution": {
                "mean_mb": 10,
                "std_mb": 5,
                "min_mb": 0.1,
                "max_mb": 100,
            },
        },
    )
    t0 = time.perf_counter()
    recs = BaselineRecommender(BASELINE_CONFIG, S3Pricing()).recommend_batch(objects)
    estimator = SavingsEstimator(S3Pricing())
    cmp_ = estimator.comprehensive_comparison(objects, recs)
    overhead_s = time.perf_counter() - t0
    our = float(cmp_["our_approach"]["cost_monthly"])
    lc = float(cmp_["aws_lifecycle_policies"]["cost_monthly"])
    it = float(cmp_["aws_intelligent_tiering"]["cost_monthly"])
    unopt = our + float(cmp_["our_approach"]["savings_vs_unoptimized"])
    return {
        "our_cost": our,
        "lifecycle_cost": lc,
        "intelligent_tiering_cost": it,
        "unoptimized_cost": unopt,
        "overhead_s": overhead_s,
        "n_objects": n_objects,
    }


def run_multi_workload_wilcoxon(
    n_trials: int = 10,
    objects_per_trial: int = 80,
    seed: int = 42,
) -> Dict[str, Any]:
    """Paired Wilcoxon per CA2 workload type (local simulator).

    ``n_trials`` maps to CA2's n≈10–15 trial buckets. Each bucket is an
    independent synthetic object set, not a live S3 bucket.
    """
    metrics = MetricsCalculator()
    workloads_out: Dict[str, Any] = {}
    significant_vs_both = []

    for name, patterns in WORKLOADS.items():
        our_costs: List[float] = []
        lc_costs: List[float] = []
        it_costs: List[float] = []
        overheads: List[float] = []
        for i in range(n_trials):
            row = _trial_costs(
                n_objects=objects_per_trial,
                patterns=patterns,
                seed=seed + i + WORKLOAD_SEED_OFFSET[name],
            )
            our_costs.append(row["our_cost"])
            lc_costs.append(row["lifecycle_cost"])
            it_costs.append(row["intelligent_tiering_cost"])
            overheads.append(row["overhead_s"])

        try:
            w_lc = metrics.wilcoxon_test(our_costs, lc_costs)
        except ValueError as exc:
            w_lc = {
                "test": "wilcoxon",
                "statistic": None,
                "p_value": None,
                "significant": False,
                "n": len(our_costs),
                "note": str(exc),
            }
        try:
            w_it = metrics.wilcoxon_test(our_costs, it_costs)
        except ValueError as exc:
            w_it = {
                "test": "wilcoxon",
                "statistic": None,
                "p_value": None,
                "significant": False,
                "n": len(our_costs),
                "note": str(exc),
            }
        mean_our = float(sum(our_costs) / len(our_costs))
        mean_lc = float(sum(lc_costs) / len(lc_costs))
        mean_it = float(sum(it_costs) / len(it_costs))
        vs_both = bool(
            w_lc.get("significant")
            and w_it.get("significant")
            and mean_our < mean_lc
            and mean_our < mean_it
        )
        if vs_both:
            significant_vs_both.append(name)
        workloads_out[name] = {
            "n_trials": n_trials,
            "objects_per_trial": objects_per_trial,
            "access_patterns": patterns,
            "mean_our_cost": mean_our,
            "mean_lifecycle_cost": mean_lc,
            "mean_intelligent_tiering_cost": mean_it,
            "mean_delta_vs_lifecycle": mean_lc - mean_our,
            "mean_delta_vs_intelligent_tiering": mean_it - mean_our,
            "wilcoxon_vs_lifecycle": w_lc,
            "wilcoxon_vs_intelligent_tiering": w_it,
            "mean_overhead_s": float(sum(overheads) / len(overheads)),
            "significant_cost_cut_vs_both_natives": vs_both,
            "mode": "local_simulator",
        }

    return {
        "protocol": "ca2_three_workload_wilcoxon",
        "mode": "local_simulator",
        "alpha": 0.05,
        "n_trials_per_workload": n_trials,
        "objects_per_trial": objects_per_trial,
        "seed": seed,
        "workloads": workloads_out,
        "success_workloads_vs_both_natives": significant_vs_both,
        "meets_ca2_two_of_three": len(significant_vs_both) >= 2,
        "operational_overhead": {
            "metric": "recommend_plus_savings_compare_seconds",
            "mean_s_by_workload": {
                k: v["mean_overhead_s"] for k, v in workloads_out.items()
            },
        },
        "disclaimer": (
            "Local simulator trial-buckets, not live S3 Inventory / CE-settled "
            "billing. Live-lite probe remains the only live AWS Wilcoxon."
        ),
    }


class _NumpyEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, np.generic):
            return o.item()
        return super().default(o)


def combined_report(
    *,
    n_trials: int = 10,
    objects_per_trial: int = 80,
    include_multi: bool = True,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "live_lite": wilcoxon_from_lite(),
    }
    if include_multi:
        out["multi_workload_local"] = run_multi_workload_wilcoxon(
            n_trials=n_trials, objects_per_trial=objects_per_trial
        )
    return out


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Varun statistics (lite + local 3-workload)")
    p.add_argument("--input", default=None, help="Unused (compat with Makefile stats)")
    p.add_argument(
        "--output",
        default=str(ROOT / "results" / "data" / "multi_workload_wilcoxon.json"),
    )
    p.add_argument("--lite-only", action="store_true")
    p.add_argument("--n-trials", type=int, default=10)
    p.add_argument("--objects-per-trial", type=int, default=80)
    args = p.parse_args(argv)
    report = combined_report(
        n_trials=args.n_trials,
        objects_per_trial=args.objects_per_trial,
        include_multi=not args.lite_only,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, cls=_NumpyEncoder) + "\n")
    print(json.dumps(report, indent=2, cls=_NumpyEncoder)[:4000])
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
