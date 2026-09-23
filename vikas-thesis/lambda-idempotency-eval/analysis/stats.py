"""Statistics used by analyse.py and pilot_size.py (plan in docs/ANALYSIS_PLAN.md).

Proportions: Wilson intervals, two-proportion z-tests, Newcombe's interval for
a difference, a Katz interval for the relative reduction, chi-square for the
path x multiplicity table. Continuous (latency, capacity): Shapiro-Wilk picks
Welch's t-test or Mann-Whitney U (with the rank-biserial correlation); the
interval for a difference is always a bootstrap. Holm-Bonferroni per family.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats as st

NAN = float("nan")


def z_crit(alpha: float = 0.05) -> float:
    return float(st.norm.ppf(1 - alpha / 2))


# ---------- proportions ----------

def wilson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float, float]:
    if n == 0:
        return NAN, NAN, NAN
    z, p = z_crit(alpha), k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    # the interval always contains p; at 0 % / 100 % rounding can push a bound just past it
    return p, min(p, max(0.0, centre - half)), max(p, min(1.0, centre + half))


def newcombe_diff(k1: int, n1: int, k2: int, n2: int, alpha: float = 0.05) -> tuple[float, float, float]:
    """p1 - p2 with Newcombe's hybrid score interval - behaves at 0 % and 100 %."""
    p1, l1, u1 = wilson(k1, n1, alpha)
    p2, l2, u2 = wilson(k2, n2, alpha)
    d = p1 - p2
    return d, d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)


def two_prop_z(k1: int, n1: int, k2: int, n2: int, alternative: str = "two-sided") -> tuple[float, float]:
    """Pooled two-proportion z-test; alternative 'greater' means p1 > p2."""
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return 0.0, 1.0  # both 0 % or both 100 %: no evidence of a difference
    z = (k1 / n1 - k2 / n2) / se
    if alternative == "greater":
        return z, float(st.norm.sf(z))
    if alternative == "less":
        return z, float(st.norm.cdf(z))
    return z, float(2 * st.norm.sf(abs(z)))


def relative_reduction(k_base: int, n_base: int, k: int, n: int, alpha: float = 0.05) -> tuple[float, float, float]:
    """1 - p/p_base with a Katz log interval; 0.5 is added to every cell when a count is 0 or n."""
    if k_base == 0:
        return NAN, NAN, NAN  # nothing to reduce
    a, b, c, d = float(k), float(n), float(k_base), float(n_base)
    if min(a, c) == 0 or a == b or c == d:
        a, b, c, d = a + 0.5, b + 1, c + 0.5, d + 1
    rr = (a / b) / (c / d)
    se = math.sqrt(1 / a - 1 / b + 1 / c - 1 / d)
    z = z_crit(alpha)
    return 1 - (k / n) / (k_base / n_base), 1 - rr * math.exp(z * se), 1 - rr * math.exp(-z * se)


def chi2_table(table) -> dict:
    t = np.asarray(table, dtype=float)
    t = t[t.sum(axis=1) > 0]
    t = t[:, t.sum(axis=0) > 0]
    if t.shape[0] < 2 or t.shape[1] < 2:
        return {"chi2": NAN, "p": NAN, "dof": 0, "min_expected": NAN, "note": "degenerate table (a whole column is empty)"}
    chi2, p, dof, exp = st.chi2_contingency(t, correction=False)
    note = "" if exp.min() >= 5 else "an expected count is below 5 - read with care"
    return {"chi2": float(chi2), "p": float(p), "dof": int(dof), "min_expected": float(exp.min()), "note": note}


def cluster_rate_ci(dups, retries, B: int = 2000, alpha: float = 0.05, seed: int = 0) -> tuple[float, float]:
    """Bootstrap over requests: the retries of one request are not independent."""
    d, r = np.asarray(dups, float), np.asarray(retries, float)
    if len(d) == 0 or r.sum() == 0:
        return NAN, NAN
    idx = np.random.default_rng(seed).integers(0, len(d), (B, len(d)))
    rates = d[idx].sum(axis=1) / np.maximum(r[idx].sum(axis=1), 1e-12)
    return float(np.quantile(rates, alpha / 2)), float(np.quantile(rates, 1 - alpha / 2))


