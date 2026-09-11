"""Paired statistics for the detector comparison.

The detectors see *identical* windows, so observations are paired (by block):

* two detectors  -> Shapiro-Wilk on the differences; normal -> paired t-test +
  Cohen's d_z, otherwise Wilcoxon signed-rank + matched-pairs rank-biserial r
* 3+ conditions  -> Friedman test + Kendall's W
* injection level detected/missed for two detectors -> McNemar (exact below 25
  discordant pairs)
* 95 % CIs by bootstrap; Holm-Bonferroni over the hypothesis family
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats


def bootstrap_ci(values, level: float = 0.95, n: int = 5000, seed: int = 1, stat=np.mean) -> tuple[float, float]:
    arr = np.asarray([v for v in values if not (isinstance(v, float) and math.isnan(v))], dtype=float)
    if arr.size == 0:
        return (math.nan, math.nan)
    if arr.size == 1 or np.all(arr == arr[0]):
        return (float(arr[0]), float(arr[0]))
    rng = np.random.default_rng(seed)
    boots = np.array([stat(rng.choice(arr, size=arr.size, replace=True)) for _ in range(n)])
    lo, hi = np.percentile(boots, [(1 - level) / 2 * 100, (1 + level) / 2 * 100])
    return (float(lo), float(hi))


def paired_test(a, b, alpha: float = 0.05) -> dict:
    """Two-sided paired comparison of a vs b (e.g. F1 per block of two detectors)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    d = a - b
    out = {"n": int(d.size), "mean_a": float(a.mean()), "mean_b": float(b.mean()),
           "mean_diff": float(d.mean()), "diff_ci95": list(bootstrap_ci(d))}
    if d.size < 2 or np.all(d == d[0]):
        return {**out, "test": "none (no variance in the differences)", "statistic": 0.0,
                "p": 1.0 if np.all(d == 0) else 0.0, "effect": "none", "effect_size": 0.0,
                "normality_p": None}
    norm_p = float(stats.shapiro(d).pvalue) if d.size >= 3 else None
    if norm_p is not None and norm_p >= alpha:
        res = stats.ttest_rel(a, b)
        sd = d.std(ddof=1)
        return {**out, "test": "paired t-test", "statistic": float(res.statistic), "p": float(res.pvalue),
                "effect": "cohens_dz", "effect_size": float(d.mean() / sd) if sd else 0.0, "normality_p": norm_p}
    res = stats.wilcoxon(a, b, zero_method="wilcox", alternative="two-sided")
    nz = d[d != 0]
    ranks = stats.rankdata(np.abs(nz))
    w_plus, w_minus = ranks[nz > 0].sum(), ranks[nz < 0].sum()
    r = float((w_plus - w_minus) / (w_plus + w_minus)) if (w_plus + w_minus) else 0.0
    return {**out, "test": "Wilcoxon signed-rank", "statistic": float(res.statistic), "p": float(res.pvalue),
            "effect": "rank_biserial", "effect_size": r, "normality_p": norm_p}


def friedman(matrix) -> dict:
    """Rows = blocks (paired), columns = conditions."""
    m = np.asarray(matrix, dtype=float)
    m = m[~np.isnan(m).any(axis=1)]
    n, k = m.shape if m.ndim == 2 else (0, 0)
    base = {"n_blocks": int(n), "k": int(k), "column_means": [float(x) for x in m.mean(axis=0)] if n else []}
    if n < 2 or k < 2 or np.all(m == m.flat[0]) or np.all(m == m[:, :1]):
        return {**base, "test": "none (no variance between conditions)", "statistic": 0.0, "p": 1.0,
                "effect": "kendalls_w", "effect_size": 0.0}
    res = stats.friedmanchisquare(*[m[:, j] for j in range(k)])
    w = float(res.statistic / (n * (k - 1)))
    return {**base, "test": "Friedman", "statistic": float(res.statistic), "p": float(res.pvalue),
            "effect": "kendalls_w", "effect_size": min(1.0, w)}


def mcnemar(a, b) -> dict:
    """a, b = detected (bool) for the same injections by two detectors."""
    a = np.asarray(a, dtype=bool)
    b = np.asarray(b, dtype=bool)
    b01 = int((~a & b).sum())
    b10 = int((a & ~b).sum())
    n = b01 + b10
    if n == 0:
        return {"b01": b01, "b10": b10, "test": "McNemar", "statistic": 0.0, "p": 1.0, "exact": True}
    if n < 25:
        p = float(stats.binomtest(min(b01, b10), n, 0.5).pvalue)
        return {"b01": b01, "b10": b10, "test": "McNemar (exact)", "statistic": float(min(b01, b10)), "p": p, "exact": True}
    chi2 = (abs(b01 - b10) - 1) ** 2 / n
    return {"b01": b01, "b10": b10, "test": "McNemar (chi2, continuity)", "statistic": float(chi2),
            "p": float(stats.chi2.sf(chi2, 1)), "exact": False}


def holm(pvalues: dict[str, float]) -> dict[str, float]:
    items = sorted(pvalues.items(), key=lambda kv: kv[1])
    m = len(items)
    out, running = {}, 0.0
    for i, (name, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[name] = running
    return out


def paired_power_n(sd_diff: float, mde: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """Pairs needed to see a mean paired difference of ``mde`` (normal approximation)."""
    if sd_diff <= 0:
        return 2
    z = stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)
    return int(math.ceil((z * sd_diff / mde) ** 2))
