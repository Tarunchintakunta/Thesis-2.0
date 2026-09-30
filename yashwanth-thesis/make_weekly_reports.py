"""Builds the Week 3 to Week 12 submissions for Yashwanth, following his 12-week Gantt chart.

Every number is read from project/results/tables (written by project/src/pipeline.py).
    python make_weekly_reports.py
Creates WeekN_Submission/ folders (report PDF plus the files behind it) and a zip for each.
"""
import json
import shutil
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parent
PROJ = ROOT / "project"
TAB, FIG, W2FIG = PROJ / "results" / "tables", PROJ / "results" / "figures", ROOT / "Week2_Submission" / "figures"
STUDENT, TOPIC = "Yashwanth", ("Determining the Role of Big Data Applications in Fraud Detection and Financial "
                               "Security in Financial Institutions of Ireland")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="Times-Bold", fontSize=14, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Times-Bold", fontSize=12, spaceBefore=8, spaceAfter=4)
B = ParagraphStyle("B", parent=ss["BodyText"], fontName="Times-Roman", fontSize=11.5, leading=16, alignment=TA_JUSTIFY, spaceAfter=7)
C = ParagraphStyle("C", parent=B, fontSize=9.5, leading=12, alignment=0, spaceAfter=0)
CAP = ParagraphStyle("CAP", parent=B, fontSize=10, alignment=1)


def tbl(rows, widths):
    t = Table([[Paragraph(f"<b>{c}</b>" if i == 0 else str(c), C) for c in r] for i, r in enumerate(rows)],
              colWidths=[w * cm for w in widths])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .5, colors.black), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return [t, Spacer(1, 6)]


def img(path, caption, w=14):
    im = Image(str(path)); im.drawHeight = im.drawHeight * (w * cm) / im.drawWidth; im.drawWidth = w * cm
    return [im, Paragraph(caption, CAP), Spacer(1, 6)]


f3 = lambda x: f"{x:.3f}"


