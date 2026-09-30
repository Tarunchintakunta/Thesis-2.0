"""End-to-end experiment pipeline for the thesis
"Analysing the Role of Big Data Analytics for Cyber Threat Detection and
Prevention in Banking Organisations of Ireland".

Run:  python src/pipeline.py
Needs data/transactions_Dataset.csv (Kaggle: charanmaik/bank-transaction-records-along-suspicious-flags).
Writes results/*.csv|json and figures/*.png.
"""
import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score, roc_curve, precision_recall_curve,
                             average_precision_score)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from statsmodels.stats.contingency_tables import mcnemar

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "transactions_Dataset.csv"
RES = ROOT / "results"
FIG = ROOT / "figures"
SEED = 42
RES.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
sns.set_theme(style="whitegrid", context="paper")

NUM = ["amount", "log_amount", "is_debit", "balance", "log_balance", "amount_to_balance",
       "negative_balance", "year", "month", "day", "dayofweek", "is_weekend"]
CAT = ["description", "channel"]


# ---------------------------------------------------------------- data
def channel_of(desc: str) -> str:
    d = desc.upper()
    for key in ["CRYPTOEXCHANGE", "PCA", "NETTXN", "IMPS", "FUNDSTRANSFER", "REFUNDOF",
                "REVOFNETTXN", "EMI", "CASHDEPOSIT", "ATMWITHDRAWAL"]:
        if d.startswith(key):
            return key
    return "OTHER"


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    n0 = len(df)
    df = df.drop_duplicates().dropna()
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
    df["amount"] = df["debit"] + df["credit"]
    df["is_debit"] = (df["debit"] > 0).astype(int)
    df["log_amount"] = np.log1p(df["amount"])
    df["log_balance"] = np.sign(df["balance"]) * np.log1p(df["balance"].abs())
    df["amount_to_balance"] = df["amount"] / (df["balance"].abs() + 1)
    df["negative_balance"] = (df["balance"] < 0).astype(int)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["dayofweek"] = df["date"].dt.dayofweek
    df["is_weekend"] = (df["dayofweek"] >= 5).astype(int)
    df["channel"] = df["description"].map(channel_of)
    print(f"loaded {n0} rows, {len(df)} after dedup/dropna")
    return df


def preprocessor(num, cat):
    return ColumnTransformer([
        ("num", StandardScaler(), num),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat),
    ])


def models():
    """Core models from the proposal (DT, RF, SVM) plus two reference models."""
    return {
        "Logistic Regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
        "Decision Tree": DecisionTreeClassifier(class_weight="balanced", random_state=SEED),
        "Random Forest": RandomForestClassifier(n_estimators=300, class_weight="balanced",
                                                n_jobs=-1, random_state=SEED),
        "SVM (RBF)": SVC(kernel="rbf", class_weight="balanced", probability=True, random_state=SEED),
        "Gradient Boosting": HistGradientBoostingClassifier(random_state=SEED),
    }


GRIDS = {
    "Decision Tree": {"clf__max_depth": [5, 10, 20, None], "clf__min_samples_leaf": [1, 5, 20]},
    "Random Forest": {"clf__max_depth": [10, 20, None], "clf__min_samples_leaf": [1, 5]},
    "SVM (RBF)": {"clf__C": [0.1, 1, 10], "clf__gamma": ["scale", 0.01]},
}


def scores(y, pred, prob):
    return {
        "accuracy": accuracy_score(y, pred),
        "precision": precision_score(y, pred),
        "recall": recall_score(y, pred),
        "f1": f1_score(y, pred),
        "roc_auc": roc_auc_score(y, prob),
        "pr_auc": average_precision_score(y, prob),
    }


def bootstrap_ci(y, pred, n=1000):
    rng = np.random.default_rng(SEED)
    y, pred = np.asarray(y), np.asarray(pred)
    vals = [f1_score(y[i], pred[i]) for i in (rng.integers(0, len(y), len(y)) for _ in range(n))]
    return np.percentile(vals, [2.5, 97.5])


