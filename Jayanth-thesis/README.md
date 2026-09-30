# Big Data Analytics for Cyber Threat Detection in Irish Banking

Final project for Jayanth Akarapu, Research Practicum (Open Data Practice).

## Layout
- `src/pipeline.py` — the full experiment in one command: EDA, tuning, evaluation, robustness tests, SHAP and figures.
- `notebooks/analysis.ipynb` — an executed notebook that reruns the pipeline and shows every table and figure.
- `results/` — CSV/JSON outputs behind every table in the report.
- `figures/` — all report figures.
- `report/thesis.tex` and `report/thesis.pdf` — the final report in LaTeX.

## Reproduce
```bash
pip install -r requirements.txt
kaggle datasets download -d charanmaik/bank-transaction-records-along-suspicious-flags --unzip -p data
python src/pipeline.py
cd report && latexmk -pdf thesis.tex
```
The Kaggle token lives in `~/.kaggle/` and is never committed.

## Headline results (held-out 20%, n = 6,723)
| Model | F1 | ROC-AUC |
|---|---|---|
| Decision Tree | 0.9960 | 0.9976 |
| Random Forest | 0.9960 | 0.9971 |
| Gradient Boosting | 0.9958 | 0.9987 |
| Rule baseline | 0.9951 | – |
| Logistic Regression | 0.9911 | 0.9965 |
| SVM (RBF) | 0.9893 | 0.9965 |

Two tests show where the models are limited:
- **Unseen merchants:** F1 falls to 0.86–0.88 when whole merchants are held out.
- **Rule baseline:** a two-condition rule comes within 0.001 F1 of the best model.

See Section 6 of the report for details.
