# Determining the Role of Big Data Applications in Fraud Detection and Financial Security in Financial Institutions of Ireland

## Research Project — MSc, National College of Ireland

---

## Overview

This research project evaluates the role of **Big Data applications** in fraud detection and financial security improvement within financial institutions in Ireland. It implements and compares three machine learning algorithms for detecting fraudulent credit card transactions.

## Research Objectives

1. Identify the applications of big data in fraud detection and financial security
2. Examine the role of Big Data in improving regulatory standards and ethical considerations
3. Analyse current challenges in Irish financial institutions for fraud detection
4. Provide recommendations for implementing Big Data applications in fraud detection systems

## Dataset

**Kaggle Credit Card Fraud Detection Dataset** (MLG-ULB)
- **284,807** European credit card transactions (September 2013)
- **31 columns**: V1–V28 (PCA features), Time, Amount, Class
- **Class distribution**: 99.827% legitimate, 0.173% fraudulent (492 fraud cases)
- Highly imbalanced — 1 fraud per 578 legitimate transactions

## Models Implemented

| Model | Type | Description |
|-------|------|-------------|
| **Logistic Regression** | Linear | Baseline classifier with balanced class weights |
| **Decision Tree** | Tree-based | Interpretable model with depth constraints |
| **Random Forest** | Ensemble | 100 trees with balanced class weights |

## Results Summary

| Model | Accuracy | Precision | Recall | F1 Score | ROC AUC |
|-------|----------|-----------|--------|----------|---------|
| Logistic Regression | 0.9732 | 0.0528 | 0.8873 | 0.0996 | 0.9663 |
| Decision Tree | 0.9938 | 0.1806 | 0.7746 | 0.2929 | 0.8862 |
| **Random Forest** | **0.9995** | **0.9292** | **0.7394** | **0.8235** | **0.9473** |

**Best Model: Random Forest** — achieves the best balance between precision and recall (F1 = 0.8235).

## Project Structure

```
project/
├── data/
│   └── creditcard.csv           # Dataset (Kaggle)
├── notebooks/
│   ├── fraud_detection_analysis.ipynb           # Main notebook (template)
│   └── fraud_detection_analysis_executed.ipynb   # Executed with outputs
├── src/
│   ├── config.py                # Configuration and constants
│   ├── data_preprocessing.py    # Data loading, cleaning, preprocessing
│   ├── model_training.py        # Model training and evaluation
│   ├── visualizations.py        # All visualization functions
│   └── main.py                  # End-to-end pipeline script
├── results/
│   ├── figures/                 # All generated plots (13 figures)
│   │   ├── 01_class_distribution.png
│   │   ├── 02_amount_distribution.png
│   │   ├── 03_time_distribution.png
│   │   ├── 04_correlation_heatmap.png
│   │   ├── 05_amount_boxplot.png
│   │   ├── 06_feature_distributions.png
│   │   ├── 07_confusion_matrices.png
│   │   ├── 08_roc_curves.png
│   │   ├── 09_precision_recall_curves.png
│   │   ├── 10_metrics_comparison.png
│   │   ├── 11_training_time.png
│   │   ├── 12_feature_importance.png
│   │   └── 13_lr_coefficients.png
│   ├── tables/                  # CSV result tables
│   │   ├── model_comparison.csv
│   │   ├── dataset_summary.csv
│   │   ├── logistic_regression_report.csv
│   │   ├── decision_tree_report.csv
│   │   └── random_forest_report.csv
│   └── models/                  # Saved trained models
│       ├── logistic_regression.joblib
│       ├── decision_tree.joblib
│       └── random_forest.joblib
├── requirements.txt
└── README.md
```

## How to Run

### Prerequisites
```bash
pip install -r requirements.txt
```

### Option 1: Run the Pipeline Script
```bash
cd project/src
python main.py
```

### Option 2: Run the Jupyter Notebook
```bash
cd project/notebooks
jupyter notebook fraud_detection_analysis.ipynb
```

### Option 3: Use Google Colab
Upload `fraud_detection_analysis.ipynb` to Google Colab and run all cells.

## Technologies Used

- **Python 3.x** — Primary language
- **Scikit-learn** — Machine learning models and evaluation metrics
- **Pandas & NumPy** — Data manipulation and numerical computing
- **Matplotlib & Seaborn** — Data visualisation
- **Jupyter Notebook** — Interactive analysis environment

## Visualizations Generated

1. **Class Distribution** — Bar + pie chart of fraud vs legitimate
2. **Amount Distribution** — Histograms on linear and log scales
3. **Temporal Distribution** — Transaction patterns over 48 hours
4. **Correlation Heatmap** — Feature-to-feature correlation matrix
5. **Amount Boxplot** — Comparing transaction amounts by class
6. **Feature Distributions** — Key PCA features by class
7. **Confusion Matrices** — For all three models side by side
8. **ROC Curves** — Receiver Operating Characteristic for all models
9. **Precision-Recall Curves** — Critical for imbalanced classification
10. **Metrics Comparison** — Grouped bar chart of all metrics
11. **Training Time** — Computational cost comparison
12. **Feature Importance** — Decision Tree and Random Forest
13. **LR Coefficients** — Logistic Regression feature weights

## Key Findings

1. **Random Forest** is the most effective algorithm, providing the best precision-recall trade-off
2. **Feature V14** is the strongest predictor of fraud across all models
3. The extreme **class imbalance** (577:1) is the primary challenge — standard accuracy is misleading
4. **Ensemble methods** significantly outperform single classifiers for fraud detection
5. Big Data analytics combined with ML can process large transaction volumes and detect complex fraud patterns

## References

- Afriyie, J.K. et al. (2023). A supervised machine learning algorithm for detecting and predicting fraud in credit card transactions.
- Central Bank of Ireland (2025). Payment fraud statistics.
- Salunke, Y. et al. (2025). Fraud detection: A hybrid approach with logistic regression, decision tree, and Random Forest.
- Kaggle Dataset: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

## License

This project is for academic research purposes. The Kaggle dataset is used under the Open Database License (ODbL).
