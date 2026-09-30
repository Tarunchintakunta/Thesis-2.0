"""Week 2 deliverables for Yashwanth.

Gantt chart (CA2 proposal, Figure 1), Week 2 activities: Literature Review (W1-W3)
and Dataset Collection (W2-W3).
Run from anywhere:  python Week2_Submission/week2.py
Outputs (next to this file): dataset_profile.json, data_dictionary.csv,
figures/*.png and Week2_Report.pdf.
"""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "project" / "data" / "creditcard.csv"
FIG = HERE / "figures"
KAGGLE_ID = "mlg-ulb/creditcardfraud"


# ---------------------------------------------------------------- dataset work
def profile():
    raw = DATA.read_bytes()
    df = pd.read_csv(DATA)
    y = df["Class"]
    dup = df.duplicated()
    counts = y.value_counts().to_dict()
    corr = df.corr()["Class"].drop("Class").abs().sort_values(ascending=False)
    hour = (df["Time"] // 3600) % 24
    v = df[[f"V{i}" for i in range(1, 29)]]
    p = {
        "file": DATA.name,
        "size_mb": round(len(raw) / 1e6, 1),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(dup.sum()),
        "duplicate_fraud_rows": int((dup & (y == 1)).sum()),
        "class_counts": {str(k): int(v_) for k, v_ in counts.items()},
        "class_counts_dedup": {str(k): int(v_) for k, v_ in y[~dup].value_counts().items()},
        "fraud_rate_pct": round(float(y.mean() * 100), 3),
        "imbalance_ratio": round(counts[0] / counts[1], 1),
        "time_span_hours": round(float(df["Time"].max() / 3600), 1),
        "zero_amount_rows": int((df["Amount"] == 0).sum()),
        "amount_max": round(float(df["Amount"].max()), 2),
        "median_amount_by_class": {str(k): round(float(x), 2) for k, x in df.groupby("Class")["Amount"].median().items()},
        "mean_amount_by_class": {str(k): round(float(x), 2) for k, x in df.groupby("Class")["Amount"].mean().items()},
        "max_fraud_amount": round(float(df.loc[y == 1, "Amount"].max()), 2),
        "pca_abs_mean_max": round(float(v.mean().abs().max()), 6),
        "pca_std_range": [round(float(v.std().min()), 3), round(float(v.std().max()), 3)],
        "top_corr_with_class": {k: round(float(x), 3) for k, x in corr.head(6).items()},
        "night_fraud_rate_pct": round(float(y[hour < 6].mean() * 100), 3),
        "day_fraud_rate_pct": round(float(y[hour >= 6].mean() * 100), 3),
    }
    # sanity checks so the report never quotes numbers that do not add up
    assert sum(p["class_counts"].values()) == p["rows"]
    assert sum(p["class_counts_dedup"].values()) == p["rows"] - p["duplicate_rows"]
    assert p["pca_abs_mean_max"] < 1e-3, "V1-V28 should be centred PCA components"
    return df, hour, corr, p


def data_dictionary(df):
    rows = []
    for c in df.columns:
        s = df[c]
        meaning = {"Time": "Seconds since the first transaction in the file",
                   "Amount": "Transaction amount (EUR, not scaled)",
                   "Class": "Target label: 1 = fraud, 0 = legitimate"}.get(c, "PCA component of anonymised original features")
        rows.append({"column": c, "dtype": str(s.dtype), "role": "target" if c == "Class" else "feature",
                     "missing": int(s.isna().sum()), "unique": int(s.nunique()),
                     "min": round(float(s.min()), 2), "max": round(float(s.max()), 2),
                     "mean": round(float(s.mean()), 3), "std": round(float(s.std()), 3), "meaning": meaning})
    return pd.DataFrame(rows)


def figures(df, hour, corr):
    FIG.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

    c = df["Class"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(["Legitimate (0)", "Fraud (1)"], c.values, color=["#4C72B0", "#C44E52"])
    ax.set_yscale("log")
    for i, v in enumerate(c.values):
        ax.text(i, v * 1.15, f"{v:,} ({v / c.sum():.3%})", ha="center", va="bottom")
    ax.set_ylabel("Transactions (log scale)"); ax.set_ylim(100, c.max() * 5); ax.set_title("Class distribution")
    fig.tight_layout(); fig.savefig(FIG / "w2_class_balance.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 3))
    bins = np.linspace(0, np.log10(df["Amount"].max() + 1), 50)
    for lab, colr, name in [(0, "#4C72B0", "Legitimate"), (1, "#C44E52", "Fraud")]:
        ax.hist(np.log10(df.loc[df.Class == lab, "Amount"] + 1), bins=bins, density=True, alpha=.6, color=colr, label=name)
    ax.set_xlabel("log10(Amount + 1)"); ax.set_ylabel("Density"); ax.legend(frameon=False)
    ax.set_title("Transaction amount by class")
    fig.tight_layout(); fig.savefig(FIG / "w2_amounts.png", dpi=160); plt.close(fig)

    h = df.groupby(hour)["Class"].agg(["size", "mean"])
    fig, ax = plt.subplots(figsize=(6.5, 3))
    ax.bar(h.index, h["size"], color="#4C72B0", alpha=.7); ax.set_xlabel("Hour of day (from Time, mod 24)")
    ax.set_ylabel("Transactions")
    ax2 = ax.twinx(); ax2.plot(h.index, h["mean"] * 100, color="#C44E52", marker="o", ms=3)
    ax2.set_ylabel("% fraud", color="#C44E52"); ax.set_title("Volume (bars) and fraud rate (line) by hour")
    fig.tight_layout(); fig.savefig(FIG / "w2_hourly.png", dpi=160); plt.close(fig)

    top = corr.head(10).sort_values()
    fig, ax = plt.subplots(figsize=(6.5, 3))
    ax.barh(top.index, top.values, color="#C44E52")
    ax.set_xlabel("|Pearson correlation| with Class"); ax.set_title("Ten features most correlated with fraud")
    fig.tight_layout(); fig.savefig(FIG / "w2_top_corr.png", dpi=160); plt.close(fig)


# ---------------------------------------------------------------- report
ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=15, textColor=colors.HexColor("#1F3864"), spaceAfter=6)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=12, textColor=colors.HexColor("#2E75B6"), spaceBefore=8)
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=9.5, leading=13.5, alignment=TA_JUSTIFY, spaceAfter=5)
C = ParagraphStyle("C", parent=B, fontSize=8, leading=10, alignment=0, spaceAfter=0)
CAP = ParagraphStyle("CAP", parent=B, fontSize=8.5, textColor=colors.grey, alignment=1)