# ---------- continuous ----------

def is_normal(x, alpha: float = 0.05, seed: int = 0) -> tuple[bool, float]:
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) < 3 or np.ptp(x) == 0:
        return False, NAN
    if len(x) > 5000:
        x = np.random.default_rng(seed).choice(x, 5000, replace=False)
    p = float(st.shapiro(x).pvalue)
    return p >= alpha, p


def bootstrap_ci(x, stat: str = "mean", B: int = 2000, alpha: float = 0.05, seed: int = 0) -> tuple[float, float]:
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return NAN, NAN
    s = x[np.random.default_rng(seed).integers(0, len(x), (B, len(x)))]
    vals = s.mean(axis=1) if stat == "mean" else np.percentile(s, 95, axis=1)
    return float(np.quantile(vals, alpha / 2)), float(np.quantile(vals, 1 - alpha / 2))


def bootstrap_diff_ci(x, y, B: int = 2000, alpha: float = 0.05, seed: int = 0) -> tuple[float, float]:
    x, y = np.asarray(x, float), np.asarray(y, float)
    rng = np.random.default_rng(seed)
    dx = x[rng.integers(0, len(x), (B, len(x)))].mean(axis=1)
    dy = y[rng.integers(0, len(y), (B, len(y)))].mean(axis=1)
    return float(np.quantile(dx - dy, alpha / 2)), float(np.quantile(dx - dy, 1 - alpha / 2))


def rank_biserial(x, y) -> float:
    u = st.mannwhitneyu(x, y, alternative="two-sided").statistic  # U of x
    return float(2 * u / (len(x) * len(y)) - 1)


def compare(x, y, alpha: float = 0.05, alternative: str = "two-sided", B: int = 2000, seed: int = 0) -> dict:
    """Welch t if both samples look normal (Shapiro-Wilk), otherwise Mann-Whitney U."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    x, y = x[~np.isnan(x)], y[~np.isnan(y)]
    nx, px = is_normal(x, alpha, seed)
    ny, py = is_normal(y, alpha, seed)
    lo, hi = bootstrap_diff_ci(x, y, B, alpha, seed)
    out = {"mean_x": float(x.mean()), "mean_y": float(y.mean()), "diff": float(x.mean() - y.mean()), "ci_lo": lo,
           "ci_hi": hi, "shapiro_p_x": px, "shapiro_p_y": py}
    if np.ptp(np.concatenate([x, y])) == 0:
        return out | {"test": "none (all values equal)", "stat": NAN, "p": 1.0, "effect": 0.0,
                      "effect_name": "rank_biserial"}
    if nx and ny:
        t = st.ttest_ind(x, y, equal_var=False, alternative=alternative)
        sd = math.sqrt((x.var(ddof=1) + y.var(ddof=1)) / 2)
        return out | {"test": "welch_t", "stat": float(t.statistic), "p": float(t.pvalue),
                      "effect": float((x.mean() - y.mean()) / sd) if sd else NAN, "effect_name": "cohen_d"}
    u = st.mannwhitneyu(x, y, alternative=alternative)
    return out | {"test": "mann_whitney_u", "stat": float(u.statistic), "p": float(u.pvalue),
                  "effect": rank_biserial(x, y), "effect_name": "rank_biserial"}


# ---------- multiple testing and sizing ----------

def holm(pvals) -> np.ndarray:
    p = np.asarray(pvals, float)
    adj = np.full(len(p), NAN)
    ok = np.where(~np.isnan(p))[0]
    m, running = len(ok), 0.0
    for rank, i in enumerate(ok[np.argsort(p[ok])]):
        running = max(running, min(1.0, (m - rank) * p[i]))
        adj[i] = running
    return adj


def n_for_proportion(p: float, half_width: float, alpha: float = 0.05) -> int:
    return max(1, math.ceil(z_crit(alpha) ** 2 * p * (1 - p) / half_width ** 2))


def n_for_mean(sd: float, mean: float, pct: float, alpha: float = 0.05) -> int:
    if mean == 0 or sd == 0:
        return 1
    return max(1, math.ceil((z_crit(alpha) * sd / (pct / 100 * abs(mean))) ** 2))
