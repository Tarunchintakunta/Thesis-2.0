"""
Model training module for Credit Card Fraud Detection.

Implements, trains, and evaluates three supervised ML models:
1. Logistic Regression
2. Decision Tree
3. Random Forest
"""

import numpy as np
import pandas as pd
import joblib
import os
import sys
import time
import warnings
warnings.filterwarnings("ignore")

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, auc,
    precision_recall_curve, average_precision_score
)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import *


def build_models(random_state=RANDOM_STATE):
    """Initialise the three classification models."""
    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            random_state=random_state,
            solver="lbfgs",
            class_weight="balanced"
        ),
        "Decision Tree": DecisionTreeClassifier(
            random_state=random_state,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight="balanced"
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            random_state=random_state,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight="balanced",
            n_jobs=-1
        ),
    }
    return models


def train_model(model, X_train, y_train, model_name):
    """Train a single model and return training time."""
    print(f"\n  Training {model_name}...")
    start = time.time()
    model.fit(X_train, y_train)
    elapsed = time.time() - start
    print(f"  ✓ {model_name} trained in {elapsed:.2f}s")
    return model, elapsed


def evaluate_model(model, X_test, y_test, model_name):
    """Evaluate a trained model and return comprehensive metrics."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # Core metrics
    metrics = {
        "model_name": model_name,
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred),
        "confusion_matrix": confusion_matrix(y_test, y_pred),
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
    }

    # ROC curve data
    fpr, tpr, roc_thresholds = roc_curve(y_test, y_proba)
    metrics["fpr"] = fpr
    metrics["tpr"] = tpr
    metrics["roc_auc"] = auc(fpr, tpr)
    metrics["roc_thresholds"] = roc_thresholds

    # Precision-Recall curve data
    pr_precision, pr_recall, pr_thresholds = precision_recall_curve(y_test, y_proba)
    metrics["pr_precision"] = pr_precision
    metrics["pr_recall"] = pr_recall
    metrics["pr_auc"] = average_precision_score(y_test, y_proba)

    # Predictions for further analysis
    metrics["y_pred"] = y_pred
    metrics["y_proba"] = y_proba

    # Print summary
    cm = metrics["confusion_matrix"]
    print(f"\n  {model_name} Results:")
    print(f"    Accuracy:  {metrics['accuracy']:.4f}")
    print(f"    Precision: {metrics['precision']:.4f}")
    print(f"    Recall:    {metrics['recall']:.4f}")
    print(f"    F1 Score:  {metrics['f1_score']:.4f}")
    print(f"    ROC AUC:   {metrics['roc_auc']:.4f}")
    print(f"    PR AUC:    {metrics['pr_auc']:.4f}")
    print(f"    Confusion Matrix:")
    print(f"      TN={cm[0][0]:,}  FP={cm[0][1]:,}")
    print(f"      FN={cm[1][0]:,}  TP={cm[1][1]:,}")

    return metrics


def train_and_evaluate_all(X_train, X_test, y_train, y_test):
    """Train and evaluate all three models, returning results."""
    models = build_models()
    results = {}

    print("\n" + "=" * 60)
    print("MODEL TRAINING AND EVALUATION")
    print("=" * 60)

    for name, model in models.items():
        trained_model, train_time = train_model(model, X_train, y_train, name)
        metrics = evaluate_model(trained_model, X_test, y_test, name)
        metrics["training_time"] = train_time
        metrics["model_object"] = trained_model
        results[name] = metrics

    return results


def save_models(results, models_dir=MODELS_DIR):
    """Save trained models to disk."""
    os.makedirs(models_dir, exist_ok=True)
    for name, res in results.items():
        filename = name.lower().replace(" ", "_") + ".joblib"
        filepath = os.path.join(models_dir, filename)
        joblib.dump(res["model_object"], filepath)
        print(f"  Saved {name} → {filepath}")


def get_comparison_table(results):
    """Create a comparison DataFrame of all model metrics."""
    rows = []
    for name, res in results.items():
        rows.append({
            "Model": name,
            "Accuracy": f"{res['accuracy']:.4f}",
            "Precision": f"{res['precision']:.4f}",
            "Recall": f"{res['recall']:.4f}",
            "F1 Score": f"{res['f1_score']:.4f}",
            "ROC AUC": f"{res['roc_auc']:.4f}",
            "PR AUC": f"{res['pr_auc']:.4f}",
            "Training Time (s)": f"{res['training_time']:.2f}",
        })
    return pd.DataFrame(rows)


def identify_best_model(results):
    """Identify the best model based on F1 Score (key metric for imbalanced data)."""
    best_name = max(results, key=lambda k: results[k]["f1_score"])
    best = results[best_name]
    print(f"\n{'='*60}")
    print(f"BEST MODEL: {best_name}")
    print(f"  F1 Score:  {best['f1_score']:.4f}")
    print(f"  ROC AUC:   {best['roc_auc']:.4f}")
    print(f"  Precision: {best['precision']:.4f}")
    print(f"  Recall:    {best['recall']:.4f}")
    print(f"{'='*60}")
    return best_name, best


def get_feature_importance(results, feature_names):
    """Extract feature importances from tree-based models."""
    importances = {}

    for name in ["Decision Tree", "Random Forest"]:
        if name in results:
            model = results[name]["model_object"]
            imp = pd.DataFrame({
                "Feature": feature_names,
                "Importance": model.feature_importances_
            }).sort_values("Importance", ascending=False)
            importances[name] = imp

    # Logistic Regression coefficients
    if "Logistic Regression" in results:
        model = results["Logistic Regression"]["model_object"]
        coef = pd.DataFrame({
            "Feature": feature_names,
            "Coefficient": model.coef_[0]
        })
        coef["Abs_Coefficient"] = coef["Coefficient"].abs()
        coef = coef.sort_values("Abs_Coefficient", ascending=False)
        importances["Logistic Regression"] = coef

    return importances


if __name__ == "__main__":
    from data_preprocessing import get_prepared_data

    X_train, X_test, y_train, y_test, summary = get_prepared_data()
    results = train_and_evaluate_all(X_train, X_test, y_train, y_test)

    comparison = get_comparison_table(results)
    print("\n" + comparison.to_string(index=False))

    best_name, best = identify_best_model(results)
    save_models(results)
    print("\n✅ All models trained, evaluated, and saved!")
