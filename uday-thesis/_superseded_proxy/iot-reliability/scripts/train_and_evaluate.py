import os
import sys
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, recall_score

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.data.qos_simulator import generate_all_sites, FEATURES, SITE_REGIMES
from src.models.qos_models import CentralizedRF, FederatedEnsembleRF

SEEDS = [42, 43, 44, 45, 46]
N_PER_SITE = 1500


def score(y_true, y_pred):
    return {
        "Accuracy": round(accuracy_score(y_true, y_pred), 4),
        "Macro-F1": round(f1_score(y_true, y_pred, average="macro", zero_division=0), 4),
        "Critical Recall (class 2)": round(recall_score(y_true, y_pred, labels=[2], average="macro", zero_division=0), 4),
    }


def main():
    all_runs = []
    exported_model = None

    for seed in SEEDS:
        print(f"\n=== Seed {seed} ===")
        sites = generate_all_sites(n_per_site=N_PER_SITE, seed=seed)

        train_frames, test_X, test_y = {}, [], []
        for site, df in sites.items():
            train_df, test_df = train_test_split(df, test_size=0.2, random_state=seed, stratify=df["label"])
            train_frames[site] = train_df.reset_index(drop=True)
            test_X.append(test_df[FEATURES].values)
            test_y.append(test_df["label"].values)
        X_test_global = np.concatenate(test_X)
        y_test_global = np.concatenate(test_y)

        print("Training Centralized RF (baseline reproduction)...")
        centralized = CentralizedRF(seed).fit(train_frames, FEATURES)
        centralized_scores = score(y_test_global, centralized.predict(X_test_global))
        centralized_scores.update({"Model": "Centralized RF (baseline)", "Seed": seed})
        all_runs.append(centralized_scores)

        print("Training Federated Ensemble RF (improved)...")
        federated = FederatedEnsembleRF(seed).fit(train_frames, FEATURES)
        federated_scores = score(y_test_global, federated.predict(X_test_global))
        federated_scores.update({"Model": "Federated Ensemble RF (improved)", "Seed": seed})
        all_runs.append(federated_scores)

        # Lower bound: a single site's own local model, alone, with no
        # federation at all -- averaged across all 6 sites' local models.
        local_only_preds = [federated.predict_single_site(site, X_test_global) for site in sites]
        local_only_scores_per_site = [score(y_test_global, p) for p in local_only_preds]
        local_only_avg = {
            k: round(float(np.mean([s[k] for s in local_only_scores_per_site])), 4)
            for k in ["Accuracy", "Macro-F1", "Critical Recall (class 2)"]
        }
        local_only_avg.update({"Model": "Single-Site Local Only (no federation)", "Seed": seed})
        all_runs.append(local_only_avg)

        exported_model = federated

    results_df = pd.DataFrame(all_runs)
    print("\nPer-seed results:")
    print(results_df.to_string(index=False))

    metric_cols = ["Accuracy", "Macro-F1", "Critical Recall (class 2)"]
    summary = results_df.groupby("Model")[metric_cols].agg(["mean", "std"]).round(4)
    print("\nSummary across seeds (mean +/- std):")
    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(summary)

    results_dir = os.path.join(parent_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    results_df.to_csv(os.path.join(results_dir, "results_per_seed.csv"), index=False)
    summary.to_csv(os.path.join(results_dir, "results_summary.csv"))
    print(f"\nResults saved to {results_dir}/")

    # Export the federated site models for deployment -- one small RF per
    # site, bundled with the Lambda handler code.
    if exported_model is not None:
        import joblib
        model_dir = os.path.join(parent_dir, "src", "lambda_handler", "model")
        os.makedirs(model_dir, exist_ok=True)
        for site, m in exported_model.site_models.items():
            joblib.dump(m, os.path.join(model_dir, f"{site}.joblib"))
        with open(os.path.join(model_dir, "metadata.json"), "w") as f:
            json.dump({"features": FEATURES, "sites": list(SITE_REGIMES.keys())}, f, indent=2)
        print(f"Deployable federated models saved to {model_dir}/")


if __name__ == "__main__":
    main()
