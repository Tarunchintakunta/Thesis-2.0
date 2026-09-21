"""Scoring invariants."""

from src.metrics import confusion, holm_bonferroni, mcnemar, rates, wilson_ci


def test_perfect_detection():
    c = confusion([1, 1, 0, 0], [1, 1, 0, 0])
    r = rates(c)
    assert c["tp"] == 2 and c["tn"] == 2
    assert r["precision"] == 1
    assert r["recall"] == 1
    assert r["f1"] == 1
    assert r["fn_rate"] == 0


def test_all_missed():
    c = confusion([1, 1, 0], [0, 0, 0])
    r = rates(c)
    assert r["recall"] == 0
    assert r["fn_rate"] == 1
    assert r["precision"] == 0


def test_wilson_bounds():
    lo, hi = wilson_ci(9, 10)
    assert 0 <= lo <= 0.9 <= hi <= 1


def test_mcnemar_symmetric():
    s = mcnemar(5, 5)
    assert s["p_two_sided"] > 0.5


def test_holm_rejects_only_smallest_when_others_above():
    tests = [
        {"pair": "a", "p_two_sided": 1e-9},
        {"pair": "b", "p_two_sided": 0.053},
        {"pair": "c", "p_two_sided": 0.058},
        {"pair": "d", "p_two_sided": 0.23},
    ]
    out = holm_bonferroni(tests, alpha=0.05)
    by_pair = {r["pair"]: r for r in out}
    assert by_pair["a"]["holm_reject_alpha_0_05"] is True
    assert by_pair["b"]["holm_reject_alpha_0_05"] is False
    assert by_pair["c"]["holm_reject_alpha_0_05"] is False
    assert by_pair["d"]["holm_reject_alpha_0_05"] is False
    assert by_pair["a"]["holm_rank"] == 1
