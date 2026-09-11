import numpy as np
import pytest
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint, proportions_ztest

from analysis import stats


def test_wilson_matches_statsmodels():
    for k, n in [(0, 50), (50, 50), (13, 40), (1, 1000)]:
        _, lo, hi = stats.wilson(k, n)
        elo, ehi = proportion_confint(k, n, method="wilson")
        assert lo == pytest.approx(elo, abs=1e-9) and hi == pytest.approx(ehi, abs=1e-9)


def test_wilson_interval_always_contains_the_estimate():
    for n in range(1, 400):  # at 0 % and 100 % rounding used to push a bound past p
        assert stats.wilson(n, n)[2] == 1.0 and stats.wilson(0, n)[1] == 0.0
        p, lo, hi = stats.wilson(n // 3, n)
        assert lo <= p <= hi


def test_two_proportion_z_matches_statsmodels():
    z, p = stats.two_prop_z(40, 50, 10, 50, "greater")
    ez, ep = proportions_ztest([40, 10], [50, 50], alternative="larger")
    assert z == pytest.approx(ez) and p == pytest.approx(ep)
    assert stats.two_prop_z(0, 50, 0, 50) == (0.0, 1.0)


def test_holm_matches_statsmodels_and_skips_nan():
    p = [0.01, 0.04, 0.03, 0.2]
    assert np.allclose(stats.holm(p), multipletests(p, method="holm")[1])
    assert np.isnan(stats.holm([0.01, np.nan])[1])


def test_newcombe_interval_at_the_extremes():
    d, lo, hi = stats.newcombe_diff(50, 50, 0, 50)
    assert d == 1.0 and 0.85 < lo < 1.0 and hi == pytest.approx(1.0)


def test_relative_reduction():
    red, lo, hi = stats.relative_reduction(1000, 1000, 0, 1000)
    assert red == 1.0 and 0.98 < lo < hi < 1.0
    assert np.isnan(stats.relative_reduction(0, 100, 0, 100)[0])  # nothing to reduce


def test_chi2_flags_degenerate_tables():
    assert stats.chi2_table([[5, 0], [5, 0]])["note"].startswith("degenerate")
    r = stats.chi2_table([[50, 0], [0, 50]])
    assert r["p"] < 1e-10 and r["dof"] == 1


def test_compare_picks_the_test_by_normality():
    rng = np.random.default_rng(1)
    r = stats.compare(rng.normal(10, 1, 200), rng.normal(10.5, 1, 200))
    assert r["test"] == "welch_t" and r["p"] < 0.05 and r["ci_hi"] < 0
    r = stats.compare(rng.lognormal(0, 1, 200), rng.lognormal(0.6, 1, 200))
    assert r["test"] == "mann_whitney_u" and r["effect"] < 0
    r = stats.compare(np.full(50, 5.0), np.full(50, 7.0))  # capacity is often constant per cell
    assert r["diff"] == -2.0 and r["p"] < 1e-6 and r["effect"] == -1.0
    assert stats.compare(np.ones(5), np.ones(5))["p"] == 1.0


def test_cluster_ci_and_sizing_formulas():
    assert stats.cluster_rate_ci([4] * 100, [4] * 100) == (1.0, 1.0)
    assert stats.n_for_proportion(0.5, 0.01) == 9604
    assert stats.n_for_mean(1.0, 10.0, 5) == 16
    lo, hi = stats.bootstrap_ci(np.arange(100.0))
    assert lo < 49.5 < hi
