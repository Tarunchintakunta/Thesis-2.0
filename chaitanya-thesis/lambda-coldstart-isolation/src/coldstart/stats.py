"""Pre-registered tests from docs/ANALYSIS_PLAN.md.

Shapiro-Wilk decides the family: normal -> Welch t / paired t / one-way ANOVA,
otherwise Mann-Whitney U / Wilcoxon signed-rank / Kruskal-Wallis. Effect sizes
go with the test: Cohen's d, d_z, eta squared - or rank-biserial r, matched-pairs
rank-biserial, epsilon squared. Holm-Bonferroni over the confirmatory family.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats as st

ALPHA = 0.05


def describe(x) -> dict:
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return {"n": 0}
    p50, p95, p99 = np.percentile(x, [50, 95, 99])
    return {"n": int(len(x)), "mean": float(x.mean()), "sd": float(x.std(ddof=1)) if len(x) > 1 else 0.0,
            "p50": float(p50), "p95": float(p95), "p99": float(p99),
            "min": float(x.min()), "max": float(x.max())}


def is_normal(x, alpha: float = ALPHA) -> bool:
    x = np.asarray(x, dtype=float)
    if len(x) < 3 or np.ptp(x) == 0:
        return False
    return bool(st.shapiro(x[:5000]).pvalue > alpha)


def cohens_d(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    pooled = math.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    return float((a.mean() - b.mean()) / pooled) if pooled > 0 else 0.0


def rank_biserial(u1: float, n1: int, n2: int) -> float:
    """Positive when the first group tends to be larger."""
    return float(2 * u1 / (n1 * n2) - 1)


def eta_squared(groups) -> float:
    allx = np.concatenate([np.asarray(g, float) for g in groups])
    grand = allx.mean()
    ss_between = sum(len(g) * (np.mean(g) - grand) ** 2 for g in groups)
    ss_total = ((allx - grand) ** 2).sum()
    return float(ss_between / ss_total) if ss_total > 0 else 0.0


def epsilon_squared(h: float, n: int) -> float:
    return float(h * (n + 1) / (n ** 2 - 1)) if n > 1 else 0.0


def bootstrap_median_diff(a, b, n_boot: int = 2000, seed: int = 0) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    a, b = np.asarray(a, float), np.asarray(b, float)
    ia = rng.integers(0, len(a), (n_boot, len(a)))
    ib = rng.integers(0, len(b), (n_boot, len(b)))
    diffs = np.median(a[ia], axis=1) - np.median(b[ib], axis=1)
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return float(lo), float(hi)


def compare_two(a, b, seed: int = 0) -> dict:
    a, b = np.asarray(a, float), np.asarray(b, float)
    normal = is_normal(a) and is_normal(b)
    if normal:
        r = st.ttest_ind(a, b, equal_var=False)
        test, stat, effect, name = "welch_t", r.statistic, cohens_d(a, b), "cohens_d"
    else:
        r = st.mannwhitneyu(a, b, alternative="two-sided")
        test, stat, effect, name = "mann_whitney_u", r.statistic, rank_biserial(r.statistic, len(a), len(b)), "rank_biserial"
    return {"test": test, "statistic": float(stat), "p": float(r.pvalue), "effect": effect,
            "effect_name": name, "normal": normal, "n": [int(len(a)), int(len(b))],
            "median_a": float(np.median(a)), "median_b": float(np.median(b)),
            "median_diff": float(np.median(a) - np.median(b)),
            "median_diff_ci95": bootstrap_median_diff(a, b, seed=seed)}


def compare_paired(a, b) -> dict:
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = a - b
    normal = is_normal(d)
    if normal:
        r = st.ttest_rel(a, b)
        sd = d.std(ddof=1)
        test, stat, effect, name = "paired_t", r.statistic, float(d.mean() / sd) if sd > 0 else 0.0, "cohens_dz"
    else:
        nz = d[d != 0]
        if len(nz) == 0:
            return {"test": "wilcoxon_signed_rank", "statistic": 0.0, "p": 1.0, "effect": 0.0,
                    "effect_name": "matched_rank_biserial", "normal": False, "n": int(len(d)),
                    "mean_diff": 0.0}
        r = st.wilcoxon(a, b, zero_method="wilcox")
        ranks = st.rankdata(np.abs(nz))
        pos, neg = ranks[nz > 0].sum(), ranks[nz < 0].sum()
        test, stat, effect, name = ("wilcoxon_signed_rank", r.statistic, float((pos - neg) / (pos + neg)),
                                    "matched_rank_biserial")
    return {"test": test, "statistic": float(stat), "p": float(r.pvalue), "effect": effect,
            "effect_name": name, "normal": normal, "n": int(len(d)), "mean_diff": float(d.mean())}


def compare_many(groups: dict) -> dict:
    names = list(groups)
    arrays = [np.asarray(groups[k], float) for k in names]
    normal = all(is_normal(g) for g in arrays)
    n = sum(len(g) for g in arrays)
    if normal:
        r = st.f_oneway(*arrays)
        test, stat, effect, name = "anova", r.statistic, eta_squared(arrays), "eta_squared"
    else:
        r = st.kruskal(*arrays)
        test, stat, effect, name = "kruskal_wallis", r.statistic, epsilon_squared(r.statistic, n), "epsilon_squared"
    return {"test": test, "statistic": float(stat), "p": float(r.pvalue), "effect": effect, "effect_name": name,
            "normal": normal, "groups": names, "n": [int(len(g)) for g in arrays],
            "medians": {k: float(np.median(g)) for k, g in zip(names, arrays, strict=True)}}


def holm(pvals: dict) -> dict:
    """Holm-Bonferroni adjusted p-values (monotone, capped at 1)."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out, running = {}, 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return out


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centre - half), min(1.0, centre + half))


def fisher_2x2(k1: int, n1: int, k2: int, n2: int) -> dict:
    table = [[k1, n1 - k1], [k2, n2 - k2]]
    res = st.fisher_exact(table)
    return {"test": "fisher_exact", "odds_ratio": float(res.statistic), "p": float(res.pvalue),
            "p1": k1 / n1 if n1 else math.nan, "p2": k2 / n2 if n2 else math.nan,
            "risk_difference": (k1 / n1 - k2 / n2) if n1 and n2 else math.nan,
            "ci1": wilson(k1, n1), "ci2": wilson(k2, n2)}
