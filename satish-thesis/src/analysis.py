"""Tables, statistics and figures from results/ (run after experiment.py).

    python src/analysis.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES, FIG, TAB = ROOT / "results", ROOT / "figures", ROOT / "results" / "tables"
RATES = [0.0, 0.1, 0.2, 0.3, 0.4]
COLORS = {"PI-GRU": "#2a78d6", "GRU-aux": "#eb6834", "GRU": "#1baf7a", "LSTM": "#eda100", "XGBoost": "#e87ba4",
          "BNN": "#008300", "BNN-paper": "#4a3aa7", "Profile": "#e34948", "Persistence": "#e34948",
          "PI-GRU-nomask": "#8a8984", "Seasonal": "#8a8984"}
MARKERS = {"PI-GRU": "o", "GRU-aux": "s", "GRU": "^", "LSTM": "v", "XGBoost": "D", "BNN": "P", "BNN-paper": "X",
           "Profile": "*", "Persistence": "*", "PI-GRU-nomask": "h", "Seasonal": "p"}
CONVENTIONAL = ["XGBoost", "LSTM", "GRU", "BNN", "BNN-paper", "Profile", "Persistence", "Seasonal"]
PUBLISHED = pd.DataFrame([  # Mahajan et al. (2024), Table 11, HVAC, complete 6-month test set
    {"model": "QRF (published)", "MAE": 17.17, "RMSE": 21.67, "MAPE": 0.40},
    {"model": "MC-LSTM (published)", "MAE": 8.21, "RMSE": 11.86, "MAPE": 0.45},
    {"model": "BNN (published)", "MAE": 7.06, "RMSE": 9.65, "MAPE": 0.35}])
plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 200, "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.6,
                     "axes.edgecolor": "#8a8984", "axes.labelcolor": "#0b0b0b", "legend.frameon": False,
                     "lines.linewidth": 2, "lines.markersize": 5})


def load(task):
    m = pd.concat([pd.read_csv(RES / f"metrics_{task}_{f}.csv") for f in ("tree", "nn")], ignore_index=True)
    p = dict(np.load(RES / f"predictions_{task}_tree.npz"))
    p.update(np.load(RES / f"predictions_{task}_nn.npz"))
    return m, p


def fmt(mean, sd, nd=2):
    return f"{mean:.{nd}f} ± {sd:.{nd}f}"


def summary(m, cols=("MAE", "RMSE", "MAPE", "R2")):
    g = m.groupby("model")[list(cols)]
    return g.mean().join(g.std().fillna(0), rsuffix="_sd")


def to_latex(df, path, caption, label):
    body = df.to_latex(index=False, escape=False, column_format="l" + "r" * (df.shape[1] - 1))
    body = body.replace("±", r"$\pm$").replace("%", r"\%")
    path.write_text(f"\\begin{{table}}[H]\n\\centering\\small\n\\caption{{{caption}}}\\label{{{label}}}\n{body}\\end{{table}}\n", encoding="utf-8")


def day_ids(p):
    return pd.to_datetime(p["t"]).floor("D").to_numpy()


def paired_bootstrap(p, a, b, pattern, rate, seeds, B=2000, rng=np.random.default_rng(0)):
    """Day-block bootstrap of RMSE(a) - RMSE(b), seed-averaged squared errors; Wilcoxon on daily MSE."""
    y, days = p["y"], day_ids(p)
    se = lambda name: np.mean([(p[f"{name}|{s}|{pattern}|{rate}"] - y) ** 2 for s in seeds], axis=0)
    da = pd.Series(se(a)).groupby(days).agg(["sum", "count"])
    db = pd.Series(se(b)).groupby(days).agg(["sum", "count"])
    n = len(da)
    idx = rng.integers(0, n, (B, n))
    cnt = da["count"].to_numpy()[idx].sum(1)
    diff = np.sqrt(da["sum"].to_numpy()[idx].sum(1) / cnt) - np.sqrt(db["sum"].to_numpy()[idx].sum(1) / cnt)
    obs = np.sqrt(da["sum"].sum() / da["count"].sum()) - np.sqrt(db["sum"].sum() / db["count"].sum())
    ref = np.sqrt(db["sum"].sum() / db["count"].sum())
    w = stats.wilcoxon(da["sum"] / da["count"], db["sum"] / db["count"])
    return {"dRMSE": obs, "dRMSE_pct": obs / ref * 100, "ci_lo": np.percentile(diff, 2.5),
            "ci_hi": np.percentile(diff, 97.5), "wilcoxon_p": w.pvalue}


def holm(pvals):
    order = np.argsort(pvals)
    adj, run = np.empty(len(pvals)), 0.0
    for rank, i in enumerate(order):
        run = max(run, (len(pvals) - rank) * pvals[i])
        adj[i] = min(1.0, run)
    return adj


# ----------------------------------------------------------------------------- tables
def baseline_table(m):
    clean = m[m.rate == 0]
    s = summary(clean)
    rows = [{"model": name, "MAE": fmt(r.MAE, r.MAE_sd), "RMSE": fmt(r.RMSE, r.RMSE_sd),
             "MAPE": fmt(r.MAPE, r.MAPE_sd, 3), "R2": fmt(r.R2, r.R2_sd, 3)} for name, r in s.sort_values("RMSE").iterrows()]
    ours = pd.DataFrame(rows)
    pub = PUBLISHED.assign(MAE=PUBLISHED.MAE.map("{:.2f}".format), RMSE=PUBLISHED.RMSE.map("{:.2f}".format),
                           MAPE=PUBLISHED.MAPE.map("{:.2f}".format), R2="--")
    t = pd.concat([pub, ours], ignore_index=True)
    t.to_csv(TAB / "baseline_comparison.csv", index=False)
    to_latex(t, TAB / "baseline_comparison.tex",
             "Complete-data test accuracy (Jul--Dec 2020, hourly HVAC kWh). Published rows are from "
             "\\citet{mahajan2024bnn}; our rows are mean $\\pm$ s.d. over five seeds.", "tab:baseline")
    return s


def robustness_table(m, task):
    s = m.groupby(["model", "pattern", "rate"])["RMSE"].agg(["mean", "std"]).reset_index()
    clean = s[s.rate == 0].set_index("model")["mean"]
    out = []
    for model, g in s.groupby("model"):
        row = {"model": model, "complete": fmt(clean[model], g[g.rate == 0]["std"].iloc[0])}
        for pat in ("mcar", "block"):
            for r in RATES[1:]:
                v = g[(g.pattern == pat) & (g.rate == r)]
                row[f"{pat} {int(r * 100)}%"] = f"{v['mean'].iloc[0]:.2f}"
        row["mcar slope"] = slope(m[m.model == model], "mcar")
        row["block slope"] = slope(m[m.model == model], "block")
        out.append(row)
    t = pd.DataFrame(out).sort_values("complete")
    t.to_csv(TAB / f"robustness_{task}.csv", index=False)
    to_latex(t.drop(columns=[c for c in t.columns if c.startswith("mcar ") and c[5:7] in ("10", "30")] +
                    [c for c in t.columns if c.startswith("block ") and c[6:8] in ("10", "30")]),
             TAB / f"robustness_{task}.tex",
             f"Test RMSE (kWh) under controlled sensor loss, {task} task, mean of five seeds. Slope: RMSE "
             "increase per 10 percentage points of missing readings (mean $\\pm$ s.d. over seeds).",
             f"tab:robust_{task}")
    return t


def slope(mm, pattern):
    vals = []
    for seed, g in mm.groupby("seed"):
        x = [0.0] + RATES[1:]
        y = [g[(g.rate == 0)]["RMSE"].iloc[0]] + [g[(g.pattern == pattern) & (g.rate == r)]["RMSE"].iloc[0] for r in RATES[1:]]
        vals.append(np.polyfit(x, y, 1)[0] / 10)
    return fmt(np.mean(vals), np.std(vals, ddof=1) if len(vals) > 1 else 0.0, 3)


def significance(m, p, task, target="PI-GRU"):
    seeds = sorted(m.seed.unique())
    rows = []
    conds = [("none", 0.0)] + [(pat, r) for pat in ("mcar", "block") for r in RATES[1:]]
    if task == "forecast":
        conds += [("block_meter", 0.2), ("block_meter", 0.4)]
    for pat, r in conds:
        cur = m[(m.pattern == pat) & (m.rate == r)].groupby("model")["RMSE"].mean()
        best = cur[[c for c in CONVENTIONAL if c in cur.index]].idxmin()
        for ref in (best, "GRU-aux"):
            res = paired_bootstrap(p, target, ref, pat, r, seeds)
            rows.append({"pattern": pat, "rate": r, "reference": ref, **res})
    t = pd.DataFrame(rows)
    t["p_holm"] = holm(t["wilcoxon_p"].to_numpy())
    t.to_csv(TAB / f"significance_{task}.csv", index=False)
    show = t.assign(condition=t.pattern + " " + (t.rate * 100).astype(int).astype(str) + "%",
                    **{"$\\Delta$RMSE": t.dRMSE.map("{:+.2f}".format), "$\\Delta$%": t.dRMSE_pct.map("{:+.1f}".format),
                       "95% CI": [f"[{a:+.2f}, {b:+.2f}]" for a, b in zip(t.ci_lo, t.ci_hi)],
                       "$p_{Holm}$": t.p_holm.map(lambda v: f"{v:.3g}")})
    to_latex(show[["condition", "reference", "$\\Delta$RMSE", "$\\Delta$%", "95% CI", "$p_{Holm}$"]],
             TAB / f"significance_{task}.tex",
             f"PI-GRU minus reference, {task} task. Negative values favour PI-GRU. CI: day-block bootstrap "
             "(2,000 resamples) on seed-averaged errors; $p$: Wilcoxon signed-rank on daily MSE, Holm-adjusted.",
             f"tab:sig_{task}")
    return t


def strata_table(m, p, task, models):
    y = p["y"]
    hour, dow, tout = p["local_hour"], p["local_dow"], p["drv"][:, 0]
    occ = (hour >= 7) & (hour < 19) & (dow < 5)
    lo, hi = np.nanpercentile(tout, [10, 90])
    groups = {"occupied": occ, "unoccupied": ~occ, "mild T_out": (tout > lo) & (tout < hi),
              "extreme T_out": (tout <= lo) | (tout >= hi)}
    seeds = sorted(m.seed.unique())
    rows = []
    for name in models:
        for cond in (("none", 0.0), ("block", 0.4)):
            row = {"model": name, "condition": f"{cond[0]} {int(cond[1] * 100)}%"}
            for g, mask in groups.items():
                row[g] = np.mean([np.sqrt(np.mean((p[f"{name}|{s}|{cond[0]}|{cond[1]}"][mask] - y[mask]) ** 2)) for s in seeds])
            rows.append(row)
    t = pd.DataFrame(rows).round(2)
    t.to_csv(TAB / f"strata_{task}.csv", index=False)
    to_latex(t, TAB / f"strata_{task}.tex", f"Test RMSE (kWh) by operating stratum, {task} task, mean of five seeds.",
             f"tab:strata_{task}")
    return t


def physics_tables(task):
    c = pd.read_csv(RES / f"physics_coefs_{task}_nn.csv")
    cols = ["tau_h", "b_eta_over_C", "c_beta_over_C", "d_gamma_over_C", "e_offset"]
    g = c.groupby("model")[cols]
    t = pd.DataFrame({k: [fmt(a, b, 4) for a, b in zip(g.mean()[k], g.std()[k])] for k in cols}, index=g.mean().index)
    t["tau_h"] = [fmt(a, b, 1) for a, b in zip(g.mean()["tau_h"], g.std()["tau_h"])]
    ref = json.loads((RES / f"ref_rc_{task}.json").read_text(encoding="utf-8"))
    tau_ref = f"{1 / ref['a']:.1f}" if ref["a"] > 0 else f"n.i. ($a$={ref['a']:.1e})"
    t.loc["Least-squares RC (train)"] = [tau_ref, f"{ref['b']:.4f}", f"{ref['c']:.4f}", f"{ref['d']:.4f}",
                                         f"{ref['e']:.4f}"]
    t = t.reset_index().rename(columns={"index": "model", "tau_h": "$\\tau$ (h)", "b_eta_over_C": "$b$",
                                        "c_beta_over_C": "$c$", "d_gamma_over_C": "$d$", "e_offset": "$e$"})
    t.to_csv(TAB / f"physics_coefs_{task}.csv", index=False)
    to_latex(t, TAB / f"physics_coefs_{task}.tex",
             f"Learned RC coefficients ({task} task, mean $\\pm$ s.d. over five seeds) against a least-squares fit "
             "on clean training data.", f"tab:coef_{task}")
    return t


def plausibility_table(m, task):
    pl = pd.concat([pd.read_csv(RES / f"plausibility_{task}_{f}.csv") for f in ("tree", "nn")])
    g = pl.groupby("model")
    t = pd.DataFrame({"$\\partial E/\\partial T_{out}$ (kWh/K)": [fmt(a, b) for a, b in zip(g.mean()["cooling_mean_dE"], g.std()["cooling_mean_dE"])],
                      "implausible (%)": [fmt(a, b, 1) for a, b in zip(g.mean()["implausible_pct"], g.std()["implausible_pct"])]},
                     index=g.mean().index)
    dual = m[m.rate.isin([0.0, 0.4]) & m.rc_residual.notna()]
    for (name, pat, r), v in dual.groupby(["model", "pattern", "rate"])["rc_residual"]:
        t.loc[name, f"RC residual {pat} {int(r * 100)}%"] = f"{v.mean():.3f}"
    t = t.fillna("--").reset_index().rename(columns={"index": "model"})
    t.to_csv(TAB / f"physics_consistency_{task}.csv", index=False)
    to_latex(t, TAB / f"physics_consistency_{task}.tex",
             f"Physical consistency, {task} task. Response of predicted HVAC energy to +1\\,K outdoor temperature in "
             "cooling hours, share of cooling hours where the response is negative, and RMS residual (K/h) of the "
             "least-squares RC balance for dual-head models.", f"tab:phys_{task}")
    return t


def cost_table(task):
    c = pd.concat([pd.read_csv(RES / f"cost_{task}_{f}.csv") for f in ("tree", "nn")])
    g = c.groupby("model")
    t = pd.DataFrame({"train (s)": [fmt(a, b, 1) for a, b in zip(g.mean()["train_s"], g.std()["train_s"])],
                      "epochs / trees": [f"{v:.0f}" for v in g.mean()["epochs_or_trees"]],
                      "inference ($\\mu$s/sample)": [f"{v:.1f}" for v in g.mean()["infer_us_per_sample"]]},
                     index=g.mean().index).reset_index().rename(columns={"index": "model"})
    t.to_csv(TAB / f"cost_{task}.csv", index=False)
    to_latex(t, TAB / f"cost_{task}.tex", f"Computational cost, {task} task (mean over seeds).", f"tab:cost_{task}")
    return t


def imputation_table():
    parts = [pd.read_csv(f) for f in (RES / f"imputation_estimate_{k}.csv" for k in ("tree", "nn")) if f.exists()]
    main = pd.concat([pd.read_csv(RES / f"metrics_estimate_{f}.csv") for f in ("tree", "nn")])
    main = main[main.model.isin(["XGBoost", "GRU-aux", "PI-GRU"]) & main.seed.isin([0, 1, 2])].assign(imputer="locf")
    d = pd.concat(parts + [main])
    d = d[d.pattern.isin(["none", "mcar", "block"]) & d.rate.isin([0.0, 0.2, 0.4])]
    d["condition"] = d.pattern + " " + (d.rate * 100).astype(int).astype(str) + "%"
    t = d.pivot_table(index=["model", "imputer"], columns="condition", values="RMSE").round(2).reset_index()
    t.to_csv(TAB / "imputation_sensitivity.csv", index=False)
    to_latex(t, TAB / "imputation_sensitivity.tex",
             "Test RMSE (kWh) by imputation method, estimation task, mean of three seeds.", "tab:imputation")
    return t


def tuning_table(task):
    t = pd.concat([pd.read_csv(RES / f"tuning_{task}_{f}.csv") for f in ("tree", "nn")])
    t.to_csv(TAB / f"tuning_{task}.csv", index=False)
    return t


def data_tables():
    d = pd.read_csv(RES / "data_dictionary.csv")
    d = d[~d.column.isin(["natural_gap", "valid", "local_month"])]
    d = d.assign(column=d.column.str.replace("_", r"\_", regex=False), source=d.source.str.replace("_", r"\_", regex=False))
    to_latex(d[["column", "unit", "source", "description"]], TAB / "data_dictionary.tex",
             "Hourly variables used in this study.", "tab:dict")
    prof = json.loads((RES / "data_profile.json").read_text(encoding="utf-8"))
    g = pd.DataFrame({"channel": list(prof["raw_missing_pct"]),
                      "natural gaps (%)": [f"{v:.2f}" for v in prof["raw_missing_pct"].values()],
                      "after short-gap filling (%)": [f"{v:.2f}" for v in prof["missing_after_fill_pct"].values()],
                      "correlation with HVAC": [f"{prof['corr_with_hvac'][k]:.2f}" for k in prof["raw_missing_pct"]]})
    g["channel"] = g.channel.str.replace("_", r"\_", regex=False)
    to_latex(g, TAB / "natural_gaps.tex", f"Natural gaps and correlation with HVAC energy, {prof['start'][:10]} to "
             f"{prof['end'][:10]} ({prof['rows']:,} hours).", "tab:gaps")


# ----------------------------------------------------------------------------- figures
def fig_data():
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from experiment import load_hourly
    df = load_hourly()
    d = df[["hvac_kwh", "t_out", "t_in"]].resample("1D").mean()
    fig, ax = plt.subplots(2, 1, figsize=(7.2, 3.8), sharex=True)
    ax[0].plot(d.index, d.hvac_kwh, color="#2a78d6", lw=1.2)
    ax[0].set_ylabel("HVAC (kWh/h)")
    ax[1].plot(d.index, d.t_out, color="#eb6834", lw=1.2, label="outdoor")
    ax[1].plot(d.index, d.t_in, color="#1baf7a", lw=1.2, label="indoor (median)")
    ax[1].set_ylabel("Temperature (°C)")
    ax[1].legend(loc="upper left", ncol=2)
    for a in ax:
        for (s, e), lab in zip([("2018-03-01", "2020-03-31"), ("2020-04-01", "2020-06-30"), ("2020-07-01", "2020-12-31")],
                               ["train", "validation", "test"]):
            a.axvspan(pd.Timestamp(s), pd.Timestamp(e), color={"train": "#f4f3ef", "validation": "#e9f1fb", "test": "#fbece5"}[lab], zorder=0)
    for (s, lab) in [("2019-01-01", "train"), ("2020-04-05", "val"), ("2020-08-15", "test")]:
        ax[0].text(pd.Timestamp(s), ax[0].get_ylim()[1] * 0.92, lab, color="#52514e")
    fig.tight_layout()
    fig.savefig(FIG / "data_overview.png")
    plt.close(fig)


def fig_masks():
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from masking import SENSORS, make_keep
    obs = np.ones((24 * 14, 9), bool)
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.4), sharey=True)
    for a, pat in zip(ax, ("mcar", "block")):
        k = make_keep(obs, pat, 0.3, 7)[:, :8]
        a.imshow(~k.T, aspect="auto", cmap=matplotlib.colors.ListedColormap(["#f4f3ef", "#2a78d6"]), interpolation="nearest")
        a.set_title(f"{pat.upper()} 30%", fontsize=9)
        a.set_xlabel("hour")
        a.grid(False)
    ax[0].set_yticks(range(8), SENSORS)
    fig.tight_layout()
    fig.savefig(FIG / "mask_examples.png")
    plt.close(fig)


def fig_robustness(m, task, models):
    pats = ["mcar", "block"] + (["block_meter"] if task == "forecast" else [])
    fig, ax = plt.subplots(1, len(pats), figsize=(3.6 * len(pats), 3.0), sharey=True)
    for a, pat in zip(np.atleast_1d(ax), pats):
        for name in models:
            g = m[m.model == name]
            rs = RATES if pat != "block_meter" else [0.0, 0.2, 0.4]
            mean = [g[(g.rate == 0)]["RMSE"].mean()] + [g[(g.pattern == pat) & (g.rate == r)]["RMSE"].mean() for r in rs[1:]]
            sd = [g[(g.rate == 0)]["RMSE"].std()] + [g[(g.pattern == pat) & (g.rate == r)]["RMSE"].std() for r in rs[1:]]
            x = np.array(rs) * 100
            a.plot(x, mean, color=COLORS[name], marker=MARKERS[name], label=name,
                   ls="--" if name in ("PI-GRU-nomask", "Seasonal") else "-")
            if name in ("PI-GRU", "XGBoost"):
                a.fill_between(x, np.array(mean) - sd, np.array(mean) + sd, color=COLORS[name], alpha=0.15, lw=0)
        a.set_title({"mcar": "Random point loss (MCAR)", "block": "Contiguous outages", "block_meter": "Outages incl. meter"}[pat])
        a.set_xlabel("readings removed (%)")
    np.atleast_1d(ax)[0].set_ylabel("test RMSE (kWh)")
    h, lab = np.atleast_1d(ax)[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=min(len(models), 5), bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    fig.savefig(FIG / f"robustness_{task}.png", bbox_inches="tight")
    plt.close(fig)


def fig_baseline(s):
    pub = PUBLISHED.set_index("model")
    names = list(pub.index) + list(s.sort_values("RMSE").index)
    vals = list(pub.RMSE) + list(s.sort_values("RMSE").RMSE)
    errs = [0, 0, 0] + list(s.sort_values("RMSE").RMSE_sd)
    col = ["#c3c2b7"] * 3 + [COLORS.get(n, "#8a8984") for n in names[3:]]
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    y = np.arange(len(names))[::-1]
    ax.barh(y, vals, xerr=errs, color=col, height=0.6, error_kw={"lw": 1, "ecolor": "#52514e"})
    for yi, v, e in zip(y, vals, errs):
        ax.text(v + e + 0.3, yi, f"{v:.2f}", va="center", fontsize=8, color="#0b0b0b")
    ax.set_yticks(y, names)
    ax.set_xlabel("test RMSE (kWh), complete data, Jul-Dec 2020")
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    fig.savefig(FIG / "baseline_comparison.png")
    plt.close(fig)


def fig_degradation(m, task, models):
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    width = 0.8 / len(models)
    x = np.arange(4)
    for i, name in enumerate(models):
        g = m[m.model == name]
        base = g[g.rate == 0]["RMSE"].mean()
        vals = [(g[(g.pattern == "block") & (g.rate == r)]["RMSE"].mean() / base - 1) * 100 for r in RATES[1:]]
        ax.bar(x + i * width, vals, width * 0.9, color=COLORS[name], label=name)
    ax.set_xticks(x + 0.4 - width / 2, [f"{int(r * 100)}%" for r in RATES[1:]])
    ax.set_xlabel("readings removed by contiguous outages")
    ax.set_ylabel("RMSE increase vs complete (%)")
    ax.axhline(0, color="#8a8984", lw=0.8)
    ax.legend(ncol=4, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / f"degradation_{task}.png")
    plt.close(fig)


def fig_lambda(task):
    t = pd.read_csv(RES / f"tuning_{task}_nn.csv")
    pi = t[t.model == "PI-GRU"].sort_values("lambda")
    base = t[t.model == "GRU-aux"]["val_rmse"].min()
    fig, ax = plt.subplots(figsize=(3.6, 2.8))
    ax.semilogx(pi["lambda"], pi["val_rmse"], color="#2a78d6", marker="o", label="PI-GRU")
    ax.axhline(base, color="#eb6834", ls="--", lw=1.5, label="GRU-aux ($\\lambda$=0)")
    ax.set_xlabel("physics weight $\\lambda$")
    ax.set_ylabel("validation RMSE (kWh)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / f"lambda_sensitivity_{task}.png")
    plt.close(fig)


def fig_trace(p, task, models):
    y, t = p["y"], pd.to_datetime(p["t"])
    start = np.searchsorted(t, pd.Timestamp("2020-08-10"))
    sl = slice(start, start + 24 * 7)
    fig, ax = plt.subplots(2, 1, figsize=(7.2, 4.2), sharex=True, sharey=True)
    for a, cond in zip(ax, (("none", 0.0), ("block", 0.4))):
        a.plot(t[sl], y[sl], color="#0b0b0b", lw=1.4, label="measured")
        for name in models:
            a.plot(t[sl], p[f"{name}|0|{cond[0]}|{cond[1]}"][sl], color=COLORS[name], lw=1.2, label=name)
        a.set_title("complete sensors" if cond[1] == 0 else "40% of readings lost to contiguous outages", fontsize=9)
        a.set_ylabel("HVAC (kWh)")
    ax[0].legend(ncol=len(models) + 1, fontsize=8, loc="upper left")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(FIG / f"trace_{task}.png")
    plt.close(fig)


def fig_coefs(task):
    c = pd.read_csv(RES / f"physics_coefs_{task}_nn.csv")
    ref = json.loads((RES / f"ref_rc_{task}.json").read_text(encoding="utf-8"))
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.6))
    for a, (col, lab, refv) in zip(ax, [("tau_h", "time constant $\\tau$ (h)", 1 / ref["a"]),
                                        ("b_eta_over_C", "HVAC gain $b$ (K per kWh)", ref["b"])]):
        for i, name in enumerate(["PI-GRU", "PI-GRU-nomask"]):
            v = c[c.model == name][col]
            a.scatter(np.full(len(v), i) + np.linspace(-0.08, 0.08, len(v)), v, color=COLORS[name], s=30, zorder=3)
        if refv > 0 and col != "tau_h" or ref["a"] > 0:
            a.axhline(refv, color="#8a8984", ls="--", lw=1.2, label="least-squares RC")
        a.set_xticks([0, 1], ["PI-GRU", "PI-GRU-nomask"])
        a.set_xlim(-0.5, 1.5)
        a.set_ylabel(lab)
        if a.get_legend_handles_labels()[0]:
            a.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / f"physics_coefs_{task}.png")
    plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)
    fig_data()
    fig_masks()
    data_tables()
    key = {}
    for task in ("estimate", "forecast"):
        if not (RES / f"metrics_{task}_nn.csv").exists():
            continue
        m, p = load(task)
        s = baseline_table(m) if task == "estimate" else summary(m[m.rate == 0])
        if task == "estimate":
            fig_baseline(s)
            imputation_table()
        order = [n for n in COLORS if n in set(m.model)]
        main_models = [n for n in order if n not in ("PI-GRU-nomask", "Seasonal")]
        robustness_table(m, task)
        sig = significance(m, p, task)
        strata_table(m, p, task, [n for n in ("PI-GRU", "GRU-aux", "XGBoost", "BNN-paper", "Persistence") if n in set(m.model)])
        physics_tables(task)
        plausibility_table(m, task)
        cost_table(task)
        tuning_table(task)
        fig_robustness(m, task, order)
        fig_degradation(m, task, [n for n in main_models if n not in ("Profile", "Persistence")])
        fig_lambda(task)
        fig_trace(p, task, [n for n in ("PI-GRU", "XGBoost", "BNN-paper") if n in set(m.model)])
        fig_coefs(task)
        key[task] = {"complete_RMSE": s["RMSE"].round(3).to_dict(), "significance": sig.round(4).to_dict("records")}
    (RES / "summary.json").write_text(json.dumps(key, indent=2, default=float), encoding="utf-8")
    print(json.dumps({t: v["complete_RMSE"] for t, v in key.items()}, indent=1))


if __name__ == "__main__":
    main()
