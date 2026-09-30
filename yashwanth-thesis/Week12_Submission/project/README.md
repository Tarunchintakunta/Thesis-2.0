# Determining the Role of Big Data Applications in Fraud Detection and Financial Security in Financial Institutions of Ireland

MSc Research Practicum project by Yashwanth, National College of Ireland. Supervisor: Dr. Prasanth Nayak.

This project compares Logistic Regression, Decision Tree and Random Forest for detecting credit card fraud. It uses the Kaggle ULB dataset: 284,807 European card transactions, 0.17% of them fraud.

## Layout
- `src/pipeline.py`: the full experiment. It removes duplicates, makes the split, tunes the models, compares imbalance strategies, evaluates, runs robustness checks, explains the models and draws the figures.
- `notebooks/analysis.ipynb`: an executed notebook that shows every table and figure.
- `results/tables/`: the CSV and JSON files behind every number in the dissertation.
- `results/figures/`: all the figures.
- `../report/dissertation.tex` and `../report/dissertation.pdf`: the dissertation.

## Reproduce
```bash
pip install -r requirements.txt
kaggle datasets download -d mlg-ulb/creditcardfraud --unzip -p data
python src/pipeline.py
```
A run takes about six minutes on a laptop. The dataset (150 MB) is not stored in git.

## Method in short
- Remove the 1,081 duplicate rows before splitting.
- Make one stratified 70/30 split with seed 42.
- Fit scaling and SMOTE on the training data only.
- Tune each model with 3-fold cross-validation on PR-AUC.
- Choose the decision threshold on a validation slice of the training data.

## Main results (test set: 85,118 transactions, 142 frauds, class weights, threshold 0.5)
| Model | Precision | Recall | F1 | PR-AUC | False alarms |
|---|---|---|---|---|---|
| Random Forest | 0.962 | 0.711 | 0.818 | 0.823 | 4 |
| Decision Tree | 0.461 | 0.746 | 0.570 | 0.704 | 124 |
| Logistic Regression | 0.053 | 0.887 | 0.100 | 0.687 | 2,264 |

Choosing the threshold on validation data raises F1 to 0.844 for Random Forest, 0.785 for Logistic Regression and 0.741 for Decision Tree. When the models are trained on earlier transactions and tested on later ones, Random Forest keeps an F1 of 0.791.

## Data licence
The dataset is published on Kaggle by the Machine Learning Group, ULB, under the Database Contents License (DbCL) v1.0.
