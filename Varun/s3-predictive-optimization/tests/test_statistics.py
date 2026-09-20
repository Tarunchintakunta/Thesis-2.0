"""Wilcoxon helper module (analysis/statistics.py)."""
from analysis.statistics import multi_workload_protocol, wilcoxon_paired


def test_wilcoxon_paired_significant():
    a = list(range(1, 25))
    b = [x * 0.5 for x in a]
    r = wilcoxon_paired(a, b)
    assert r["n"] == 24
    assert bool(r["significant"]) is True


def test_multi_workload_requires_three():
    payload = {
        "w1": {"baseline": list(range(10, 20)), "improved": list(range(1, 11))},
        "w2": {"baseline": list(range(10, 20)), "improved": list(range(1, 11))},
    }
    r = multi_workload_protocol(payload)
    assert r["n_workloads"] == 2
    assert r["success"] is False
