"""
Visualization module for Credit Card Fraud Detection.

Generates all figures for the research report:
- EDA plots (class distribution, amount distribution, correlation, etc.)
- Model evaluation plots (confusion matrices, ROC curves, PR curves)
- Comparison charts
- Feature importance plots
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import numpy as np
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import *

# Global style
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": FIGURE_DPI,
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "figure.facecolor": "white",
})
sns.set_style("whitegrid")


def save_fig(fig, name, figures_dir=FIGURES_DIR):
    """Save a figure to the results directory."""
    os.makedirs(figures_dir, exist_ok=True)
    path = os.path.join(figures_dir, f"{name}.{FIGURE_FORMAT}")
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓ Saved: {name}.{FIGURE_FORMAT}")
    return path


# ═══════════════════════════════════════════════════════════════════════════
# EDA VISUALIZATIONS
# ═══════════════════════════════════════════════════════════════════════════

def plot_class_distribution(df):
    """Bar chart of class distribution (legitimate vs fraudulent)."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Count plot
    counts = df[TARGET_COL].value_counts()
    labels = [CLASS_LABELS[i] for i in counts.index]
    colors = [CLASS_COLORS[l] for l in labels]
    bars = axes[0].bar(labels, counts.values, color=colors, edgecolor="black", linewidth=0.5)
    for bar, val in zip(bars, counts.values):
        axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 500,
                     f"{val:,}", ha="center", va="bottom", fontweight="bold")
    axes[0].set_title("Transaction Class Distribution")
    axes[0].set_ylabel("Number of Transactions")

    # Pie chart
    axes[1].pie(counts.values, labels=labels, colors=colors, autopct="%1.3f%%",
                startangle=90, explode=(0, 0.1), shadow=True,
                textprops={"fontsize": 11})
    axes[1].set_title("Percentage Distribution")

    fig.suptitle("Class Distribution: Legitimate vs Fraudulent Transactions",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return save_fig(fig, "01_class_distribution")


def plot_amount_distribution(df):
    """Distribution of transaction amounts for each class."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for i, (cls, label) in enumerate(CLASS_LABELS.items()):
        subset = df[df[TARGET_COL] == cls]["Amount"]
        color = CLASS_COLORS[label]

        axes[0].hist(subset, bins=50, alpha=0.7, label=label, color=color, edgecolor="black", linewidth=0.3)
        axes[1].hist(subset, bins=50, alpha=0.7, label=label, color=color, edgecolor="black", linewidth=0.3)

    axes[0].set_title("Transaction Amount Distribution")
    axes[0].set_xlabel("Amount (€)")
    axes[0].set_ylabel("Frequency")
    axes[0].legend()

    axes[1].set_title("Transaction Amount Distribution (Log Scale)")
    axes[1].set_xlabel("Amount (€)")
    axes[1].set_ylabel("Frequency (log)")
    axes[1].set_yscale("log")
    axes[1].legend()

    fig.suptitle("Transaction Amount Distribution by Class",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return save_fig(fig, "02_amount_distribution")


def plot_time_distribution(df):
    """Distribution of transactions over time."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Overall time distribution
    axes[0].hist(df["Time"] / 3600, bins=48, color="#2196F3", alpha=0.7,
                 edgecolor="black", linewidth=0.3)
    axes[0].set_title("All Transactions Over Time")
    axes[0].set_xlabel("Time (hours)")
    axes[0].set_ylabel("Number of Transactions")

    # Fraud vs legit over time
    for cls, label in CLASS_LABELS.items():
        subset = df[df[TARGET_COL] == cls]["Time"] / 3600
        axes[1].hist(subset, bins=48, alpha=0.6, label=label,
                     color=CLASS_COLORS[label], edgecolor="black", linewidth=0.3)
    axes[1].set_title("Transactions Over Time by Class")
    axes[1].set_xlabel("Time (hours)")
    axes[1].set_ylabel("Frequency")
    axes[1].legend()

    fig.suptitle("Temporal Distribution of Transactions",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return save_fig(fig, "03_time_distribution")


def plot_correlation_heatmap(df):
    """Correlation heatmap of features."""
    fig, ax = plt.subplots(figsize=(16, 14))
    corr = df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, cmap="RdBu_r", center=0,
                annot=False, fmt=".2f", linewidths=0.5, ax=ax,
                cbar_kws={"shrink": 0.8})
    ax.set_title("Feature Correlation Heatmap", fontsize=14, fontweight="bold")
    fig.tight_layout()
    return save_fig(fig, "04_correlation_heatmap")


def plot_fraud_amount_boxplot(df):
    """Boxplot comparing transaction amounts between classes."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Standard scale
    data_plot = [df[df[TARGET_COL] == 0]["Amount"], df[df[TARGET_COL] == 1]["Amount"]]
    bp1 = axes[0].boxplot(data_plot, labels=["Legitimate", "Fraudulent"],
                          patch_artist=True, notch=True)
    bp1["boxes"][0].set_facecolor(CLASS_COLORS["Legitimate"])
    bp1["boxes"][1].set_facecolor(CLASS_COLORS["Fraudulent"])
    axes[0].set_title("Transaction Amount by Class")
    axes[0].set_ylabel("Amount (€)")

    # Log scale for better visibility
    bp2 = axes[1].boxplot(data_plot, labels=["Legitimate", "Fraudulent"],
                          patch_artist=True, notch=True)
    bp2["boxes"][0].set_facecolor(CLASS_COLORS["Legitimate"])
    bp2["boxes"][1].set_facecolor(CLASS_COLORS["Fraudulent"])
    axes[1].set_title("Transaction Amount by Class (Log Scale)")
    axes[1].set_ylabel("Amount (€) — log scale")
    axes[1].set_yscale("log")

    fig.suptitle("Transaction Amount Comparison: Legitimate vs Fraudulent",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return save_fig(fig, "05_amount_boxplot")


def plot_top_feature_distributions(df):
    """Distribution of top PCA features for fraud vs legitimate."""
    top_features = ["V1", "V2", "V3", "V4", "V10", "V11", "V12", "V14",
                    "V16", "V17"]
    fig, axes = plt.subplots(2, 5, figsize=(20, 8))
    axes = axes.flatten()

    for i, feat in enumerate(top_features):
        for cls, label in CLASS_LABELS.items():
            subset = df[df[TARGET_COL] == cls][feat]
            axes[i].hist(subset, bins=50, alpha=0.6, label=label,
                         color=CLASS_COLORS[label], density=True)
        axes[i].set_title(feat, fontweight="bold")
        axes[i].set_xlabel("")
        if i == 0:
            axes[i].legend(fontsize=8)

    fig.suptitle("Distribution of Key PCA Features by Class",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return save_fig(fig, "06_feature_distributions")


# ═══════════════════════════════════════════════════════════════════════════
# MODEL EVALUATION VISUALIZATIONS
# ═══════════════════════════════════════════════════════════════════════════

def plot_confusion_matrices(results, y_test):
    """Side-by-side confusion matrices for all three models."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    for i, (name, res) in enumerate(results.items()):
        cm = res["confusion_matrix"]
        sns.heatmap(cm, annot=True, fmt=",d", cmap="Blues", ax=axes[i],
                    xticklabels=["Legitimate", "Fraud"],
                    yticklabels=["Legitimate", "Fraud"],
                    linewidths=1, linecolor="black")
        axes[i].set_title(f"{name}\nAccuracy: {res['accuracy']:.4f}",
                          fontweight="bold")
        axes[i].set_ylabel("Actual")
        axes[i].set_xlabel("Predicted")

    fig.suptitle("Confusion Matrices — Model Comparison",
                 fontsize=14, fontweight="bold", y=1.05)
    fig.tight_layout()
    return save_fig(fig, "07_confusion_matrices")


def plot_roc_curves(results):
    """ROC curves for all three models on a single plot."""
    fig, ax = plt.subplots(figsize=(10, 8))

    for name, res in results.items():
        color = MODEL_COLORS[name]
        ax.plot(res["fpr"], res["tpr"],
                label=f"{name} (AUC = {res['roc_auc']:.4f})",
                color=color, linewidth=2)

    ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random Classifier")
    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title("Receiver Operating Characteristic (ROC) Curves",
                 fontsize=14, fontweight="bold")
    ax.legend(loc="lower right", fontsize=11)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1.02])
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    return save_fig(fig, "08_roc_curves")


