import numpy as np
import pytest

from coldstart import stats


def test_describe_percentiles():
    d = stats.describe(np.arange(1, 101))
    assert d["n"] == 100 and d["p50"] == pytest.approx(50.5) and d["p99"] == pytest.approx(99.01)
    assert stats.describe([])["n"] == 0


def test_holm_matches_hand_calculation():
    adj = stats.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adj["a"] == pytest.approx(0.03)
    assert adj["c"] == pytest.approx(0.06)
    assert adj["b"] == pytest.approx(0.06)  # monotone: never below the previous one


def test_holm_caps_at_one():
    assert stats.holm({"a": 0.6, "b": 0.7})["b"] == 1.0


def test_normal_samples_use_welch_t():
    rng = np.random.default_rng(1)
    r = stats.compare_two(rng.normal(100, 10, 60), rng.normal(90, 10, 60))
    assert r["test"] == "welch_t" and r["p"] < 0.05 and r["effect"] > 0


def test_skewed_samples_use_mann_whitney():
    rng = np.random.default_rng(2)
    a, b = rng.lognormal(5, 0.8, 80), rng.lognormal(4.5, 0.8, 80)
    r = stats.compare_two(a, b)
    assert r["test"] == "mann_whitney_u" and r["effect_name"] == "rank_biserial"
    assert 0 < r["effect"] <= 1
    lo, hi = r["median_diff_ci95"]
    assert lo < r["median_diff"] < hi


def test_rank_biserial_extremes():
    assert stats.rank_biserial(100, 10, 10) == 1.0
    assert stats.rank_biserial(0, 10, 10) == -1.0


def test_three_groups_kruskal_and_epsilon():
    rng = np.random.default_rng(3)
    g = {"python": rng.lognormal(5.0, 0.6, 50), "nodejs": rng.lognormal(5.1, 0.6, 50),
         "java": rng.lognormal(6.0, 0.6, 50)}
    r = stats.compare_many(g)
    assert r["test"] == "kruskal_wallis" and r["p"] < 0.001
    assert 0 < r["effect"] < 1 and r["groups"] == ["python", "nodejs", "java"]


def test_three_normal_groups_anova_and_eta():
    rng = np.random.default_rng(4)
    r = stats.compare_many({k: rng.normal(m, 5, 40) for k, m in [("a", 50), ("b", 55), ("c", 60)]})
    assert r["test"] == "anova" and 0 < r["effect"] < 1


def test_paired_blocks():
    rng = np.random.default_rng(5)
    off = rng.uniform(0.3, 0.7, 20)
    on = off - rng.uniform(0.2, 0.3, 20)
    r = stats.compare_paired(on, off)
    assert r["p"] < 0.01 and r["effect"] < 0


def test_paired_all_ties():
    r = stats.compare_paired([0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
    assert r["p"] == 1.0


def test_wilson_interval():
    lo, hi = stats.wilson(5, 10)
    assert lo < 0.5 < hi and 0 <= lo and hi <= 1
    assert stats.wilson(0, 10)[0] == 0.0


def test_fisher_2x2():
    r = stats.fisher_2x2(2, 50, 20, 50)
    assert r["p"] < 0.001 and r["risk_difference"] == pytest.approx(-0.36)
