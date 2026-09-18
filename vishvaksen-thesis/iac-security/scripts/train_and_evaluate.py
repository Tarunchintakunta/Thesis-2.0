import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.data.iac_dataset import generate_dataset
from src.models.detectors import MLDetector, HybridDetector, rule_based_flag

SEEDS = [42, 43, 44, 45, 46]
N_SAMPLES = 1200


def score(y_true, y_pred):
    return {
        "Precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "Recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "F1": round(f1_score(y_true, y_pred, zero_division=0), 4),
    }


def main():
    all_runs = []
    exported_ml_detector = None

    for seed in SEEDS:
        print(f"\n=== Seed {seed} ===")
        # Same underlying samples (identical pattern/label/filler choices
        # given the same seed), rendered with and without the explanatory
        # comment -- a paired rich-context vs. code-only comparison.
        rich_snippets, labels = generate_dataset(N_SAMPLES, seed=seed, with_comments=True)
        plain_snippets, labels_check = generate_dataset(N_SAMPLES, seed=seed, with_comments=False)
        assert (labels == labels_check).all(), "rich/plain datasets must be paired by construction"

        idx_train, idx_test = train_test_split(
            np.arange(N_SAMPLES), test_size=0.3, random_state=seed, stratify=labels
        )
        y_train, y_test = labels[idx_train], labels[idx_test]

        rich_train = [rich_snippets[i] for i in idx_train]
        rich_test = [rich_snippets[i] for i in idx_test]
        plain_train = [plain_snippets[i] for i in idx_train]
        plain_test = [plain_snippets[i] for i in idx_test]

        # RQ1 reproduction: ML classifier with rich (comment + code) context.
        ml_rich = MLDetector().fit(rich_train, y_train)
        rich_scores = score(y_test, ml_rich.predict(rich_test))
        rich_scores.update({"Model": "ML Detector (rich context)", "Seed": seed})
        all_runs.append(rich_scores)

        # RQ2 reproduction: same classifier family, code-only (no comments).
        ml_plain = MLDetector().fit(plain_train, y_train)
        plain_scores = score(y_test, ml_plain.predict(plain_test))
        plain_scores.update({"Model": "ML Detector (code-only, baseline gap)", "Seed": seed})
        all_runs.append(plain_scores)

        # Rule layer alone, for reference (comment-independent by construction).
        rule_preds = [1 if rule_based_flag(s) else 0 for s in plain_test]
        rule_scores = score(y_test, rule_preds)
        rule_scores.update({"Model": "Rule-Based Only (reference)", "Seed": seed})
        all_runs.append(rule_scores)

        # Improvement: hybrid of the code-only ML classifier + rule layer.
        hybrid = HybridDetector(ml_plain)
        hybrid_scores = score(y_test, hybrid.predict(plain_test))
        hybrid_scores.update({"Model": "Hybrid Detector (improved, code-only)", "Seed": seed})
        all_runs.append(hybrid_scores)

        exported_ml_detector = ml_plain

    results_df = pd.DataFrame(all_runs)
    print("\nPer-seed results:")
    print(results_df.to_string(index=False))

    metric_cols = ["Precision", "Recall", "F1"]
    summary = results_df.groupby("Model")[metric_cols].agg(["mean", "std"]).round(4)
    print("\nSummary across seeds (mean +/- std):")
    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(summary)

    results_dir = os.path.join(parent_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    results_df.to_csv(os.path.join(results_dir, "results_per_seed.csv"), index=False)
    summary.to_csv(os.path.join(results_dir, "results_summary.csv"))
    print(f"\nResults saved to {results_dir}/")

    if exported_ml_detector is not None:
        import joblib
        model_dir = os.path.join(parent_dir, "src", "lambda_handler", "model")
        os.makedirs(model_dir, exist_ok=True)
        joblib.dump(exported_ml_detector, os.path.join(model_dir, "ml_detector.joblib"))
        print(f"Deployable detector saved to {model_dir}/ml_detector.joblib")


if __name__ == "__main__":
    main()
