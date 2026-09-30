"""
Data preprocessing module for Credit Card Fraud Detection.

Handles loading, cleaning, exploring, and preparing the dataset
for machine learning model training and evaluation.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import *


def load_data(filepath=DATA_FILE):
    """Load the credit card fraud dataset from CSV."""
    print(f"Loading dataset from: {filepath}")
    df = pd.read_csv(filepath)
    print(f"Dataset loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
    return df


def explore_data(df):
    """Perform initial exploratory data analysis and return summary statistics."""
    summary = {}

    # Basic info
    summary["shape"] = df.shape
    summary["columns"] = list(df.columns)
    summary["dtypes"] = df.dtypes.to_dict()

    # Missing values
    summary["missing_values"] = df.isnull().sum().to_dict()
    summary["total_missing"] = df.isnull().sum().sum()

    # Duplicates
    summary["duplicates"] = df.duplicated().sum()

    # Class distribution
    class_dist = df[TARGET_COL].value_counts()
    summary["class_distribution"] = class_dist.to_dict()
    summary["class_percentage"] = (class_dist / len(df) * 100).to_dict()
    summary["fraud_ratio"] = class_dist[1] / class_dist[0]

    # Descriptive statistics
    summary["describe"] = df.describe()

    # Time and Amount statistics
    summary["time_stats"] = df["Time"].describe().to_dict()
    summary["amount_stats"] = df["Amount"].describe().to_dict()
    summary["amount_fraud"] = df[df[TARGET_COL] == 1]["Amount"].describe().to_dict()
    summary["amount_legit"] = df[df[TARGET_COL] == 0]["Amount"].describe().to_dict()

    # Print summary
    print("\n" + "=" * 60)
    print("DATASET SUMMARY")
    print("=" * 60)
    print(f"Total transactions:    {summary['shape'][0]:,}")
    print(f"Total features:        {summary['shape'][1]}")
    print(f"Missing values:        {summary['total_missing']}")
    print(f"Duplicate rows:        {summary['duplicates']}")
    print(f"\nClass Distribution:")
    print(f"  Legitimate (0): {class_dist[0]:,} ({summary['class_percentage'][0]:.3f}%)")
    print(f"  Fraudulent (1): {class_dist[1]:,} ({summary['class_percentage'][1]:.3f}%)")
    print(f"  Fraud ratio:    1:{1/summary['fraud_ratio']:.0f}")
    print(f"\nTransaction Amount:")
    print(f"  Mean:   €{df['Amount'].mean():.2f}")
    print(f"  Median: €{df['Amount'].median():.2f}")
    print(f"  Max:    €{df['Amount'].max():.2f}")
    print(f"  Fraud Mean:  €{df[df[TARGET_COL]==1]['Amount'].mean():.2f}")
    print(f"  Legit Mean:  €{df[df[TARGET_COL]==0]['Amount'].mean():.2f}")
    print("=" * 60)

    return summary


def clean_data(df):
    """Clean the dataset: handle missing values and duplicates."""
    print("\nCleaning dataset...")
    initial_rows = len(df)

    # Remove duplicates
    df = df.drop_duplicates()
    removed = initial_rows - len(df)
    print(f"  Removed {removed:,} duplicate rows")

    # Check for missing values
    missing = df.isnull().sum().sum()
    if missing > 0:
        print(f"  Found {missing} missing values — dropping rows with NaN")
        df = df.dropna()
    else:
        print("  No missing values found")

    print(f"  Final dataset: {len(df):,} rows")
    return df


def preprocess_data(df):
    """
    Preprocess the dataset:
    - Scale 'Time' and 'Amount' features using StandardScaler
    - V1-V28 are already PCA-transformed and scaled
    """
    print("\nPreprocessing features...")
    df = df.copy()

    # Scale Time and Amount
    scaler = StandardScaler()
    df["Time_scaled"] = scaler.fit_transform(df[["Time"]])
    df["Amount_scaled"] = scaler.fit_transform(df[["Amount"]])

    # Drop original Time and Amount, use scaled versions
    df = df.drop(["Time", "Amount"], axis=1)

    print("  Scaled 'Time' and 'Amount' using StandardScaler")
    print(f"  Feature count: {df.shape[1] - 1} (excluding target)")

    return df


def split_data(df, test_size=TEST_SIZE, random_state=RANDOM_STATE):
    """Split the dataset into training and testing sets."""
    # Separate features and target
    X = df.drop(TARGET_COL, axis=1)
    y = df[TARGET_COL]

    # Stratified split to preserve class distribution
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )

    print(f"\nData split (stratified, test_size={test_size}):")
    print(f"  Training set: {X_train.shape[0]:,} samples")
    print(f"    - Legitimate: {(y_train == 0).sum():,}")
    print(f"    - Fraudulent: {(y_train == 1).sum():,}")
    print(f"  Testing set:  {X_test.shape[0]:,} samples")
    print(f"    - Legitimate: {(y_test == 0).sum():,}")
    print(f"    - Fraudulent: {(y_test == 1).sum():,}")

    return X_train, X_test, y_train, y_test


def get_prepared_data(filepath=DATA_FILE):
    """Full pipeline: load, clean, preprocess, and split the data."""
    df = load_data(filepath)
    summary = explore_data(df)
    df = clean_data(df)
    df = preprocess_data(df)
    X_train, X_test, y_train, y_test = split_data(df)
    return X_train, X_test, y_train, y_test, summary


if __name__ == "__main__":
    X_train, X_test, y_train, y_test, summary = get_prepared_data()
    print("\n✅ Data preparation complete!")