def table(rows, widths):
    t = Table([[Paragraph(str(c), C) for c in r] for r in rows], colWidths=[w * cm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#BFBFBF")),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F2")),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FC")])]))
    return t


def fig(name, caption, w=15):
    img = Image(str(FIG / name)); img.drawHeight = img.drawHeight * (w * cm) / img.drawWidth; img.drawWidth = w * cm
    return [img, Paragraph(caption, CAP), Spacer(1, 6)]


def P(text):
    return Paragraph(text, B)


def footer(canvas, doc):
    canvas.saveState(); canvas.setFont("Helvetica", 7.5); canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.2 * cm, "Week 2 - Literature Review (continued) and Dataset Collection | Yashwanth")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}"); canvas.restoreState()


def report(p, dd):
    cc, cd = p["class_counts"], p["class_counts_dedup"]
    s = []
    s += [Spacer(1, 3 * cm), Paragraph("Week 2 Progress Report", H1),
          Paragraph("Literature Review (continued) and Dataset Collection", H2), Spacer(1, 10),
          P("<b>Project:</b> Determining the Role of Big Data Applications in Fraud Detection and Financial Security "
            "in Financial Institutions of Ireland"),
          P("<b>Student:</b> Yashwanth"), P("<b>Course:</b> Open Data Practice - Research Practicum"),
          P("<b>Supervisor:</b> Dr. Prasanth Nayak"),
          P("<b>Gantt activities this week (W2):</b> Literature Review (W1-W3), Dataset Collection (W2-W3)"),
          Spacer(1, 14),
          table([["Section", "Content"],
                 ["1", "Week 2 scope against the project Gantt chart"],
                 ["2", "Literature review: thematic synthesis, method comparison matrix, refined gaps"],
                 ["3", "Dataset collection: selection, acquisition, data dictionary, quality audit, first look"],
                 ["4", "Ethics and data governance"],
                 ["5", "Progress status, risks and Week 3 plan"]], [2, 13]),
          PageBreak()]

    # 1 scope
    s += [Paragraph("1. Week 2 Scope", H1),
          P("The project Gantt chart (CA2 proposal, Section 3.7, Figure 1) plans twelve weeks. Literature Review runs "
            "W1-W3 and Dataset Collection runs W2-W3; Data Preprocessing starts in W3 and Exploratory Data Analysis "
            "in W4. Week 2 therefore has two tasks: turn the Week 1 paper summaries into a critical synthesis, and "
            "obtain, verify and document the dataset. Full EDA is left for W4 as planned; Section 3.6 gives only "
            "the first-look checks needed to plan preprocessing."),
          table([["Gantt activity", "Planned weeks", "Week 2 target", "Status"],
                 ["Literature Review", "W1-W3", "Thematic synthesis, comparison matrix, refined gaps", "On track"],
                 ["Dataset Collection", "W2-W3", "Dataset selected, downloaded, verified and documented", "Ahead (core done)"],
                 ["Data Preprocessing", "W3-W4", "Not started; issues logged in Section 3.6 feed it", "Next week"],
                 ["Exploratory Data Analysis", "W4-W5", "First-look checks only", "Planned"]],
                [3.5, 2.5, 6.5, 2.5])]

    # 2 literature
    s += [Paragraph("2. Literature Review (continued)", H1),
          Paragraph("2.1 Thematic synthesis", H2),
          P("Week 1 summarised 15 papers (2023-2026) one at a time. This week they were compared with each other. "
            "Five findings shape the study design."),
          P("<b>(a) Random Forest is the consistent leader, Logistic Regression the recall baseline.</b> Random "
            "Forest gives the best F1 in Papers 4, 5, 7, 8, 13 and 15, and the reviews (Papers 3, 9, 14) report the "
            "same pattern: median F1 of about 0.82 for ensembles against 0.65 for single classifiers (Paper 3). "
            "Logistic Regression often has the highest recall but low precision (Papers 4, 6). This supports the "
            "proposal's comparison of Logistic Regression, Decision Tree and Random Forest."),
          P("<b>(b) SMOTE trades precision for recall, and the timing matters.</b> SMOTE raised Random Forest F1 "
            "from 0.82 to 0.91 but lowered precision from 0.93 to 0.87 (Paper 7), and raised recall from 0.76 to "
            "0.92 (Paper 8). Most papers do not say whether SMOTE was applied before or after the train-test split. "
            "Applying it before the split leaks synthetic copies of test frauds into training and inflates scores. "
            "This study will resample the training fold only and compare against class weights."),
          P("<b>(c) Metric choice changes the conclusion.</b> With 0.17% fraud, a model that flags nothing scores "
            "99.8% accuracy. Papers 6 and 9 show accuracy is misleading; Paper 9 recommends PR-AUC, and Paper 8 adds "
            "MCC. Precision, recall, F1, PR-AUC and MCC will be the primary metrics, with accuracy reported only "
            "for comparison with earlier work."),
          P("<b>(d) One benchmark dominates.</b> Papers 4-8, 13 and 15 all use the same Kaggle credit card dataset. "
            "This makes results comparable, but Paper 3 notes that it limits generalisation. The PCA features also "
            "limit explanation: V14, V12, V10 and V17 are the top predictors (Paper 15) but have no business meaning. "
            "None of the papers report the duplicate rows found in Section 3.4."),
          P("<b>(e) Big data and regulation are discussed mainly for the US.</b> Papers 1, 10, 11 and 12 connect "
            "detection to Spark pipelines, compliance audit trails, sub-50 ms scoring and customer trust, but in US "
            "or general settings. The Irish angle (Central Bank of Ireland fraud statistics, GDPR Article 22, PSD2 "
            "Strong Customer Authentication) is still missing from the literature. This is the study's main niche."),
          Paragraph("2.2 Method comparison matrix", H2),
          table([["#", "Study", "Models", "Data", "Class balance", "Reported result", "Use here"],
                 ["1*", "Jamil et al. 2025", "Spark MLlib, Flink, MapReduce + RF", "US financial data", "n/s", "F1 0.89; FP -35%", "Big data framing"],
                 ["2", "Elumilade et al. 2025", "Conceptual framework", "Case studies", "n/a", "Detection 2.5x faster", "Business value"],
                 ["3", "Gkegkas et al. 2025", "Systematic review (80+)", "Mostly Kaggle, IEEE-CIS", "Discussed", "Ensemble F1 0.82 vs 0.65", "Model choice"],
                 ["4*", "Salunke et al. 2025", "LR, DT, RF", "Kaggle ULB", "Class weights", "RF F1 0.85; LR recall 0.92", "Primary baseline"],
                 ["5*", "Saeed & Abdulazeez 2024", "KNN, RF, LR", "Kaggle ULB", "n/s", "RF AUC 0.98, F1 0.86", "Benchmark"],
                 ["6", "Appavu 2025", "LR, DT", "Kaggle ULB", "n/s", "LR recall 0.89; DT 0.78", "Metric warning"],
                 ["7*", "Andrade-Arenas & Yactayo-Arias 2025", "LR, DT, RF, SVM", "Kaggle ULB", "SMOTE vs RUS/ROS", "RF F1 0.82 to 0.91", "Resampling design"],
                 ["8", "Aghware et al. 2024", "RF + SMOTE / ADASYN", "Kaggle ULB", "SMOTE", "Recall 0.76 to 0.92; MCC", "Extra metric"],
                 ["9", "Baisholan et al. 2025", "Review (50+)", "Various", "Original imbalance", "Ensemble F1 0.78 vs 0.45", "PR-AUC choice"],
                 ["10", "Chowdhury et al. 2025", "ML + compliance checks", "Synthetic banking", "n/s", "94% fraud detected", "Regulation"],
                 ["11", "Khan et al. 2026", "RF, XGBoost, LSTM", "FinTech transactions", "n/s", "RF F1 0.84; < 50 ms", "Real-time angle"],
                 ["12", "Mensa & Akinsanya 2026", "Mixed methods", "US survey (500+)", "n/a", "Trust +28%", "Trust / ROI"],
                 ["13", "Haider et al. 2024", "PCA + SMOTE + LR, DT, RF, SVM", "Kaggle ULB", "SMOTE", "RF F1 0.93, AUC 0.99", "Upper reference"],
                 ["14", "Bian 2025", "Review: ML, ensembles, DL", "Various", "Discussed", "DL +2-5% F1 only", "Interpretability"],
                 ["15*", "Afriyie et al. 2023", "DT, RF, LR, NB, SVM", "Kaggle ULB", "Stratified k-fold", "RF F1 0.86; V14 top", "Feature check"]],
                [0.8, 2.9, 2.9, 2.3, 1.8, 2.6, 2.1]),
          Paragraph("* baseline paper. n/s = not stated; n/a = not a classification experiment.", CAP),
          Paragraph("2.3 Refined research gaps and link to research questions", H2),
          table([["Gap from the synthesis", "How this study responds", "RQ"],
                 ["G1. SMOTE timing is unreported, so gains may be leakage",
                  "Resample the training fold only; compare with class weights on the same split", "RQ1"],
                 ["G2. Accuracy-led reporting hides poor fraud detection",
                  "Precision, recall, F1, PR-AUC and MCC as primary metrics", "RQ1"],
                 ["G3. Duplicate rows in the benchmark are never discussed",
                  "Report results with duplicates removed before the split (Section 3.4)", "RQ1, RQ3"],
                 ["G4. PCA features give little explanation to regulators",
                  "Feature importance plus a discussion of GDPR Article 22 explanation needs", "RQ2"],
                 ["G5. No Irish grounding of big data fraud detection",
                  "Use Central Bank of Ireland statistics as context; Irish recommendations", "RQ2, RQ3"]],
                [5.5, 7.5, 2]),
          PageBreak()]

    # 3 dataset
    s += [Paragraph("3. Dataset Collection", H1),
          Paragraph("3.1 Selection criteria and candidates", H2),
          P("Five criteria were set before choosing: (1) labelled card or payment transactions, (2) an open licence "
            "for academic use, (3) European origin where possible, (4) no personal data, and (5) comparability with "
            "the baseline papers. Four candidates were assessed."),
          table([["Candidate", "Type", "Size", "Fraud rate", "Licence", "Decision"],
                 ["Credit Card Fraud Detection (ULB, Kaggle)", "Real European card transactions, Sept 2013",
                  f"{p['rows']:,} rows", f"{p['fraud_rate_pct']}%", "DbCL-1.0",
                  "<b>Selected</b>: named in the proposal, used by 7 of 15 papers, European, anonymised"],
                 ["IEEE-CIS Fraud Detection (Kaggle)", "Real e-commerce transactions", "about 590k rows", "about 3.5%",
                  "Competition rules", "Rejected: competition-only licence, many raw identity fields"],
                 ["PaySim (Lopez-Rojas et al., 2016)", "Simulated mobile money", "6.36M rows", "about 0.13%",
                  "CC BY-SA 4.0", "Reserve: synthetic, not card payments"],
                 ["Bank Account Fraud (Jesus et al., 2022)", "Synthetic account applications", "1M rows per variant",
                  "about 1%", "CC BY-NC-SA 4.0", "Reserve: application fraud, not transactions"]],
                [3.4, 3, 2, 1.6, 2, 4]),
          P("For Irish context the Central Bank of Ireland payment fraud statistics (2022-2024) were also collected. "
            "They are aggregate figures, used in the introduction and discussion, not for model training: EUR 160 "
            "million of fraudulent payments and about 815,000 fraudulent transactions in 2024 (centralbank.ie, 2025)."),
          Paragraph("3.2 Acquisition and verification", H2),
          P(f"The dataset was downloaded with the Kaggle API: <font face='Courier'>kaggle datasets download -d "
            f"{KAGGLE_ID} --unzip -p project/data</font>. Kaggle metadata lists the licence as DbCL-1.0 (Database "
            f"Contents License). The file <font face='Courier'>{p['file']}</font> is {p['size_mb']} MB. Its SHA-256 "
            f"checksum is recorded so later weeks can prove the same file is used:"),
          Paragraph(f"<font face='Courier' size='7.5'>{p['sha256']}</font>", B),
          Paragraph("3.3 Data dictionary", H2),
          P("V1-V28 are principal components produced by the data owners to protect cardholder confidentiality; the "
            "original features are not released. Only Time and Amount keep their original meaning. The full "
            "31-column dictionary is in data_dictionary.csv; the table below shows the non-PCA columns and the "
            "V1-V28 group."),
          table([["Column", "Type", "Missing", "Min", "Max", "Mean", "Meaning"]] +
                [[r["column"], r["dtype"], r["missing"], r["min"], r["max"], r["mean"], r["meaning"]]
                 for _, r in dd[dd.column.isin(["Time", "Amount", "Class"])].iterrows()] +
                [["V1-V28", "float64", 0, round(dd[dd.column.str.match(r"V\d")]["min"].min(), 2),
                  round(dd[dd.column.str.match(r"V\d")]["max"].max(), 2), "0 (centred)",
                  f"PCA components; std from {p['pca_std_range'][1]} (V1) down to {p['pca_std_range'][0]}"]],
                [1.8, 1.5, 1.4, 1.6, 1.9, 1.7, 5.1]),
          Paragraph("3.4 Initial quality audit", H2),
          table([["Check", "Result", "Implication"],
                 ["Rows x columns", f"{p['rows']:,} x {p['columns']}", "Fits in memory; all three models train in minutes"],
                 ["Missing cells", f"{p['missing_cells']}", "No imputation needed"],
                 ["Exact duplicate rows", f"{p['duplicate_rows']:,} ({p['duplicate_fraud_rows']} of them fraud)",
                  "Remove before splitting, or copies land in both train and test"],
                 ["After de-duplication", f"{cd['0']:,} legitimate, {cd['1']:,} fraud", "This becomes the modelling set"],
                 ["Time span", f"0 to {p['time_span_hours']} hours (two days)", "Too short for a month-level time split"],
                 ["Zero-amount transactions", f"{p['zero_amount_rows']:,}", "Keep; card checks are a known fraud pattern"],
                 ["Amount range", f"0 to {p['amount_max']:,}; not scaled", "Scale Amount (and Time) like V1-V28"],
                 ["V1-V28 centring", f"max |mean| = {p['pca_abs_mean_max']}", "Already centred; no further scaling needed"]],
                [4, 5, 6]),
          Paragraph("3.5 Class distribution", H2),
          P(f"Only {cc['1']:,} of {p['rows']:,} transactions ({p['fraud_rate_pct']}%) are fraud: one fraud per "
            f"{p['imbalance_ratio']:.0f} legitimate transactions. A model that predicts 'legitimate' every time would "
            f"reach {100 - p['fraud_rate_pct']:.2f}% accuracy, which confirms gap G2. The split must be stratified so "
            f"the test set keeps its fraud cases."),
          *fig("w2_class_balance.png", "Figure 1. Class distribution (log scale).", 9),
          PageBreak(),
          Paragraph("3.6 First look at the data", H2),
          P(f"Fraud amounts are skewed toward small values: the median fraud is {p['median_amount_by_class']['1']} "
            f"against {p['median_amount_by_class']['0']} for legitimate transactions, although the fraud mean is "
            f"higher ({p['mean_amount_by_class']['1']} against {p['mean_amount_by_class']['0']}) because of a long "
            f"tail. The largest fraud is {p['max_fraud_amount']:,}. This fits small 'test' charges followed by "
            f"larger ones (Figure 2)."),
          *fig("w2_amounts.png", "Figure 2. Distribution of log10(Amount + 1) by class."),
          P(f"Transactions follow a day-night cycle (Figure 3). Volume drops in the first hours of each day, while "
            f"the fraud rate rises: {p['night_fraud_rate_pct']}% in hours 0-5 against {p['day_fraud_rate_pct']}% "
            f"for the rest of the day. An hour-of-day feature derived from Time is therefore worth testing in "
            f"preprocessing."),
          *fig("w2_hourly.png", "Figure 3. Transactions per hour of day (bars) and fraud rate (line)."),
          P("The PCA components most correlated with fraud are " +
            ", ".join(f"{k} ({v})" for k, v in p["top_corr_with_class"].items()) +
            ". This matches the V14/V12/V10/V17 finding of Paper 15, so the downloaded file behaves like the one used "
            "in the baseline literature (Figure 4)."),
          *fig("w2_top_corr.png", "Figure 4. Absolute correlation of each feature with Class (top 10)."),
          Paragraph("Issues logged for Data Preprocessing (W3-W4)", H2),
          table([["#", "Issue", "Planned action"],
                 ["1", f"{p['duplicate_rows']:,} duplicate rows", "Drop before the train-test split"],
                 ["2", "Time and Amount are unscaled", "StandardScaler (or RobustScaler for Amount); fit on training data only"],
                 ["3", "Time is seconds from start", "Derive hour of day; test whether it helps"],
                 ["4", f"{p['imbalance_ratio']:.0f}:1 imbalance", "Stratified 70/30 split (as in config.py); class weights vs SMOTE on training fold"],
                 ["5", "PCA features lack meaning", "Report feature importance; discuss explanation limits"]],
                [0.8, 5.2, 9]),
          ]

    # 4 ethics, 5 status
    s += [Paragraph("4. Ethics and Data Governance", H1),
          P("The dataset contains no names, card numbers or other direct identifiers. The data owners released only "
            "PCA components, Time and Amount to protect cardholder confidentiality, so individuals cannot be "
            "re-identified from the file. It is used under the DbCL-1.0 licence for academic research, stored "
            "locally, not redistributed, and identified by its checksum. The Central Bank of Ireland statistics are "
            "public aggregate figures. Because the transactions are European but not Irish and date from 2013, "
            "results will be presented as evidence about methods, with Irish recommendations drawn from the "
            "literature and Central Bank data rather than claimed from the model."),
          Paragraph("5. Progress, Risks and Week 3 Plan", H1),
          table([["Item", "Status / note"],
                 ["Literature synthesis, comparison matrix, refined gaps", "Done (Section 2)"],
                 ["Dataset selected against written criteria", "Done (Section 3.1)"],
                 ["Dataset downloaded, checksummed, licence checked", "Done (Section 3.2)"],
                 ["Data dictionary and quality audit", "Done; saved as data_dictionary.csv and dataset_profile.json"],
                 ["Irish context data collected", "Done: Central Bank of Ireland 2022-2024 fraud statistics"],
                 ["Risk: 2013 data may not reflect current fraud", "Stated as a limitation; cite recent Irish statistics"],
                 ["Risk: PCA features limit interpretability", "Feature importance plus a regulatory discussion"]],
                [7, 8]),
          Spacer(1, 6),
          P("<b>Week 3 (Literature Review and Dataset Collection finish; Data Preprocessing starts):</b> add 3-5 "
            "papers on resampling leakage and PR-AUC evaluation, and on the Irish/EU regulation of automated fraud "
            "decisions; close dataset collection by recording the final de-duplicated modelling set; start the "
            "preprocessing notebook (drop duplicates, scale Time and Amount, create the stratified split with a fixed "
            "seed and save it for all later experiments)."),
          Paragraph("References", H1)]
    refs = [
        "Afriyie, J.K., Tawiah, K., Pels, W.A., Addai-Henne, S. et al. (2023) 'A Supervised Machine Learning Algorithm for Detecting and Predicting Fraud in Credit Card Transactions', Decision Analytics Journal, 6, 100163.",
        "Aghware, F.O., Ojugo, A.A., Adigwe, W. et al. (2024) 'Enhancing the Random Forest Model via Synthetic Minority Oversampling Technique for Credit-Card Fraud Detection', Journal of Computing Theories and Applications.",
        "Andrade-Arenas, L. and Yactayo-Arias, C. (2025) 'Comparative Analysis of Machine Learning Models for Credit Card Fraud Detection Using SMOTE for Class Imbalance', IJACSA.",
        "Appavu, N. (2025) 'AI and ML Approaches for Credit Card Fraud Detection: A Comparative Study of Logistic Regression and Decision Tree Techniques', 3rd International Conference on Intelligent Systems (IEEE).",
        "Baisholan, N., Dietz, J.E., Gnatyuk, S., Turdalyuly, M. et al. (2025) 'A Systematic Review of Machine Learning in Credit Card Fraud Detection Under Original Class Imbalance', Computers (MDPI).",
        "Bian, C. (2025) 'Credit Card Fraud Detection: Machine Learning and Deep Learning Advances, Challenges, and Future Directions', ITM Web of Conferences.",
        "Central Bank of Ireland (2025) Payment fraud statistics. Available at: https://www.centralbank.ie/statistics/data-and-analysis/payment-fraud-statistics",
        "Chowdhury, S.A., Hoque, A., Chy, M.S.K. et al. (2025) 'Next Generation Financial Security: Leveraging AI for Fraud Detection, Compliance and Adaptive Risk Management'.",
        "Elumilade, O.O., Ogundeji, I.A. et al. (2025) 'Leveraging Financial Data Analytics for Business Growth, Fraud Prevention, and Risk Mitigation in Markets', Gulf Journal of Advance Business Research.",
        "Gkegkas, M., Kydros, D. and Pazarskis, M. (2025) 'Using Data Analytics in Financial Statement Fraud Detection and Prevention: A Systematic Review', Journal of Risk and Financial Management, 18(11), 598.",
        "Haider, Z.A., Khan, F.M., Zafar, A. and Khan, I.U. (2024) 'Optimizing Machine Learning Classifiers for Credit Card Fraud Detection on Highly Imbalanced Datasets Using PCA and SMOTE Techniques', VAWKUM Transactions on Computer Sciences.",
        "Jamil, M.H., Hossen, A., Talukder, S.I., Arafat, Y. et al. (2025) 'Big Data Analytics and Its Usage on Financial Fraud Detection in the USA', Advances in Machine Learning & Artificial Intelligence.",
        "Jesus, S., Pombal, J., Alves, D., Cruz, A., Saleiro, P., Ribeiro, R., Gama, J. and Bizarro, P. (2022) 'Turning the Tables: Biased, Imbalanced, Dynamic Tabular Datasets for ML Evaluation', NeurIPS Datasets and Benchmarks Track.",
        "kaggle.com (2018) Credit Card Fraud Detection (Machine Learning Group, ULB). Available at: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud",
        "Khan, S.U., Zafar, U., Imran, S. et al. (2026) 'Artificial Intelligence-Driven Fraud Detection in FinTech: Strengthening Cybersecurity Against Digital Financial Scams', Journal of Business Insight and Innovation.",
        "Lopez-Rojas, E.A., Elmir, A. and Axelsson, S. (2016) 'PaySim: A Financial Mobile Money Simulator for Fraud Detection', 28th European Modeling and Simulation Symposium.",
        "Mensa, J.T. and Akinsanya, O.B. (2026) 'Impact of Data Analytics on Fraud Prevention and Public Trust in the United States', working paper.",
        "Saeed, V.A. and Abdulazeez, A.M. (2024) 'Credit Card Fraud Detection Using KNN, Random Forest and Logistic Regression Algorithms: A Comparative Analysis', The Indonesian Journal of Computer Science.",
        "Salunke, Y., Phalke, S., Madavi, M. et al. (2025) 'Fraud Detection: A Hybrid Approach with Logistic Regression, Decision Tree, and Random Forest', Cureus Journal of Computer Science.",
    ]
    s += [Paragraph(f"{i}. {r}", ParagraphStyle("R", parent=B, fontSize=8.5, leading=11, alignment=0)) for i, r in enumerate(refs, 1)]
    doc = SimpleDocTemplate(str(HERE / "Week2_Report.pdf"), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm, title="Week 2 Progress Report - Yashwanth")
    doc.build(s, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    df, hour, corr, p = profile()
    dd = data_dictionary(df)
    dd.to_csv(HERE / "data_dictionary.csv", index=False)
    (HERE / "dataset_profile.json").write_text(json.dumps(p, indent=2))
    figures(df, hour, corr)
    report(p, dd)
    print(json.dumps(p, indent=2))