def weeks():
    meta = json.loads((TAB / "run_meta.json").read_text())
    tune = pd.read_csv(TAB / "tuning.csv").set_index("model")
    st = pd.read_csv(TAB / "imbalance_strategies.csv", keep_default_na=False)
    test = pd.read_csv(TAB / "test_results.csv").set_index("model")
    mc = pd.read_csv(TAB / "mcnemar.csv")
    thr = pd.read_csv(TAB / "thresholds.csv").set_index("model")
    temp = pd.read_csv(TAB / "temporal_split.csv").set_index("model")
    hour = pd.read_csv(TAB / "ablation_hour.csv").set_index("features")
    sc = pd.read_csv(TAB / "scalability.csv")
    imp = pd.read_csv(TAB / "feature_importance.csv")
    s = lambda m, k, c: st[(st.model == m) & (st.strategy == k)][c].iloc[0]
    M = ["Logistic Regression", "Decision Tree", "Random Forest"]
    dups = meta["rows_raw"] - meta["rows_dedup"]

    return {
        3: dict(gantt="Literature Review and Dataset Collection (final week), Data Preprocessing (start)",
                body=[
                    "This week I finished the literature review and dataset collection and started preprocessing. For the "
                    "review I added Ma et al. (2026), who warn that resampling should be judged on a test set with the real "
                    "class balance, and Horobets et al. (2025) on EU rules for AI in banking.",
                    f"For preprocessing, my first step was the duplicates I found in Week 2. The file has "
                    f"{meta['rows_raw']:,} rows and {dups:,} of them are exact copies. I checked what happens if they are "
                    f"left in: after a normal 70/30 split, {meta['leak_test_rows_also_in_train']} test rows also appear in the "
                    f"training data, {meta['leak_fraud_rows_also_in_train']} of them fraud. So I removed duplicates before "
                    f"splitting. The final split is {meta['train_rows']:,} training rows ({meta['train_fraud']} frauds) and "
                    f"{meta['test_rows']:,} test rows ({meta['test_fraud']} frauds), stratified with seed {meta['seed']}. I "
                    f"added a check to the code that stops the run if any test row is also in training.",
                ],
                table=([["Step", "Result"], ["Rows in file", f"{meta['rows_raw']:,}"], ["Duplicates removed", f"{dups:,}"],
                        ["Rows after cleaning", f"{meta['rows_dedup']:,}"], ["Training rows (frauds)", f"{meta['train_rows']:,} ({meta['train_fraud']})"],
                        ["Test rows (frauds)", f"{meta['test_rows']:,} ({meta['test_fraud']})"],
                        ["Test rows leaked if duplicates kept", f"{meta['leak_test_rows_also_in_train']}"]], [8, 6]),
                figs=[], files=[TAB / "run_meta.json"],
                next="Scale Time and Amount, add an hour of day feature and explore the cleaned data."),
        4: dict(gantt="Data Preprocessing and Exploratory Data Analysis",
                body=[
                    "This week I finished preprocessing and started the exploratory analysis. Time, Amount and the new Hour "
                    "feature are standardised, and the scaler is fitted on training data only so no test information is "
                    "used. V1 to V28 are already centred PCA components, so they are left as they are.",
                    "The exploration confirmed three patterns from Week 2. Fraud amounts have a lower median but a longer "
                    "tail than legitimate ones, fraud is about three to four times more common between midnight and 6am, "
                    "and V17, V14, V12 and V10 are the components most correlated with fraud.",
                ],
                table=None,
                figs=[(W2FIG / "w2_amounts.png", "Transaction amounts by class (log scale)."),
                      (W2FIG / "w2_hourly.png", "Transactions and fraud rate by hour of day.")],
                files=[W2FIG / "w2_top_corr.png"],
                next="Build the model pipeline and run a first comparison of the three models."),
        5: dict(gantt="Exploratory Data Analysis (end) and Model Development (start)",
                body=[
                    "This week I built the model pipeline. Each model is wrapped with scaling and, where used, SMOTE, so "
                    "every step that learns from data only sees the training data. I then ran a first comparison of "
                    "Logistic Regression, Decision Tree and Random Forest without any resampling.",
                    f"Random Forest was already ahead with an F1 of {f3(s('Random Forest', 'No resampling', 'f1'))}, then "
                    f"Decision Tree at {f3(s('Decision Tree', 'No resampling', 'f1'))} and Logistic Regression at "
                    f"{f3(s('Logistic Regression', 'No resampling', 'f1'))}. All three have accuracy above 99.9%, which "
                    f"confirms that accuracy is not a useful measure on this data.",
                ],
                table=([["Model", "Accuracy", "Precision", "Recall", "F1"]] +
                       [[m, f"{s(m, 'No resampling', 'accuracy'):.4f}", f3(s(m, 'No resampling', 'precision')), f3(s(m, 'No resampling', 'recall')), f3(s(m, 'No resampling', 'f1'))] for m in M],
                       [4.5, 2.5, 2.5, 2.5, 2.5]),
                figs=[], files=[PROJ / "src" / "pipeline.py"],
                next="Tune each model with cross-validation on the training data."),
        6: dict(gantt="Model Development",
                body=[
                    "This week I tuned the models with stratified 3-fold cross-validation on the training data. I used "
                    "PR-AUC as the tuning score because it focuses on how well the rare fraud class is ranked, which is "
                    "what matters here.",
                    f"Random Forest clearly leads with a cross-validated PR-AUC of {f3(tune.loc['Random Forest', 'cv_pr_auc'])} "
                    f"and the smallest spread across folds. Logistic Regression ({f3(tune.loc['Logistic Regression', 'cv_pr_auc'])}) "
                    f"and Decision Tree ({f3(tune.loc['Decision Tree', 'cv_pr_auc'])}) are close to each other.",
                ],
                table=([["Model", "Selected settings", "CV PR-AUC", "SD"]] +
                       [[m, tune.loc[m, "best_params"].replace('"clf__', '"').replace('"', '').replace("null", "None"),
                         f3(tune.loc[m, "cv_pr_auc"]), f3(tune.loc[m, "cv_pr_auc_sd"])] for m in M],
                       [4, 7, 2.5, 2]),
                figs=[], files=[TAB / "tuning.csv"],
                next="Compare no resampling, class weights and SMOTE for every model."),
        7: dict(gantt="Model Development (end) and Model Evaluation (start)",
                body=[
                    "This week I compared three ways of handling the imbalance for every tuned model: no resampling, class "
                    "weights and SMOTE. SMOTE is applied only inside the training data.",
                    f"The result was not what many papers suggest. For Random Forest the strategy makes little difference "
                    f"(F1 between {f3(st[st.model == 'Random Forest'].f1.min())} and {f3(st[st.model == 'Random Forest'].f1.max())}). "
                    f"For Logistic Regression, class weights and SMOTE push F1 down to about 0.10 because the model flags "
                    f"thousands of legitimate payments at the default threshold of 0.5. Decision Tree with SMOTE also drops "
                    f"sharply (F1 {f3(s('Decision Tree', 'SMOTE', 'f1'))}). This agrees with Ma et al. (2026) that resampling "
                    f"is not always helpful.",
                ],
                table=([["Model", "No resampling", "Class weights", "SMOTE"]] +
                       [[m] + [f3(s(m, k, "f1")) for k in ["No resampling", "Class weights", "SMOTE"]] for m in M], [5, 3, 3, 3]),
                figs=[(FIG / "imbalance_f1.png", "F1 on the test set for each imbalance strategy.")],
                files=[TAB / "imbalance_strategies.csv"],
                next="Evaluate the final models in detail and test whether the differences are significant."),
        8: dict(gantt="Model Evaluation and Results Analysis",
                body=[
                    f"This week I evaluated the three models with class weights, as planned in my proposal, on the "
                    f"{meta['test_rows']:,} test transactions. Random Forest is the best model: F1 "
                    f"{f3(test.loc['Random Forest', 'f1'])} (95% interval {f3(test.loc['Random Forest', 'f1_ci_low'])} to "
                    f"{f3(test.loc['Random Forest', 'f1_ci_high'])}), PR-AUC {f3(test.loc['Random Forest', 'pr_auc'])}, and only "
                    f"{int(test.loc['Random Forest', 'fp'])} false alarms. Logistic Regression finds the most frauds but raises "
                    f"{int(test.loc['Logistic Regression', 'fp']):,} false alarms.",
                    "McNemar's test shows that Random Forest is significantly different from both other models (p below "
                    "0.001). Logistic Regression has the highest ROC-AUC but a low PR-AUC, which shows why PR-AUC is the "
                    "better measure for rare fraud.",
                ],
                table=([["Model", "Precision", "Recall", "F1", "PR-AUC", "False alarms"]] +
                       [[m, f3(test.loc[m, "precision"]), f3(test.loc[m, "recall"]), f3(test.loc[m, "f1"]), f3(test.loc[m, "pr_auc"]), f"{int(test.loc[m, 'fp']):,}"] for m in test.index],
                       [4.2, 2.2, 2.2, 2.2, 2.2, 2.5]),
                figs=[(FIG / "roc_pr_curves.png", "ROC and precision-recall curves on the test set.")],
                files=[TAB / "test_results.csv", TAB / "mcnemar.csv", FIG / "confusion_matrices.png"],
                next="Analyse thresholds, robustness over time and which features drive the predictions."),
        9: dict(gantt="Results Analysis and Dissertation Writing (start)",
                body=[
                    f"This week I analysed the results further. Choosing the threshold on validation data instead of "
                    f"using 0.5 raised Logistic Regression from F1 {f3(thr.loc['Logistic Regression', 'default_f1'])} to "
                    f"{f3(thr.loc['Logistic Regression', 'tuned_f1'])}, Decision Tree from {f3(thr.loc['Decision Tree', 'default_f1'])} "
                    f"to {f3(thr.loc['Decision Tree', 'tuned_f1'])}, and Random Forest from {f3(thr.loc['Random Forest', 'default_f1'])} "
                    f"to {f3(thr.loc['Random Forest', 'tuned_f1'])}.",
                    f"When I trained on the first 70% of the time period and tested on the rest, Random Forest kept an F1 "
                    f"of {f3(temp.loc['Random Forest', 'f1'])}, while Decision Tree fell to {f3(temp.loc['Decision Tree', 'f1'])} "
                    f"and Logistic Regression to {f3(temp.loc['Logistic Regression', 'f1'])}. The hour feature made no "
                    f"difference to Random Forest (F1 {f3(hour.loc['With Hour', 'f1'])} with and without it). Training on the "
                    f"full training set took {sc.fit_seconds.iloc[-1]:.1f} seconds. The most important features by permutation "
                    f"were {', '.join(imp.feature.head(5))}. I also started the dissertation outline.",
                ],
                table=None,
                figs=[(FIG / "threshold_tradeoff.png", "Random Forest precision and recall at different thresholds."),
                      (FIG / "shap_summary.png", "SHAP summary for Random Forest.", 10)],
                files=[TAB / "thresholds.csv", TAB / "temporal_split.csv", TAB / "ablation_hour.csv",
                       TAB / "scalability.csv", TAB / "feature_importance.csv", FIG / "feature_importance.png"],
                next="Write the introduction, literature review and methodology chapters."),
        10: dict(gantt="Dissertation Writing",
                 body=[
                     "This week I wrote the introduction, literature review and methodology chapters of the dissertation. "
                     "The literature review uses the fifteen checked papers from Weeks 1 and 2. The methodology explains the "
                     "dataset, the duplicate removal, the single stratified split, the tuning, the imbalance strategies and "
                     "the evaluation measures, so that the study can be repeated exactly.",
                 ],
                 table=([["Chapter", "Status"], ["1. Introduction", "Drafted"], ["2. Literature review", "Drafted"],
                         ["3. Methodology", "Drafted"], ["4. Implementation", "Next week"], ["5. Evaluation", "Next week"],
                         ["6. Discussion and 7. Conclusion", "Next week"]], [7, 7]),
                 figs=[], files=[], next="Write the implementation, evaluation, discussion and conclusion chapters."),
        11: dict(gantt="Dissertation Writing",
                 body=[
                     "This week I completed the full draft. The evaluation chapter reports the main results, the imbalance "
                     "comparison, the threshold analysis, the robustness checks and the explanations. The discussion answers "
                     "each research question and gives recommendations for Irish financial institutions, linked to GDPR, "
                     "PSD2 and the EU AI Act.",
                     "The main message is that Random Forest is the best choice, but the way a model is evaluated matters "
                     "as much as the model itself. Default thresholds, resampling and duplicate rows can all change the "
                     "conclusions.",
                 ],
                 table=None, figs=[(FIG / "confusion_matrices.png", "Confusion matrices of the three models.")], files=[],
                 next="Proofread, check every number against the results files and prepare the final submission."),
        12: dict(gantt="Final Submission",
                 body=[
                     "This is my final submission. It contains the dissertation (dissertation.pdf), the code and the "
                     "results files behind every table and figure. The whole experiment runs with one command, python "
                     "src/pipeline.py, after downloading the dataset from Kaggle, and takes about six minutes.",
                     "Before submitting I checked every number in the dissertation against the results files and confirmed "
                     "that every reference exists and was published in the last two years, apart from the standard method "
                     "references.",
                 ],
                 table=([["File", "Content"], ["dissertation.pdf", "Final dissertation"], ["project/src/pipeline.py", "Full experiment"],
                         ["project/results/", "Tables and figures"], ["project/README.md", "How to reproduce"]], [6, 8]),
                 figs=[], files=[], next=None),
    }


