"""Full experiment for Yashwanth's thesis, in one command.

Credit card fraud detection on the Kaggle ULB dataset with Logistic Regression,
Decision Tree and Random Forest.  Everything reported in the dissertation comes
from the CSV/JSON files this script writes to results/tables and the figures in
results/figures.

    python src/pipeline.py            # from the project folder

Design choices (see dissertation, Section 3):
- exact duplicate rows are removed BEFORE splitting, so no test row also sits in training;
- one stratified 70/30 split with a fixed seed is used for every model;
- scaling and SMOTE are fitted on training data only (inside an imblearn Pipeline);
- tuning uses stratified 3-fold CV on the training split, scored by PR-AUC;
- the decision threshold is chosen on a validation slice of the training split, never on test.
"""
import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from scipy.stats import chi2
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, confusion_matrix, f1_score,
                             matthews_corrcoef, precision_recall_curve, precision_score, recall_score,
                             roc_auc_score, roc_curve)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "creditcard.csv"
TAB = ROOT / "results" / "tables"
FIG = ROOT / "results" / "figures"
PCA = [f"V{i}" for i in range(1, 29)]
COLORS = {"Logistic Regression": "#4C72B0", "Decision Tree": "#DD8452", "Random Forest": "#55A868"}


# ---------------------------------------------------------------- data
def load():
    df = pd.read_csv(DATA)
    n_raw = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    df["Hour"] = (df["Time"] // 3600) % 24
    return df, n_raw


def features(with_hour=True):
    return PCA + ["Amount", "Time"] + (["Hour"] if with_hour else [])


def make(model, sampler=None, cols=None):
    cols = cols or features()
    scale = [c for c in ("Amount", "Time", "Hour") if c in cols]
    pre = ColumnTransformer([("scale", StandardScaler(), scale)], remainder="passthrough")
    steps = [("pre", pre)] + ([("smote", sampler)] if sampler is not None else []) + [("clf", model)]
    return Pipeline(steps)


def base_models(weighted=True):
    cw = "balanced" if weighted else None
    return {
        "Logistic Regression": LogisticRegression(max_iter=2000, class_weight=cw, random_state=SEED),
        "Decision Tree": DecisionTreeClassifier(class_weight=cw, random_state=SEED),
        "Random Forest": RandomForestClassifier(n_estimators=200, class_weight=cw, n_jobs=-1, random_state=SEED),
    }


GRIDS = {
    "Logistic Regression": {"clf__C": [0.01, 0.1, 1.0]},
    "Decision Tree": {"clf__max_depth": [5, 10, 20], "clf__min_samples_leaf": [1, 10]},
    "Random Forest": {"clf__max_depth": [None, 15], "clf__min_samples_leaf": [1, 5]},
}


def scores(y, prob, thr=0.5):
    pred = (prob >= thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {"accuracy": accuracy_score(y, pred), "precision": precision_score(y, pred, zero_division=0),
            "recall": recall_score(y, pred), "f1": f1_score(y, pred), "mcc": matthews_corrcoef(y, pred),
            "roc_auc": roc_auc_score(y, prob), "pr_auc": average_precision_score(y, prob),
            "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}


def bootstrap_f1(y, pred, n=1000):
    rng = np.random.default_rng(SEED)
    y, pred = np.asarray(y), np.asarray(pred)
    vals = [f1_score(y[i], pred[i]) for i in (rng.integers(0, len(y), len(y)) for _ in range(n))]
    return np.percentile(vals, [2.5, 97.5])


def mcnemar(y, a, b):
    """Continuity-corrected McNemar test on two prediction vectors."""
    ra, rb = (a == y), (b == y)
    n01, n10 = int((ra & ~rb).sum()), int((~ra & rb).sum())
    stat = (abs(n01 - n10) - 1) ** 2 / (n01 + n10) if n01 + n10 else 0.0
    return n01, n10, stat, float(chi2.sf(stat, 1))


def best_threshold(y, prob):
    p, r, t = precision_recall_curve(y, prob)
    f = 2 * p * r / np.clip(p + r, 1e-12, None)
    return float(t[np.argmax(f[:-1])])


# ---------------------------------------------------------------- main
def main():
    t0 = time.time()
    TAB.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    df, n_raw = load()
    X, y = df[features()], df["Class"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=SEED)
    # sanity check: after de-duplication no test row may also appear in training
    h = lambda d: set(pd.util.hash_pandas_object(pd.concat([d, df.loc[d.index, "Class"]], axis=1), index=False))
    assert not (h(Xtr) & h(Xte)), "duplicate rows leak between train and test"
    cv = StratifiedKFold(3, shuffle=True, random_state=SEED)
    meta = {"seed": SEED, "rows_raw": n_raw, "rows_dedup": len(df), "train_rows": len(Xtr), "test_rows": len(Xte),
            "train_fraud": int(ytr.sum()), "test_fraud": int(yte.sum())}

    # 1) duplicate leakage: what happens if duplicates are NOT removed before the split
    raw = pd.read_csv(DATA)
    rtr, rte = train_test_split(raw, test_size=0.3, stratify=raw["Class"], random_state=SEED)
    key = lambda d: pd.util.hash_pandas_object(d, index=False)
    leaked = rte[key(rte).isin(set(key(rtr)))]
    meta["leak_test_rows_also_in_train"] = int(len(leaked))
    meta["leak_fraud_rows_also_in_train"] = int(leaked["Class"].sum())

    # 2) tuning with class weights (3-fold CV on training split, PR-AUC)
    tuned, tuning_rows = {}, []
    for name, m in base_models().items():
        gs = GridSearchCV(make(m), GRIDS[name], scoring="average_precision", cv=cv, n_jobs=1 if name == "Random Forest" else -1)
        gs.fit(Xtr, ytr)
        tuned[name] = gs.best_params_
        tuning_rows.append({"model": name, "best_params": json.dumps(gs.best_params_), "cv_pr_auc": gs.best_score_,
                            "cv_pr_auc_sd": gs.cv_results_["std_test_score"][gs.best_index_]})
        print(f"tuned {name}: {gs.best_params_} CV PR-AUC {gs.best_score_:.4f}")
    pd.DataFrame(tuning_rows).to_csv(TAB / "tuning.csv", index=False)

    def tuned_model(name, weighted=True):
        m = base_models(weighted)[name]
        m.set_params(**{k.replace("clf__", ""): v for k, v in tuned[name].items()})
        return m

    # 3) imbalance strategy comparison on the test set: none vs class weights vs SMOTE
    strat_rows, fitted, probs = [], {}, {}
    for name in base_models():
        for strat in ["No resampling", "Class weights", "SMOTE"]:
            pipe = make(tuned_model(name, weighted=(strat == "Class weights")),
                        SMOTE(random_state=SEED) if strat == "SMOTE" else None)
            s = time.time(); pipe.fit(Xtr, ytr); fit_s = time.time() - s
            prob = pipe.predict_proba(Xte)[:, 1]
            strat_rows.append({"model": name, "strategy": strat, **scores(yte, prob), "fit_seconds": fit_s})
            fitted[(name, strat)], probs[(name, strat)] = pipe, prob
            print(f"{name:20s} {strat:14s} F1 {strat_rows[-1]['f1']:.4f} PR-AUC {strat_rows[-1]['pr_auc']:.4f}")
    strat_df = pd.DataFrame(strat_rows)
    strat_df.to_csv(TAB / "imbalance_strategies.csv", index=False)

    # main results = each model with its best strategy by validation-free rule: class weights (as proposed);
    # the strategy table shows the alternatives on the same test set.
    MAIN = "Class weights"
    main_rows, preds = [], {}
    for name in base_models():
        pipe, prob = fitted[(name, MAIN)], probs[(name, MAIN)]
        pred = (prob >= 0.5).astype(int); preds[name] = pred
        lo, hi = bootstrap_f1(yte, pred)
        s = time.time(); pipe.predict_proba(Xte); lat = (time.time() - s) / len(Xte) * 1000
        fit_s = strat_df.query("model == @name and strategy == @MAIN")["fit_seconds"].iloc[0]
        main_rows.append({"model": name, **scores(yte, prob), "f1_ci_low": lo, "f1_ci_high": hi,
                          "fit_seconds": fit_s, "latency_ms_per_txn": lat})
    main_df = pd.DataFrame(main_rows).sort_values("pr_auc", ascending=False)
    main_df.to_csv(TAB / "test_results.csv", index=False)
    best = main_df.iloc[0]["model"]; meta["best_model"] = best

    # 4) McNemar: best model vs the others
    mc = [{"model_a": best, "model_b": o, **dict(zip(["a_right_b_wrong", "b_right_a_wrong", "chi2", "p_value"],
                                                    mcnemar(yte.values, preds[best], preds[o])))}
          for o in preds if o != best]
    pd.DataFrame(mc).to_csv(TAB / "mcnemar.csv", index=False)

    # 5) decision threshold chosen on a validation slice of the training split
    Xa, Xv, ya, yv = train_test_split(Xtr, ytr, test_size=0.25, stratify=ytr, random_state=SEED)
    thr_rows = []
    for name in base_models():
        pipe = make(tuned_model(name)).fit(Xa, ya)
        thr = best_threshold(yv, pipe.predict_proba(Xv)[:, 1])
        prob = probs[(name, MAIN)]
        thr_rows.append({"model": name, "threshold": thr, **{f"default_{k}": v for k, v in scores(yte, prob).items() if k in ("precision", "recall", "f1")},
                         **{f"tuned_{k}": v for k, v in scores(yte, prob, thr).items() if k in ("precision", "recall", "f1", "fp", "fn")}})
    pd.DataFrame(thr_rows).to_csv(TAB / "thresholds.csv", index=False)

    # 6) Hour feature ablation (Random Forest, class weights)
    abl = []
    for label, cols in [("With Hour", features(True)), ("Without Hour", features(False))]:
        p = make(tuned_model("Random Forest"), cols=cols).fit(Xtr[cols], ytr).predict_proba(Xte[cols])[:, 1]
        abl.append({"features": label, **scores(yte, p)})
    pd.DataFrame(abl).to_csv(TAB / "ablation_hour.csv", index=False)

    # 7) temporal robustness: train on the first 70% of time, test on the last 30%
    cut = df["Time"].quantile(0.7)
    early, late = df[df.Time <= cut], df[df.Time > cut]
    temp = []
    for name in base_models():
        p = make(tuned_model(name)).fit(early[features()], early.Class).predict_proba(late[features()])[:, 1]
        temp.append({"model": name, "train_rows": len(early), "test_rows": len(late), **scores(late.Class, p)})
    pd.DataFrame(temp).to_csv(TAB / "temporal_split.csv", index=False)

    # 8) explainability: RF impurity + permutation importance, LR coefficients, SHAP
    rf = fitted[("Random Forest", MAIN)]
    names = list(rf.named_steps["pre"].get_feature_names_out())
    names = [n.split("__")[-1] for n in names]
    imp = pd.DataFrame({"feature": names, "impurity": rf.named_steps["clf"].feature_importances_})
    sub = Xte.sample(20000, random_state=SEED); ysub = yte.loc[sub.index]
    perm = permutation_importance(rf, sub, ysub, scoring="average_precision", n_repeats=5, random_state=SEED, n_jobs=-1)
    imp = imp.merge(pd.DataFrame({"feature": list(Xte.columns), "permutation": perm.importances_mean}), on="feature")
    lr = fitted[("Logistic Regression", MAIN)]
    lrn = [n.split("__")[-1] for n in lr.named_steps["pre"].get_feature_names_out()]
    imp = imp.merge(pd.DataFrame({"feature": lrn, "lr_coef": lr.named_steps["clf"].coef_[0]}), on="feature")
    imp.sort_values("permutation", ascending=False).to_csv(TAB / "feature_importance.csv", index=False)

    Xs = pd.DataFrame(rf.named_steps["pre"].transform(Xte.sample(1500, random_state=SEED)), columns=names)
    sv = shap.TreeExplainer(rf.named_steps["clf"]).shap_values(Xs)
    sv = sv[1] if isinstance(sv, list) else sv[..., 1]
    plt.figure(); shap.summary_plot(sv, Xs, max_display=12, show=False)
    plt.tight_layout(); plt.savefig(FIG / "shap_summary.png", dpi=160, bbox_inches="tight"); plt.close()

    # 9) scalability: Random Forest training time vs training size
    sc = []
    for frac in [0.1, 0.25, 0.5, 1.0]:
        n = int(len(Xtr) * frac)
        s = time.time(); make(tuned_model("Random Forest")).fit(Xtr.iloc[:n], ytr.iloc[:n]); sc.append({"rows": n, "fit_seconds": time.time() - s})
    pd.DataFrame(sc).to_csv(TAB / "scalability.csv", index=False)

    # 10) figures
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    for name in base_models():
        p = probs[(name, MAIN)]
        fpr, tpr, _ = roc_curve(yte, p); pr, rc, _ = precision_recall_curve(yte, p)
        ax[0].plot(fpr, tpr, color=COLORS[name], label=f"{name} (AUC {roc_auc_score(yte, p):.3f})")
        ax[1].plot(rc, pr, color=COLORS[name], label=f"{name} (AP {average_precision_score(yte, p):.3f})")
    ax[0].plot([0, 1], [0, 1], "k:", lw=.8); ax[0].set(xlabel="False positive rate", ylabel="True positive rate", title="ROC curves")
    ax[1].set(xlabel="Recall", ylabel="Precision", title="Precision-recall curves")
    for a in ax: a.legend(frameon=False, fontsize=7.5)
    fig.tight_layout(); fig.savefig(FIG / "roc_pr_curves.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(1, 3, figsize=(9, 2.9))
    for a, name in zip(ax, base_models()):
        r = main_df.set_index("model").loc[name]
        cm = np.array([[r.tn, r.fp], [r.fn, r.tp]])
        a.imshow(cm, cmap="Blues", norm=matplotlib.colors.LogNorm())
        for i in range(2):
            for j in range(2):
                a.text(j, i, f"{cm[i, j]:,}", ha="center", va="center", fontsize=9)
        a.set(xticks=[0, 1], yticks=[0, 1], xticklabels=["Legit", "Fraud"], yticklabels=["Legit", "Fraud"],
              xlabel="Predicted", ylabel="Actual", title=name)
    fig.tight_layout(); fig.savefig(FIG / "confusion_matrices.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 3.2))
    piv = strat_df.pivot(index="model", columns="strategy", values="f1")[["No resampling", "Class weights", "SMOTE"]]
    piv.loc[list(base_models())].plot.bar(ax=ax, rot=0, color=["#BBBBBB", "#4C72B0", "#C44E52"])
    ax.set(ylabel="F1 on test set", xlabel="", title="Effect of imbalance handling on F1"); ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(FIG / "imbalance_f1.png", dpi=160); plt.close(fig)

    top = imp.sort_values("permutation", ascending=False).head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    ax.barh(top.feature, top.permutation, color="#55A868")
    ax.set(xlabel="Drop in PR-AUC when feature is shuffled", title="Random Forest permutation importance")
    fig.tight_layout(); fig.savefig(FIG / "feature_importance.png", dpi=160); plt.close(fig)

    p = probs[("Random Forest", MAIN)]; pr, rc, t = precision_recall_curve(yte, p)
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    ax.plot(t, pr[:-1], label="Precision"); ax.plot(t, rc[:-1], label="Recall")
    ax.axvline(0.5, color="k", ls=":", lw=.8)
    rt = [r for r in thr_rows if r["model"] == "Random Forest"][0]["threshold"]
    ax.axvline(rt, color="#C44E52", ls="--", lw=.8, label=f"Tuned threshold {rt:.2f}")
    ax.set(xlabel="Decision threshold", title="Random Forest precision and recall by threshold"); ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(FIG / "threshold_tradeoff.png", dpi=160); plt.close(fig)

    s = pd.DataFrame(sc)
    fig, ax = plt.subplots(figsize=(5.5, 3))
    ax.plot(s.rows, s.fit_seconds, marker="o"); ax.set(xlabel="Training rows", ylabel="Fit time (s)", title="Random Forest training time")
    fig.tight_layout(); fig.savefig(FIG / "scalability.png", dpi=160); plt.close(fig)

    meta["runtime_seconds"] = time.time() - t0
    (TAB / "run_meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