def plot_precision_recall_curves(results):
    """Precision-Recall curves for all three models."""
    fig, ax = plt.subplots(figsize=(10, 8))

    for name, res in results.items():
        color = MODEL_COLORS[name]
        ax.plot(res["pr_recall"], res["pr_precision"],
                label=f"{name} (AP = {res['pr_auc']:.4f})",
                color=color, linewidth=2)

    ax.set_xlabel("Recall", fontsize=12)
    ax.set_ylabel("Precision", fontsize=12)
    ax.set_title("Precision-Recall Curves",
                 fontsize=14, fontweight="bold")
    ax.legend(loc="lower left", fontsize=11)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1.02])
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    return save_fig(fig, "09_precision_recall_curves")


def plot_metrics_comparison(results):
    """Grouped bar chart comparing all metrics across models."""
    metrics_keys = ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
    metric_labels = ["Accuracy", "Precision", "Recall", "F1 Score", "ROC AUC"]
    model_names = list(results.keys())

    x = np.arange(len(metric_labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 7))

    for i, name in enumerate(model_names):
        values = [results[name][k] for k in metrics_keys]
        bars = ax.bar(x + i * width, values, width, label=name,
                      color=MODEL_COLORS[name], edgecolor="black", linewidth=0.5)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax.set_xlabel("Metric", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title("Model Performance Comparison",
                 fontsize=14, fontweight="bold")
    ax.set_xticks(x + width)
    ax.set_xticklabels(metric_labels)
    ax.legend(fontsize=11)
    ax.set_ylim(0, 1.15)
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    return save_fig(fig, "10_metrics_comparison")


def plot_training_time(results):
    """Bar chart of training times."""
    fig, ax = plt.subplots(figsize=(8, 5))

    names = list(results.keys())
    times = [results[n]["training_time"] for n in names]
    colors = [MODEL_COLORS[n] for n in names]

    bars = ax.bar(names, times, color=colors, edgecolor="black", linewidth=0.5)
    for bar, t in zip(bars, times):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                f"{t:.2f}s", ha="center", va="bottom", fontweight="bold")

    ax.set_ylabel("Training Time (seconds)")
    ax.set_title("Model Training Time Comparison",
                 fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    return save_fig(fig, "11_training_time")


def plot_feature_importance(importances):
    """Feature importance plots for tree-based models."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    for i, (name, df_imp) in enumerate(importances.items()):
        if name == "Logistic Regression":
            continue
        top = df_imp.head(15)
        color = MODEL_COLORS[name]
        axes[i if name == "Decision Tree" else 1].barh(
            top["Feature"], top["Importance"],
            color=color, edgecolor="black", linewidth=0.3
        )
        axes[i if name == "Decision Tree" else 1].set_title(
            f"{name} — Top 15 Feature Importances", fontweight="bold"
        )
        axes[i if name == "Decision Tree" else 1].set_xlabel("Importance")
        axes[i if name == "Decision Tree" else 1].invert_yaxis()

    fig.suptitle("Feature Importance Analysis",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return save_fig(fig, "12_feature_importance")


def plot_lr_coefficients(importances):
    """Logistic Regression coefficient plot."""
    if "Logistic Regression" not in importances:
        return None

    df_coef = importances["Logistic Regression"].head(15)

    fig, ax = plt.subplots(figsize=(10, 7))
    colors = ["#F44336" if c < 0 else "#4CAF50" for c in df_coef["Coefficient"]]
    ax.barh(df_coef["Feature"], df_coef["Coefficient"], color=colors,
            edgecolor="black", linewidth=0.3)
    ax.set_title("Logistic Regression — Top 15 Feature Coefficients",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Coefficient Value")
    ax.invert_yaxis()
    ax.axvline(x=0, color="black", linewidth=0.8)
    ax.grid(axis="x", alpha=0.3)

    fig.tight_layout()
    return save_fig(fig, "13_lr_coefficients")


def generate_all_eda_plots(df):
    """Generate all EDA visualizations."""
    print("\n" + "=" * 60)
    print("GENERATING EDA VISUALIZATIONS")
    print("=" * 60)

    paths = []
    paths.append(plot_class_distribution(df))
    paths.append(plot_amount_distribution(df))
    paths.append(plot_time_distribution(df))
    paths.append(plot_correlation_heatmap(df))
    paths.append(plot_fraud_amount_boxplot(df))
    paths.append(plot_top_feature_distributions(df))

    print(f"\n  Generated {len(paths)} EDA plots")
    return paths


def generate_all_model_plots(results, y_test, importances):
    """Generate all model evaluation visualizations."""
    print("\n" + "=" * 60)
    print("GENERATING MODEL EVALUATION VISUALIZATIONS")
    print("=" * 60)

    paths = []
    paths.append(plot_confusion_matrices(results, y_test))
    paths.append(plot_roc_curves(results))
    paths.append(plot_precision_recall_curves(results))
    paths.append(plot_metrics_comparison(results))
    paths.append(plot_training_time(results))
    paths.append(plot_feature_importance(importances))
    paths.append(plot_lr_coefficients(importances))

    print(f"\n  Generated {len(paths)} model evaluation plots")
    return paths
