"""Figures (matplotlib, colour-blind safe Okabe-Ito colours)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import precision_recall_curve  # noqa: E402

COLOURS = {"d1_primary": "#0072B2", "d1_ocsvm": "#56B4E9", "d1_iforest": "#009E73",
           "d2_transfer": "#E69F00", "d3_thresholds": "#D55E00"}
NAMES = {"d1_primary": "D1 primary", "d1_ocsvm": "D1a OC-SVM", "d1_iforest": "D1b IForest",
         "d2_transfer": "D2 transfer", "d3_thresholds": "D3 alarms"}
TAG = " (emulated logs)"

plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 150, "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False, "font.size": 9})


def _save(fig, out: Path, name: str) -> None:
    fig.tight_layout()
    fig.savefig(out / name)
    plt.close(fig)
    print("wrote", out / name)


def fig_f1(summary: pd.DataFrame, out: Path) -> None:
    s = summary.set_index("detector")
    dets = ["d1_ocsvm", "d1_iforest", "d2_transfer", "d3_thresholds"]
    fig, ax = plt.subplots(figsize=(5.8, 3.4))
    f1 = s.loc[dets, "f1"].to_numpy()
    err = np.vstack([f1 - s.loc[dets, "f1_ci_low"].to_numpy(), s.loc[dets, "f1_ci_high"].to_numpy() - f1])
    ax.bar([NAMES[d] for d in dets], f1, yerr=err, capsize=4, color=[COLOURS[d] for d in dets])
    for i, v in enumerate(f1):
        ax.text(i, v + 0.02, f"{v:.2f}", ha="center")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("F1 (phase B windows)")
    ax.set_title("Detection F1 with 95% block-bootstrap CI" + TAG)
    _save(fig, out, "f1_by_detector.png")


def fig_category(cats: pd.DataFrame, out: Path) -> None:
    dets = ["d1_primary", "d2_transfer", "d3_thresholds"]
    categories = list(dict.fromkeys(cats["category"]))
    fig, ax = plt.subplots(figsize=(7, 3.4))
    width = 0.26
    for k, det in enumerate(dets):
        vals = cats[cats["detector"] == det].set_index("category").reindex(categories)["f1"]
        ax.bar(np.arange(len(categories)) + (k - 1) * width, vals, width, label=NAMES[det], color=COLOURS[det])
    ax.set_xticks(range(len(categories)), [c.replace("_", "\n") for c in categories])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("F1 (category windows + all normal windows)")
    ax.set_title("F1 per fault category" + TAG)
    ax.legend(frameon=False, fontsize=8)
    _save(fig, out, "f1_by_category.png")


def fig_pr(B: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(5, 4))
    y = B["label"].astype(int).to_numpy()
    for det in ("d1_ocsvm", "d1_iforest", "d2_transfer"):
        prec, rec, _ = precision_recall_curve(y, B[f"score_{det}"].to_numpy())
        ax.plot(rec, prec, color=COLOURS[det], label=NAMES[det])
        pred = B[f"pred_{det}"].astype(bool).to_numpy()
        tp = (pred & (y == 1)).sum()
        ax.plot(tp / max(1, y.sum()), tp / max(1, pred.sum()), "o", color=COLOURS[det])
    pred = B["pred_d3_thresholds"].astype(bool).to_numpy()
    tp = (pred & (y == 1)).sum()
    ax.plot(tp / max(1, y.sum()), tp / max(1, pred.sum()), "s", color=COLOURS["d3_thresholds"], label=NAMES["d3_thresholds"])
    ax.axhline(y.mean(), color="grey", lw=0.8, ls="--", label="chance (prevalence)")
    ax.set_xlabel("recall")
    ax.set_ylabel("precision")
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.02)
    ax.set_title("Precision-recall, dots = operating points" + TAG)
    ax.legend(frameon=False, fontsize=7, loc="lower left")
    _save(fig, out, "pr_curves.png")


def fig_far(summary: pd.DataFrame, out: Path) -> None:
    s = summary.set_index("detector")
    dets = ["d1_primary", "d2_transfer", "d3_thresholds"]
    fig, ax = plt.subplots(figsize=(5.8, 3.4))
    width = 0.38
    ax.bar(np.arange(3) - width / 2, s.loc[dets, "far_C_no_burst"], width, label="no burst", color="#999999")
    ax.bar(np.arange(3) + width / 2, s.loc[dets, "far_C_burst"], width, label="scale-up burst", color="#CC79A7")
    ax.set_xticks(range(3), [NAMES[d] for d in dets])
    ax.set_ylabel("false-alarm rate (share of windows)")
    ax.set_title("Phase C: false alarms under benign elasticity" + TAG)
    ax.legend(frameon=False)
    _save(fig, out, "elasticity_far.png")


def fig_delay(inj: pd.DataFrame, out: Path) -> None:
    dets = ["d1_primary", "d2_transfer", "d3_thresholds"]
    data = [inj[(inj["detector"] == d) & inj["detected"]]["delay_s"].dropna().to_numpy() for d in dets]
    fig, ax = plt.subplots(figsize=(5.5, 3.4))
    ax.boxplot([d if len(d) else [np.nan] for d in data], showfliers=True)
    ax.set_xticks(range(1, 4), [NAMES[d] for d in dets])
    ax.set_ylabel("detection delay (s)")
    ax.set_title("Delay from injection start to first alarm" + TAG)
    _save(fig, out, "detection_delay.png")


def fig_timeline(B: pd.DataFrame, out: Path, hours: float = 6.0) -> None:
    seed = sorted(B["seed"].unique())[0]
    g = B[B["seed"] == seed].sort_values("start")
    g = g[g["start"] < g["start"].min() + hours * 3600]
    t = (g["start"] - g["start"].min()) / 3600.0
    fig, ax = plt.subplots(figsize=(9, 3.2))
    for det in ("d1_primary", "d2_transfer", "d3_thresholds"):
        flagged = g[f"pred_{det}"].astype(bool).to_numpy()
        offset = {"d1_primary": 2, "d2_transfer": 1, "d3_thresholds": 0}[det]
        ax.scatter(t[flagged], np.full(flagged.sum(), offset), s=8, color=COLOURS[det], label=NAMES[det])
    lab = g["label"].astype(bool).to_numpy()
    for x, is_anom, cat in zip(t, lab, g["category"]):
        if is_anom:
            ax.axvspan(x, x + 1 / 60, color="#F0E442", alpha=0.35, lw=0)
    ax.set_yticks([0, 1, 2], [NAMES["d3_thresholds"], NAMES["d2_transfer"], NAMES["d1_primary"]])
    ax.set_xlabel("hours into phase B (yellow = injected fault)")
    ax.set_title(f"Alarms over the first {hours:.0f} h of phase B, seed {seed}" + TAG)
    _save(fig, out, "timeline_phase_B.png")


def make_all(B, C, summary, cats, inj, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    fig_f1(summary, out)
    fig_category(cats, out)
    fig_pr(B, out)
    fig_far(summary, out)
    fig_delay(inj, out)
    fig_timeline(B, out)
