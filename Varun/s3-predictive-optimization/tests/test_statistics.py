"""Tests for lite Wilcoxon re-export and local 3-workload protocol."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis.statistics import (
    WORKLOADS,
    run_multi_workload_wilcoxon,
    wilcoxon_from_lite,
)


def test_wilcoxon_from_lite_has_n24_probe():
    block = wilcoxon_from_lite()
    assert block["n_per_arm"] == 24
    assert block["wilcoxon"] is not None
    assert "lite" in block["disclaimer"].lower() or "FinOps" in block["disclaimer"]


def test_multi_workload_protocol_three_types_and_overhead():
    # Small n so the unit test stays fast; the committed campaign uses n=10.
    report = run_multi_workload_wilcoxon(n_trials=6, objects_per_trial=40, seed=7)
    assert report["mode"] == "local_simulator"
    assert set(report["workloads"]) == set(WORKLOADS)
    assert report["n_trials_per_workload"] == 6
    for name, w in report["workloads"].items():
        assert w["wilcoxon_vs_lifecycle"]["n"] == 6
        assert w["wilcoxon_vs_intelligent_tiering"]["n"] == 6
        assert w["mean_overhead_s"] > 0
        assert w["mode"] == "local_simulator"
    assert "mean_s_by_workload" in report["operational_overhead"]
    assert isinstance(report["meets_ca2_two_of_three"], bool)
    assert "not live" in report["disclaimer"].lower() or "Local" in report["disclaimer"]
