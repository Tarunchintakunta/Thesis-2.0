"""
Main pipeline script — runs the complete fraud detection analysis end-to-end.

Steps:
1. Load and explore the dataset
2. Clean and preprocess the data
3. Train three ML models (Logistic Regression, Decision Tree, Random Forest)
4. Evaluate and compare model performance
5. Generate all visualizations
6. Save results and models
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

# Ensure src is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from data_preprocessing import load_data, explore_data, clean_data, preprocess_data, split_data
from model_training import (
    train_and_evaluate_all, save_models, get_comparison_table,
    identify_best_model, get_feature_importance
)
from visualizations import generate_all_eda_plots, generate_all_model_plots

import pandas as pd


def main():
    print("╔" + "═" * 58 + "╗")
    print("║   CREDIT CARD FRAUD DETECTION — COMPLETE ANALYSIS        ║")
    print("║   Big Data Applications in Financial Security (Ireland)  ║")
    print("╚" + "═" * 58 + "╝")

    # ── Step 1: Load & Explore ──────────────────────────────────────────
    print("\n▶ STEP 1: Loading and Exploring Dataset")
    df = load_data()
    summary = explore_data(df)

    # ── Step 2: EDA Visualizations ──────────────────────────────────────
    print("\n▶ STEP 2: Generating EDA Visualizations")
    generate_all_eda_plots(df)

    # ── Step 3: Clean & Preprocess ──────────────────────────────────────
    print("\n▶ STEP 3: Cleaning and Preprocessing Data")
    df_clean = clean_data(df)
    df_processed = preprocess_data(df_clean)

    # ── Step 4: Split Data ──────────────────────────────────────────────
    print("\n▶ STEP 4: Splitting Data (70/30 stratified)")
    X_train, X_test, y_train, y_test = split_data(df_processed)

    # ── Step 5: Train & Evaluate Models ─────────────────────────────────
    print("\n▶ STEP 5: Training and Evaluating Models")
    results = train_and_evaluate_all(X_train, X_test, y_train, y_test)

    # ── Step 6: Comparison & Best Model ─────────────────────────────────
    print("\n▶ STEP 6: Model Comparison")
    comparison_df = get_comparison_table(results)
    print("\n" + comparison_df.to_string(index=False))

    best_name, best = identify_best_model(results)

    # ── Step 7: Feature Importance Analysis ─────────────────────────────
    print("\n▶ STEP 7: Feature Importance Analysis")
    feature_names = list(X_train.columns)
    importances = get_feature_importance(results, feature_names)

    for name, imp_df in importances.items():
        col = "Importance" if "Importance" in imp_df.columns else "Abs_Coefficient"
        print(f"\n  {name} — Top 10 Features:")
        for _, row in imp_df.head(10).iterrows():
            print(f"    {row['Feature']:>20s}: {row[col]:.6f}")

    # ── Step 8: Model Evaluation Visualizations ─────────────────────────
    print("\n▶ STEP 8: Generating Model Evaluation Visualizations")
    generate_all_model_plots(results, y_test, importances)

    # ── Step 9: Save Results ────────────────────────────────────────────
    print("\n▶ STEP 9: Saving Results")

    # Save models
    save_models(results)

    # Save comparison table
    os.makedirs(TABLES_DIR, exist_ok=True)
    comparison_df.to_csv(os.path.join(TABLES_DIR, "model_comparison.csv"), index=False)
    print(f"  Saved comparison table → {TABLES_DIR}/model_comparison.csv")

    # Save detailed classification reports
    for name, res in results.items():
        report_df = pd.DataFrame(res["classification_report"]).transpose()
        fname = name.lower().replace(" ", "_") + "_report.csv"
        report_df.to_csv(os.path.join(TABLES_DIR, fname))
        print(f"  Saved {name} report → {TABLES_DIR}/{fname}")

    # Save dataset summary
    summary_data = {
        "Metric": [
            "Total Transactions", "Features", "Legitimate Transactions",
            "Fraudulent Transactions", "Fraud Percentage", "Missing Values",
            "Duplicate Rows", "Mean Amount", "Max Amount",
            "Fraud Mean Amount", "Legit Mean Amount",
            "Training Samples", "Testing Samples",
            "Best Model", "Best F1 Score", "Best ROC AUC"
        ],
        "Value": [
            f"{summary['shape'][0]:,}", summary["shape"][1] - 1,
            f"{summary['class_distribution'][0]:,}",
            f"{summary['class_distribution'][1]:,}",
            f"{summary['class_percentage'][1]:.4f}%",
            summary["total_missing"], summary["duplicates"],
            f"€{summary['amount_stats']['mean']:.2f}",
            f"€{summary['amount_stats']['max']:.2f}",
            f"€{summary['amount_fraud']['mean']:.2f}",
            f"€{summary['amount_legit']['mean']:.2f}",
            f"{X_train.shape[0]:,}", f"{X_test.shape[0]:,}",
            best_name, f"{best['f1_score']:.4f}", f"{best['roc_auc']:.4f}"
        ]
    }
    pd.DataFrame(summary_data).to_csv(
        os.path.join(TABLES_DIR, "dataset_summary.csv"), index=False
    )
    print(f"  Saved dataset summary → {TABLES_DIR}/dataset_summary.csv")

    # ── Done ────────────────────────────────────────────────────────────
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║   ✅ ANALYSIS COMPLETE                                    ║")
    print("╚" + "═" * 58 + "╝")
    print(f"\n  Best Model: {best_name}")
    print(f"  Figures saved to: {FIGURES_DIR}")
    print(f"  Tables saved to:  {TABLES_DIR}")
    print(f"  Models saved to:  {MODELS_DIR}")

    return results, summary, comparison_df, importances


if __name__ == "__main__":
    results, summary, comparison_df, importances = main()
