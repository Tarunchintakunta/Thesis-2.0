"""Scoring invariants."""

from src.metrics import confusion, mcnemar, rates, wilson_ci


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
