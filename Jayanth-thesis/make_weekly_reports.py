"""Builds the Week 3 to Week 12 submissions for Jayanth Akarapu.

His Gantt chart is monthly (Aug to Dec). The weekly submissions follow its phases in
order: preprocessing, model development, evaluation, result analysis, report writing,
final submission. Every number is read from results/ (written by src/pipeline.py).

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
RES, FIG = ROOT / "results", ROOT / "figures"
STUDENT, TOPIC = "Jayanth Akarapu", ("Analysing the Role of Big Data Analytics for Cyber Threat Detection and "
                                     "Prevention in Banking Organisations of Ireland")

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


def f3(x):
    return f"{x:.3f}"


def weeks():
    eda = json.loads((RES / "eda_summary.json").read_text())
    meta = json.loads((RES / "run_meta.json").read_text())
    rule = json.loads((RES / "rule_baseline.json").read_text())
    test = pd.read_csv(RES / "test_results.csv").set_index("model")
    cv = pd.read_csv(RES / "cv_results.csv").set_index("model")
    tune = pd.read_csv(RES / "tuning.csv").set_index("model")
    mc = pd.read_csv(RES / "mcnemar.csv")
    imb = pd.read_csv(RES / "imbalance.csv").set_index("strategy")
    abl = pd.read_csv(RES / "ablation.csv").set_index("feature_set")
    temp = pd.read_csv(RES / "temporal_split.csv")
    grp = pd.read_csv(RES / "unseen_merchant.csv").set_index("model")
    scal = pd.read_csv(RES / "scalability.csv")
    ch = pd.read_csv(RES / "channel_rates.csv").set_index("channel")
    imp = pd.read_csv(RES / "rf_feature_importance.csv", index_col=0)["importance"]
    sv = scal[scal.rows == scal.rows.max()].set_index("model")["fit_seconds"]
    t = lambda m, k: test.loc[m, k]

    return {
        3: dict(gantt="Literature Review (final part) and Data Preprocessing (start)",
                body=[
                    "This week I finished the reading part of the literature review and started preprocessing. I added "
                    "four recent papers on banking fraud and intrusion detection to my review: Sanda et al. (2026), "
                    "Dhammayogi and Pramartha (2026), Baisholan et al. (2025) and Pospichal et al. (2026). All of them find "
                    "tree ensembles such as Random Forest and XGBoost at or near the top, which matches my plan.",
                    f"For preprocessing I parsed the date column into year, month, day and day of week, and split the "
                    f"description field into a channel (for example NETTXN, IMPS, PCA) and the merchant. I also added the "
                    f"log of the amount and the ratio of amount to balance, because amounts vary over several orders of "
                    f"magnitude. The {eda['rows']:,} rows had no missing values, so no rows were dropped. Finally I created "
                    f"one stratified 80/20 split with a fixed seed ({meta['seed']}): {meta['train_rows']:,} training rows and "
                    f"{meta['test_rows']:,} test rows. Every later experiment uses this split.",
                ],
                table=([["Step", "What I did"],
                        ["Dates", "Parsed dd-mm-yyyy; added year, month, day, day of week"],
                        ["Description", "Split into channel and merchant; one-hot encoded"],
                        ["Amounts", "Single amount column, log amount, amount to balance ratio"],
                        ["Scaling", "Standard scaling fitted on the training split only"],
                        ["Split", f"Stratified 80/20, seed {meta['seed']}"]], [4, 12]),
                figs=[], files=[],
                next="Finish the exploratory analysis of the cleaned data and look at how the suspicious rate changes by channel."),
        4: dict(gantt="Data Preprocessing",
                body=[
                    f"This week I explored the cleaned data. {eda['suspicious']:,} of {eda['rows']:,} transactions "
                    f"({eda['suspicious_rate']:.1%}) are flagged suspicious, and the data runs from {eda['date_min']} to "
                    f"{eda['date_max']}.",
                    f"The most useful finding was the channel. Seven channels, including ATM withdrawals, cash deposits, "
                    f"IMPS and fund transfers, are never flagged. Crypto exchanges are flagged in "
                    f"{ch.loc['CRYPTOEXCHANGE', 'mean']:.0%} of rows and NETTXN online payments in "
                    f"{ch.loc['NETTXN', 'mean']:.0%}. This means the labels are strongly tied to the channel, which I need "
                    f"to keep in mind when I judge how good the models really are.",
                ],
                table=([["Channel", "Rows", "Suspicious rate"]] +
                       [[c, f"{int(ch.loc[c, 'size']):,}", f"{ch.loc[c, 'mean']:.1%}"] for c in ch.sort_values("size", ascending=False).index[:8]],
                       [5, 3, 4]),
                figs=[("suspicious_rate_by_channel.png", "Suspicious rate by channel."),
                      ("monthly_trend.png", "Transactions and suspicious rate by month.")],
                files=["eda_summary.json", "channel_rates.csv"],
                next="Train the first versions of Decision Tree, Random Forest and SVM, plus simple baselines."),
        5: dict(gantt="Data Preprocessing (end) and Model Development (start)",
                body=[
                    "This week I finished preprocessing and built the first models. As planned in my proposal I use "
                    "Decision Tree, Random Forest and SVM. I also added Logistic Regression and Gradient Boosting as "
                    "reference models, and a simple rule so I can see how much machine learning adds.",
                    f"The rule is learnt from the training data only. It flags a transaction if its merchant has any "
                    f"suspicious history in training and the amount is above {rule['amount_threshold']:,.0f}. "
                    f"{len(rule['risky_descriptions'])} merchants count as risky. On the test set this rule already reaches "
                    f"an F1 of {f3(t('Rule baseline', 'f1'))}, which is very close to the machine learning models. This "
                    f"is an important result for my research question on effectiveness.",
                ],
                table=None, figs=[], files=["rule_baseline.json"],
                next="Tune each model with cross-validation on the training split."),
        6: dict(gantt="Model Development",
                body=[
                    "This week I tuned the models with 5-fold cross-validation on the training split only, so the test "
                    "set stays untouched. I used F1 as the tuning score because both missed threats and false alarms "
                    "matter. The table shows the chosen settings and the cross-validated F1.",
                    f"Decision Tree and Random Forest reach the same cross-validated F1 of {f3(cv.loc['Decision Tree', 'f1_mean'])}, "
                    f"with a very small spread across folds (standard deviation {f3(cv.loc['Decision Tree', 'f1_sd'])}). SVM "
                    f"is a little lower at {f3(cv.loc['SVM (RBF)', 'f1_mean'])}.",
                ],
                table=([["Model", "Best settings", "CV F1"]] +
                       [[m, tune.loc[m, "best_params"].replace('"clf__', '"').replace('"', ''), f3(tune.loc[m, "cv_f1"])] for m in tune.index],
                       [4, 8, 3]),
                figs=[], files=["tuning.csv", "cv_results.csv"],
                next="Evaluate the tuned models once on the held-out test set and compare them statistically."),
        7: dict(gantt="Model Development (end) and Model Evaluation (start)",
                body=[
                    f"This week I evaluated all tuned models once on the {meta['test_rows']:,} test rows. Decision Tree and "
                    f"Random Forest are tied at F1 {f3(t('Decision Tree', 'f1'))} with recall {f3(t('Decision Tree', 'recall'))}. "
                    f"SVM is the weakest at F1 {f3(t('SVM (RBF)', 'f1'))} and also the slowest to train.",
                    "To check whether the differences are real I used McNemar's test on the test predictions. Decision "
                    "Tree is significantly better than Logistic Regression and SVM (p below 0.001), but not different from "
                    "Random Forest or Gradient Boosting.",
                ],
                table=([["Model", "Precision", "Recall", "F1", "ROC-AUC"]] +
                       [[m, f3(t(m, "precision")), f3(t(m, "recall")), f3(t(m, "f1")), f3(t(m, "roc_auc")) if m != "Rule baseline" else "n/a"] for m in test.index],
                       [4.5, 2.5, 2.5, 2.5, 2.5]),
                figs=[("roc_pr_curves.png", "ROC and precision-recall curves on the test set.")],
                files=["test_results.csv", "mcnemar.csv"],
                next="Test the effect of class imbalance handling, the decision threshold and each feature group."),
        8: dict(gantt="Model Evaluation",
                body=[
                    f"This week I checked what drives the results. First, imbalance handling makes no difference here: "
                    f"Random Forest reaches F1 {f3(imb.loc['No re-balancing', 'f1'])} with no re-balancing, with class weights "
                    f"and with SMOTE. That makes sense because {eda['suspicious_rate']:.0%} of rows are suspicious, so the "
                    f"data is not strongly imbalanced.",
                    f"Second, the ablation shows where the signal is. Without the description and channel, F1 falls to "
                    f"{f3(abl.loc['Without description/channel', 'f1'])}. With amount and balance only it is "
                    f"{f3(abl.loc['Amount & balance only', 'f1'])}. The models depend heavily on which merchant the "
                    f"transaction is with.",
                ],
                table=([["Feature set", "F1", "ROC-AUC"]] + [[k, f3(abl.loc[k, "f1"]), f3(abl.loc[k, "roc_auc"])] for k in abl.index],
                       [7, 3, 3]),
                figs=[("threshold_tradeoff.png", "Precision and recall of the best model at different thresholds.")],
                files=["imbalance.csv", "ablation.csv", "thresholds.csv"],
                next="Run the robustness tests: a time-based split and a test on merchants the model has never seen."),
        9: dict(gantt="Result Analysis",
                body=[
                    f"This week I analysed how well the results would hold up in practice. When I train on transactions up "
                    f"to {temp.train_until.iloc[0]} and test on later ones, the tree models stay near perfect, but SVM drops "
                    f"to F1 {f3(temp.query('model == \"SVM (RBF)\" and feature_set == \"All features\"').f1.iloc[0])} because it "
                    f"leans on date features.",
                    f"The hardest test holds out whole merchants. On merchants never seen in training, F1 falls to between "
                    f"{f3(grp.f1.min())} and {f3(grp.f1.max())}. So the near-perfect test scores come mostly from memorising "
                    f"risky merchants. For the explanation I used Random Forest importance and SHAP. The top features are "
                    f"the amount, the log amount and the NETTXN and crypto channels. Training time grows slowly for the trees "
                    f"but quickly for SVM ({sv['SVM (RBF)']:.1f} s against {sv['Decision Tree']:.2f} s for Decision Tree on "
                    f"the full training set).",
                ],
                table=([["Model", "F1 on unseen merchants", "ROC-AUC"]] + [[m, f3(grp.loc[m, "f1"]), f3(grp.loc[m, "roc_auc"])] for m in grp.index],
                       [5, 5, 3]),
                figs=[("shap_summary.png", "SHAP summary for the Random Forest.", 11),
                      ("scalability.png", "Training time as the training set grows.")],
                files=["temporal_split.csv", "unseen_merchant.csv", "rf_feature_importance.csv", "scalability.csv"],
                next="Start writing the report: introduction, related work and methodology."),
        10: dict(gantt="Report Writing",
                 body=[
                     "This week I started the final report. I wrote the introduction, the related work section and the "
                     "methodology. The related work now uses the checked papers from my literature review, and I corrected "
                     "some citation details, such as the year of Ofoegbu et al. and what Ali et al. (2022) actually found.",
                     "In the methodology I describe the dataset, the preprocessing steps, the single fixed train and test "
                     "split, the tuning procedure and the statistical tests, so that someone else could repeat the study.",
                 ],
                 table=([["Section", "Status"], ["Introduction", "Drafted"], ["Related work", "Drafted with checked sources"],
                         ["Methodology", "Drafted"], ["Design and implementation", "Next week"], ["Evaluation and discussion", "Next week"]], [7, 7]),
                 figs=[], files=[], next="Write the design, implementation, evaluation and discussion sections."),
        11: dict(gantt="Report Writing",
                 body=[
                     "This week I wrote the design, implementation, evaluation and discussion sections, so the report is now "
                     "a complete draft. The evaluation section reports the test results, the McNemar tests and all the "
                     "robustness experiments. The discussion answers each research question and gives recommendations for "
                     "Irish banks, linking the results to GDPR, DORA and the EU AI Act.",
                     f"The main message is that very high scores (F1 {f3(t('Decision Tree', 'f1'))}) are possible on this data, "
                     f"but a simple rule gets almost the same result and the models drop to about "
                     f"{f3(grp.f1.mean())} on new merchants. Banks should use big data analytics to find and maintain simple, "
                     f"auditable risk rules, and test models on new merchants and later time periods before trusting them.",
                 ],
                 table=None, figs=[("confusion_matrices.png", "Confusion matrices of the tuned models.")], files=[],
                 next="Proofread, check every number against the results files, and prepare the final submission."),
        12: dict(gantt="Final Submission",
                 body=[
                     "This is my final submission. It contains the final report (thesis.pdf), the full code, and the "
                     "results files behind every table and figure. The whole experiment can be repeated with one command, "
                     "python src/pipeline.py, after downloading the dataset from Kaggle.",
                     "Before submitting I checked every number in the report against the results files, confirmed that all "
                     "references exist, and removed the old draft files.",
                 ],
                 table=([["File", "Content"], ["thesis.pdf", "Final report"], ["src/pipeline.py", "Full experiment"],
                         ["notebooks/analysis.ipynb", "Executed notebook"], ["results/", "CSV and JSON results"],
                         ["figures/", "All report figures"], ["README.md", "How to reproduce"]], [5, 9]),
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
        s += img(FIG / f[0], f[1], *(f[2:] or [14]))
    if w["next"]:
        s += [Paragraph("Next week", H2), Paragraph(w["next"], B)]
    SimpleDocTemplate(str(out / f"Week{n}_Report.pdf"), pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                      topMargin=2 * cm, bottomMargin=2 * cm, title=f"Week {n} Report, {STUDENT}").build(s)
    for f in w["files"]:
        shutil.copy(RES / f, out / f)
    for f in w["figs"]:
        shutil.copy(FIG / f[0], out / f[0])
    if n == 12:
        shutil.copy(ROOT / "report" / "thesis.pdf", out / "thesis.pdf")
        for d in ["src", "notebooks", "results", "figures"]:
            shutil.copytree(ROOT / d, out / d, ignore=shutil.ignore_patterns("__pycache__", ".omc", "*.pyc"))
        for f in ["README.md", "requirements.txt"]:
            shutil.copy(ROOT / f, out / f)
    shutil.make_archive(str(ROOT / f"Jayanth_Week{n}_Submission"), "zip", ROOT, out.name)


if __name__ == "__main__":
    for n, w in weeks().items():
        build(n, w)
        print("built week", n)