# ---------------------------------------------------------------- EDA
def eda(df):
    summary = {
        "rows": len(df), "columns_raw": 6,
        "date_min": str(df.date.min().date()), "date_max": str(df.date.max().date()),
        "suspicious": int(df.isSuspicious.sum()), "normal": int((df.isSuspicious == 0).sum()),
        "suspicious_rate": float(df.isSuspicious.mean()),
        "unique_descriptions": int(df.description.nunique()),
    }
    json.dump(summary, open(RES / "eda_summary.json", "w"), indent=2)

    fig, ax = plt.subplots(figsize=(4, 3))
    df.isSuspicious.map({0: "Normal", 1: "Suspicious"}).value_counts().plot.bar(ax=ax, color=["#4C72B0", "#C44E52"])
    ax.set_ylabel("Transactions"); ax.set_xlabel(""); ax.tick_params(axis="x", rotation=0)
    fig.tight_layout(); fig.savefig(FIG / "class_balance.png", dpi=200); plt.close(fig)

    ch = df.groupby("channel").isSuspicious.agg(["mean", "size"]).sort_values("mean")
    ch.to_csv(RES / "channel_rates.csv")
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ch["mean"].plot.barh(ax=ax, color="#C44E52")
    ax.set_xlabel("Share flagged suspicious"); ax.set_ylabel("")
    fig.tight_layout(); fig.savefig(FIG / "suspicious_rate_by_channel.png", dpi=200); plt.close(fig)

    df.groupby("description").isSuspicious.agg(["mean", "size"]).sort_values("mean").to_csv(RES / "description_rates.csv")

    fig, ax = plt.subplots(figsize=(6, 3.5))
    sns.histplot(data=df, x="log_amount", hue="isSuspicious", bins=60, element="step", stat="density",
                 common_norm=False, ax=ax)
    ax.set_xlabel("log(1 + transaction amount)")
    fig.tight_layout(); fig.savefig(FIG / "amount_distribution.png", dpi=200); plt.close(fig)

    m = df.set_index("date").resample("MS").isSuspicious.agg(["mean", "size"])
    fig, ax1 = plt.subplots(figsize=(7, 3.2))
    ax1.bar(m.index, m["size"], width=20, color="#BBBBBB", label="Transactions")
    ax1.set_ylabel("Transactions / month")
    ax2 = ax1.twinx(); ax2.plot(m.index, m["mean"], color="#C44E52", marker="o", ms=3, label="Suspicious share")
    ax2.set_ylabel("Suspicious share"); ax2.grid(False)
    fig.tight_layout(); fig.savefig(FIG / "monthly_trend.png", dpi=200); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4.5))
    sns.heatmap(df[NUM + ["isSuspicious"]].corr(), cmap="vlag", center=0, ax=ax, cbar_kws={"shrink": .7})
    fig.tight_layout(); fig.savefig(FIG / "correlation_heatmap.png", dpi=200); plt.close(fig)
    return summary