def build(n, w):
    out = ROOT / f"Week{n}_Submission"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    s = [Paragraph(f"Week {n} Report: {w['gantt']}", H1),
         Paragraph(f"Project: {TOPIC}<br/>Student: {STUDENT}<br/>Supervisor: Dr. Prasanth Nayak", B),
         Paragraph("What I did this week", H2)] + [Paragraph(x, B) for x in w["body"]]
    if w["table"]:
        s += tbl(*w["table"])
    for f in w["figs"]:
        s += img(f[0], f[1], *(f[2:] or [14]))
    if w["next"]:
        s += [Paragraph("Next week", H2), Paragraph(w["next"], B)]
    SimpleDocTemplate(str(out / f"Week{n}_Report.pdf"), pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                      topMargin=2 * cm, bottomMargin=2 * cm, title=f"Week {n} Report, {STUDENT}").build(s)
    for f in list(w["files"]) + [f[0] for f in w["figs"]]:
        shutil.copy(f, out / Path(f).name)
    if n == 12:
        shutil.copy(ROOT / "report" / "dissertation.pdf", out / "dissertation.pdf")
        dst = out / "project"
        dst.mkdir()
        for d in ["src", "results", "notebooks"]:
            shutil.copytree(PROJ / d, dst / d, ignore=shutil.ignore_patterns("__pycache__", ".omc", "*.pyc", "*.log"))
        for f in ["README.md", "requirements.txt"]:
            shutil.copy(PROJ / f, dst / f)
    shutil.make_archive(str(ROOT / f"Yashwanth_Week{n}_Submission"), "zip", ROOT, out.name)


if __name__ == "__main__":
    for n, w in weeks().items():
        build(n, w)
        print("built week", n)
