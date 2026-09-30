"""
Configuration file for the Fraud Detection Research Project.

Title: Determining the Role of Big Data Applications in Fraud Detection
       and Financial Security in Financial Institutions of Ireland

Author: Yashwanth
Dataset: Kaggle Credit Card Fraud Detection Dataset
"""

import os

# ─── Paths ───────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
FIGURES_DIR = os.path.join(RESULTS_DIR, "figures")
TABLES_DIR = os.path.join(RESULTS_DIR, "tables")
MODELS_DIR = os.path.join(RESULTS_DIR, "models")

DATA_FILE = os.path.join(DATA_DIR, "creditcard.csv")

# ─── Model Parameters ───────────────────────────────────────────────────────
RANDOM_STATE = 42
TEST_SIZE = 0.3  # 70% training, 30% testing

# ─── Target Column ──────────────────────────────────────────────────────────
TARGET_COL = "Class"  # 0 = Legitimate, 1 = Fraud

# ─── Feature Columns ────────────────────────────────────────────────────────
# V1-V28 are PCA-transformed features; Time and Amount are original
PCA_FEATURES = [f"V{i}" for i in range(1, 29)]
OTHER_FEATURES = ["Time", "Amount"]
ALL_FEATURES = OTHER_FEATURES + PCA_FEATURES

# ─── Visualization Settings ─────────────────────────────────────────────────
FIGURE_DPI = 300
FIGURE_FORMAT = "png"
PLOT_STYLE = "seaborn-v0_8-whitegrid"

# Model names for consistent labelling
MODEL_NAMES = {
    "lr": "Logistic Regression",
    "dt": "Decision Tree",
    "rf": "Random Forest"
}

# Colour palette for the three models
MODEL_COLORS = {
    "Logistic Regression": "#2196F3",
    "Decision Tree": "#FF9800",
    "Random Forest": "#4CAF50"
}

CLASS_LABELS = {0: "Legitimate", 1: "Fraudulent"}
CLASS_COLORS = {"Legitimate": "#4CAF50", "Fraudulent": "#F44336"}
