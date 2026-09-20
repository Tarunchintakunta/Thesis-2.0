"""Statistical helpers for the S3 FinOps evaluation (Wilcoxon signed-rank).

Wraps the existing MetricsCalculator.wilcoxon_test so analysis/statistics.py
exists as the CA2-named module. Does not invent multi-workload live campaigns.
"""
from __future__ import annotations

from typing import Dict, List, Sequence

from src.evaluation.metrics import MetricsCalculator


def wilcoxon_paired(sample1: Sequence[float], sample2: Sequence[float], alpha: float = 0.05) -> Dict:
    return MetricsCalculator.wilcoxon_test(list(sample1), list(sample2), alpha=alpha)


def multi_workload_protocol(results_by_workload: Dict[str, Dict], alpha: float = 0.05) -> Dict:
    """CA2 success: significant cost cut on ≥2/3 named workloads.

    Each value must already contain paired cost arrays `baseline` and `improved`.
    Missing workloads are reported, not filled.
    """
    per = {}
    wins = 0
    for name, payload in results_by_workload.items():
        test = wilcoxon_paired(payload["baseline"], payload["improved"], alpha=alpha)
        per[name] = test
        if test.get("significant"):
            wins += 1
    n = len(results_by_workload)
    return {
        "alpha": alpha,
        "n_workloads": n,
        "n_significant": wins,
        "success_rule": "significant on >= 2 of 3 workloads",
        "success": n >= 3 and wins >= 2,
        "per_workload": per,
        "note": "live multi-workload campaign not run; pass only if three workloads supplied",
    }