# ---------------------------------------------------------------- experiments
def main():
    t_all = time.time()
    df = load()
    eda(df)
    X, y = df[NUM + CAT], df["isSuspicious"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)

    # 1) hyper-parameter tuning (5-fold CV on the training split only)
    tuned, tuning_rows = {}, []
    for name, clf in models().items():
        pipe = Pipeline([("prep", preprocessor(NUM, CAT)), ("clf", clf)])
        if name in GRIDS:
            gs = GridSearchCV(pipe, GRIDS[name], scoring="f1", cv=cv, n_jobs=-1)
            gs.fit(X_tr, y_tr)
            pipe = gs.best_estimator_
            tuning_rows.append({"model": name, "best_params": json.dumps(gs.best_params_),
                                "cv_f1": gs.best_score_})
        tuned[name] = pipe
    pd.DataFrame(tuning_rows).to_csv(RES / "tuning.csv", index=False)

    # 2) 5-fold CV of tuned models (mean +- sd) and held-out test evaluation
    cv_rows, test_rows, preds, probs = [], [], {}, {}
    for name, pipe in tuned.items():
        cvr = cross_validate(pipe, X_tr, y_tr, cv=cv, n_jobs=-1,
                             scoring=["accuracy", "precision", "recall", "f1", "roc_auc"])
        cv_rows.append({"model": name, **{f"{k[5:]}_mean": v.mean() for k, v in cvr.items() if k.startswith("test_")},
                        **{f"{k[5:]}_sd": v.std() for k, v in cvr.items() if k.startswith("test_")}})
        t = time.time(); pipe.fit(X_tr, y_tr); fit_s = time.time() - t
        t = time.time(); prob = pipe.predict_proba(X_te)[:, 1]; pred = (prob >= 0.5).astype(int)
        lat_ms = (time.time() - t) / len(X_te) * 1000
        lo, hi = bootstrap_ci(y_te, pred)
        tn, fp, fn, tp = confusion_matrix(y_te, pred).ravel()
        test_rows.append({"model": name, **scores(y_te, pred, prob), "f1_ci_low": lo, "f1_ci_high": hi,
                          "tn": tn, "fp": fp, "fn": fn, "tp": tp, "fit_seconds": fit_s,
                          "latency_ms_per_txn": lat_ms})
        preds[name], probs[name] = pred, prob
        print(f"{name:20s} F1={test_rows[-1]['f1']:.4f} AUC={test_rows[-1]['roc_auc']:.4f}")
    # transparent two-condition rule learnt from the training split only:
    # flag if the merchant/description has any suspicious history AND amount > threshold
    risky = set(X_tr.loc[y_tr == 1, "description"])
    ths = np.quantile(X_tr["amount"], np.linspace(.05, .95, 181))
    rule_f1 = [f1_score(y_tr, (X_tr.description.isin(risky) & (X_tr.amount > t)).astype(int)) for t in ths]
    rule_t = float(ths[int(np.argmax(rule_f1))])
    pred = (X_te.description.isin(risky) & (X_te.amount > rule_t)).astype(int).values
    lo, hi = bootstrap_ci(y_te, pred)
    tn, fp, fn, tp = confusion_matrix(y_te, pred).ravel()
    test_rows.append({"model": "Rule baseline", **scores(y_te, pred, pred), "f1_ci_low": lo, "f1_ci_high": hi,
                      "tn": tn, "fp": fp, "fn": fn, "tp": tp, "fit_seconds": 0, "latency_ms_per_txn": 0})
    json.dump({"risky_descriptions": sorted(risky), "amount_threshold": rule_t}, open(RES / "rule_baseline.json", "w"), indent=2)
    print(f"Rule baseline        F1={test_rows[-1]['f1']:.4f} (amount > {rule_t:,.0f})")

    cv_df = pd.DataFrame(cv_rows); cv_df.to_csv(RES / "cv_results.csv", index=False)
    test_df = pd.DataFrame(test_rows).sort_values("f1", ascending=False); test_df.to_csv(RES / "test_results.csv", index=False)

    # 3) McNemar test: best model vs every other model
    best = test_df.iloc[0]["model"]
    mc_rows = []
    for name in tuned:
        if name == best:
            continue
        a, b = preds[best] == y_te.values, preds[name] == y_te.values
        tbl = [[np.sum(a & b), np.sum(a & ~b)], [np.sum(~a & b), np.sum(~a & ~b)]]
        if tbl[0][1] + tbl[1][0] == 0:  # identical predictions: no evidence of a difference
            stat, pval = 0.0, 1.0
        else:
            r = mcnemar(tbl, exact=True)
            stat, pval = r.statistic, r.pvalue
        mc_rows.append({"best": best, "other": name, "best_only_correct": tbl[0][1],
                        "other_only_correct": tbl[1][0], "statistic": stat, "p_value": pval})
    pd.DataFrame(mc_rows).to_csv(RES / "mcnemar.csv", index=False)

    # 4) figures: ROC, PR, confusion matrices
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.8))
    for name in tuned:
        fpr, tpr, _ = roc_curve(y_te, probs[name]); a1.plot(fpr, tpr, label=f"{name} ({roc_auc_score(y_te, probs[name]):.3f})")
        p, r, _ = precision_recall_curve(y_te, probs[name]); a2.plot(r, p, label=name)
    a1.plot([0, 1], [0, 1], "k--", lw=.8); a1.set_xlabel("False positive rate"); a1.set_ylabel("True positive rate"); a1.legend(fontsize=6)
    a2.set_xlabel("Recall"); a2.set_ylabel("Precision"); a2.axhline(y_te.mean(), color="k", ls="--", lw=.8)
    fig.tight_layout(); fig.savefig(FIG / "roc_pr_curves.png", dpi=200); plt.close(fig)

    fig, axes = plt.subplots(1, len(tuned), figsize=(3 * len(tuned), 2.8))
    for ax, name in zip(axes, tuned):
        sns.heatmap(confusion_matrix(y_te, preds[name]), annot=True, fmt="d", cbar=False, cmap="Blues", ax=ax,
                    xticklabels=["Normal", "Susp."], yticklabels=["Normal", "Susp."])
        ax.set_title(name, fontsize=8); ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
    fig.tight_layout(); fig.savefig(FIG / "confusion_matrices.png", dpi=200); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 3.5))
    m = test_df.set_index("model")[["accuracy", "precision", "recall", "f1", "roc_auc"]]
    m.plot.bar(ax=ax, width=.8); ax.set_ylim(max(0, m.values.min() - .1), 1.0); ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=15); ax.legend(fontsize=7, ncol=5, loc="lower center", bbox_to_anchor=(.5, 1.0), frameon=False)
    fig.tight_layout(); fig.savefig(FIG / "model_comparison.png", dpi=200); plt.close(fig)

    # 5) explainability: RF impurity importance + SHAP
    rf = tuned["Random Forest"]
    names = rf.named_steps["prep"].get_feature_names_out()
    imp = pd.Series(rf.named_steps["clf"].feature_importances_, index=names).sort_values(ascending=False)
    imp.to_csv(RES / "rf_feature_importance.csv", header=["importance"])
    fig, ax = plt.subplots(figsize=(6, 4))
    imp.head(15)[::-1].plot.barh(ax=ax, color="#4C72B0"); ax.set_xlabel("Mean decrease in impurity")
    fig.tight_layout(); fig.savefig(FIG / "rf_feature_importance.png", dpi=200); plt.close(fig)
    try:
        import shap
        Xs = rf.named_steps["prep"].transform(X_te.sample(500, random_state=SEED))
        sv = shap.TreeExplainer(rf.named_steps["clf"]).shap_values(Xs)
        sv = sv[1] if isinstance(sv, list) else sv[..., 1]
        plt.figure()
        shap.summary_plot(sv, Xs, feature_names=[n.split("__")[-1] for n in names], max_display=15, show=False)
        plt.tight_layout(); plt.savefig(FIG / "shap_summary.png", dpi=200); plt.close("all")
    except Exception as e:  # SHAP is optional; report without it
        print("SHAP skipped:", e)

    # 6) ablations (Random Forest, same split): which feature groups carry the signal
    groups = {
        "All features": (NUM, CAT),
        "Without description/channel": (NUM, []),
        "Without date features": ([c for c in NUM if c not in ["year", "month", "day", "dayofweek", "is_weekend"]], CAT),
        "Description/channel only": ([], CAT),
        "Amount & balance only": (["amount", "log_amount", "is_debit", "balance", "log_balance", "amount_to_balance", "negative_balance"], []),
    }
    ab_rows = []
    for g, (num, cat) in groups.items():
        p = Pipeline([("prep", preprocessor(num, cat)), ("clf", RandomForestClassifier(
            n_estimators=300, class_weight="balanced", n_jobs=-1, random_state=SEED,
            **{k[5:]: v for k, v in json.loads(tuning_rows[[r["model"] for r in tuning_rows].index("Random Forest")]["best_params"]).items()}))])
        p.fit(X_tr[num + cat], y_tr); pr = p.predict_proba(X_te[num + cat])[:, 1]
        ab_rows.append({"feature_set": g, **scores(y_te, (pr >= .5).astype(int), pr)})
    pd.DataFrame(ab_rows).to_csv(RES / "ablation.csv", index=False)

    # 7) class-imbalance handling: class weights vs SMOTE vs none (Random Forest)
    im_rows = []
    for label, pipe in {
        "No re-balancing": Pipeline([("prep", preprocessor(NUM, CAT)), ("clf", RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=SEED))]),
        "Class weights": Pipeline([("prep", preprocessor(NUM, CAT)), ("clf", RandomForestClassifier(n_estimators=300, class_weight="balanced", n_jobs=-1, random_state=SEED))]),
        "SMOTE": ImbPipeline([("prep", preprocessor(NUM, CAT)), ("smote", SMOTE(random_state=SEED)), ("clf", RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=SEED))]),
    }.items():
        pipe.fit(X_tr, y_tr); pr = pipe.predict_proba(X_te)[:, 1]
        im_rows.append({"strategy": label, **scores(y_te, (pr >= .5).astype(int), pr)})
    pd.DataFrame(im_rows).to_csv(RES / "imbalance.csv", index=False)

    # 8) temporal robustness: train on older transactions, test on the latest 20%
    order = df.sort_values("date")
    cut_date = order.date.iloc[int(len(order) * .8)]
    tr, te = order[order.date < cut_date], order[order.date >= cut_date]
    tmp_rows = []
    for name in ["Decision Tree", "Random Forest", "SVM (RBF)", "Gradient Boosting"]:
        for fs, num in {"All features": NUM, "Without date features": [c for c in NUM if c not in ["year", "month", "day", "dayofweek", "is_weekend"]]}.items():
            p = Pipeline([("prep", preprocessor(num, CAT)), ("clf", tuned[name].named_steps["clf"])])
            p.fit(tr[num + CAT], tr.isSuspicious); pr = p.predict_proba(te[num + CAT])[:, 1]
            tmp_rows.append({"model": name, "feature_set": fs, "train_until": str(tr.date.max().date()),
                             "test_from": str(te.date.min().date()), "test_suspicious_rate": te.isSuspicious.mean(),
                             **scores(te.isSuspicious, (pr >= .5).astype(int), pr)})
    pd.DataFrame(tmp_rows).to_csv(RES / "temporal_split.csv", index=False)

    # 8b) unseen-merchant generalisation: GroupKFold over descriptions, description one-hot dropped
    from sklearn.model_selection import GroupKFold
    grp_rows = []
    for name in ["Decision Tree", "Random Forest", "SVM (RBF)", "Gradient Boosting"]:
        p = Pipeline([("prep", preprocessor(NUM, ["channel"])), ("clf", tuned[name].named_steps["clf"])])
        r = cross_validate(p, X[NUM + ["channel"]], y, groups=df["description"], cv=GroupKFold(5), n_jobs=-1,
                           scoring=["accuracy", "precision", "recall", "f1", "roc_auc"])
        grp_rows.append({"model": name, **{k[5:]: v.mean() for k, v in r.items() if k.startswith("test_")},
                         "f1_sd": r["test_f1"].std()})
    pd.DataFrame(grp_rows).to_csv(RES / "unseen_merchant.csv", index=False)

    # 9) decision threshold trade-off for the best model (alert budget view)
    th_rows = []
    for th in np.arange(.1, .95, .05):
        pr = (probs[best] >= th).astype(int)
        th_rows.append({"threshold": round(th, 2), "precision": precision_score(y_te, pr, zero_division=0),
                        "recall": recall_score(y_te, pr), "f1": f1_score(y_te, pr),
                        "alerts_per_1000": pr.mean() * 1000})
    th = pd.DataFrame(th_rows); th.to_csv(RES / "thresholds.csv", index=False)
    fig, ax = plt.subplots(figsize=(5.5, 3.3))
    for c in ["precision", "recall", "f1"]:
        ax.plot(th.threshold, th[c], marker="o", ms=3, label=c)
    ax.set_xlabel(f"Decision threshold ({best})"); ax.legend()
    fig.tight_layout(); fig.savefig(FIG / "threshold_tradeoff.png", dpi=200); plt.close(fig)

    # 10) scalability: training time vs data size (Random Forest, n_jobs=-1)
    sc_rows = []
    for frac in [.1, .25, .5, 1.0]:
        n = int(len(X_tr) * frac)
        for name in ["Decision Tree", "Random Forest", "SVM (RBF)"]:
            p = Pipeline([("prep", preprocessor(NUM, CAT)), ("clf", tuned[name].named_steps["clf"])])
            t = time.time(); p.fit(X_tr.iloc[:n], y_tr.iloc[:n]); sc_rows.append({"model": name, "rows": n, "fit_seconds": time.time() - t})
    sc = pd.DataFrame(sc_rows); sc.to_csv(RES / "scalability.csv", index=False)
    fig, ax = plt.subplots(figsize=(5, 3.2))
    for name, g in sc.groupby("model"):
        ax.plot(g.rows, g.fit_seconds, marker="o", label=name)
    ax.set_xlabel("Training rows"); ax.set_ylabel("Fit time (s)"); ax.legend()
    fig.tight_layout(); fig.savefig(FIG / "scalability.png", dpi=200); plt.close(fig)

    json.dump({"best_model": best, "runtime_seconds": time.time() - t_all, "seed": SEED,
               "train_rows": len(X_tr), "test_rows": len(X_te)}, open(RES / "run_meta.json", "w"), indent=2)
    print(f"done in {time.time() - t_all:.0f}s; best={best}")


if __name__ == "__main__":
    main()
