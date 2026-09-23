"""Pre-registered tests (docs/ANALYSIS_PLAN.md).

Per workload, on the per-batch summaries (n = 30 per configuration):

* normality of the two-way model's residuals (Shapiro-Wilk) decides the method
* normal     -> two-way ANOVA key x capacity **with interaction**, partial eta^2;
               a significant interaction is followed by Tukey HSD across key designs
               inside each capacity mode (simple effects)
* not normal -> Aligned Rank Transform (Wobbrock et al.'s procedure) before the same
               factorial model, epsilon^2 per term
* H_joint    -> bootstrap over batches: how often do the latency-optimal and the
               cost-optimal configuration coincide?
* Holm-Bonferroni across the whole hypothesis family
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats as st
from statsmodels.stats.multicomp import pairwise_tukeyhsd

A, B = "key_design", "capacity_mode"
FORMULA = "y ~ C(key_design) * C(capacity_mode)"
TERMS = {"C(key_design)": "key", "C(capacity_mode)": "capacity", "C(key_design):C(capacity_mode)": "interaction"}


def _fit(df: pd.DataFrame, y: str):
    d = df[[A, B]].assign(y=df[y].astype(float).to_numpy())
    return smf.ols(FORMULA, data=d).fit(), d


def residuals_normal(df: pd.DataFrame, y: str, alpha: float = 0.05) -> tuple[bool, float]:
    model, _ = _fit(df, y)
    r = np.asarray(model.resid)
    if len(r) < 3 or np.ptp(r) == 0:
        return False, float("nan")
    p = float(st.shapiro(r[:5000]).pvalue)
    return p > alpha, p


def anova2(df: pd.DataFrame, y: str) -> dict:
    model, _ = _fit(df, y)
    tab = sm.stats.anova_lm(model, typ=2)
    ss_res = float(tab.loc["Residual", "sum_sq"])
    out = {}
    for term, name in TERMS.items():
        ss = float(tab.loc[term, "sum_sq"])
        out[name] = {"df": float(tab.loc[term, "df"]), "F": float(tab.loc[term, "F"]), "p": float(tab.loc[term, "PR(>F)"]),
                     "partial_eta2": ss / (ss + ss_res) if ss + ss_res > 0 else float("nan")}
    return {"method": "anova2", "terms": out}


def _aligned(df: pd.DataFrame, y: str) -> pd.DataFrame:
    d = df[[A, B]].copy()
    d["y"] = df[y].astype(float).to_numpy()
    grand = d["y"].mean()
    cell = d.groupby([A, B])["y"].transform("mean")
    ma = d.groupby(A)["y"].transform("mean")
    mb = d.groupby(B)["y"].transform("mean")
    resid = d["y"] - cell
    d["key"] = resid + (ma - grand)
    d["capacity"] = resid + (mb - grand)
    d["interaction"] = resid + (cell - ma - mb + grand)
    return d


def art_anova(df: pd.DataFrame, y: str) -> dict:
    """Aligned Rank Transform: align for one effect, rank, full factorial ANOVA, keep that effect only."""
    d = _aligned(df, y)
    out = {}
    for term, name in TERMS.items():
        ranked = d[[A, B]].assign(y=st.rankdata(d[name]))
        model = smf.ols(FORMULA, data=ranked).fit()
        tab = sm.stats.anova_lm(model, typ=2)
        ss, dfe = float(tab.loc[term, "sum_sq"]), float(tab.loc[term, "df"])
        ms_err = float(tab.loc["Residual", "sum_sq"] / tab.loc["Residual", "df"])
        ss_tot = float(tab["sum_sq"].sum())
        out[name] = {"df": dfe, "F": float(tab.loc[term, "F"]), "p": float(tab.loc[term, "PR(>F)"]),
                     "epsilon2": (ss - dfe * ms_err) / (ss_tot + ms_err) if ss_tot + ms_err > 0 else float("nan")}
    return {"method": "art", "terms": out}


def factorial(df: pd.DataFrame, y: str, alpha: float = 0.05) -> dict:
    """Pick ANOVA or ART from the residual normality check; handle a DV with no variance."""
    if df[y].astype(float).nunique() <= 1:
        return {"method": "no_variance", "value": float(df[y].iloc[0]) if len(df) else float("nan"),
                "terms": {n: {"p": 1.0, "note": "every batch has the same value - not testable"} for n in TERMS.values()}}
    normal, p_sw = residuals_normal(df, y, alpha)
    res = anova2(df, y) if normal else art_anova(df, y)
    res["shapiro_p"] = p_sw
    if res["terms"]["interaction"]["p"] < alpha:
        res["simple_effects"] = tukey_simple_effects(df, y, alpha)
    return res


def tukey_simple_effects(df: pd.DataFrame, y: str, alpha: float = 0.05) -> list[dict]:
    rows = []
    for mode, g in df.groupby(B):
        t = pairwise_tukeyhsd(g[y].astype(float), g[A], alpha=alpha)
        for r in t.summary().data[1:]:
            rows.append({"capacity_mode": mode, "a": r[0], "b": r[1], "mean_diff": float(r[2]),
                         "p_adj": float(r[3]), "reject": bool(r[6])})
    return rows


def holm(pvals: dict) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m, out, running = len(items), {}, 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return out


def joint_divergence(df: pd.DataFrame, lat: str, cost: str, n_boot: int = 2000, seed: int = 0) -> dict:
    """H_joint: share of bootstrap resamples in which one configuration is best on both.

    p = that share. Small p -> the latency-optimal and cost-optimal choices diverge.
    """
    rng = np.random.default_rng(seed)
    groups = {cfg: g for cfg, g in df.groupby("configuration")}
    names = sorted(groups)
    lat_obs = {c: float(groups[c][lat].mean()) for c in names}
    cost_obs = {c: float(groups[c][cost].mean()) for c in names}
    best_lat, best_cost = min(lat_obs, key=lat_obs.get), min(cost_obs, key=cost_obs.get)
    same = 0
    for _ in range(n_boot):
        ml, mc = {}, {}
        for c in names:
            g = groups[c]
            idx = rng.integers(0, len(g), len(g))
            ml[c] = g[lat].to_numpy()[idx].mean()
            mc[c] = g[cost].to_numpy()[idx].mean()
        same += min(ml, key=ml.get) == min(mc, key=mc.get)
    return {"test": "bootstrap_argmin", "latency_optimal": best_lat, "cost_optimal": best_cost,
            "coincide_observed": best_lat == best_cost, "p": same / n_boot, "n_boot": n_boot}
