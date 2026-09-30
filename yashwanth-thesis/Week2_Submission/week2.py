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
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="Times-Bold", fontSize=14, spaceBefore=10, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Times-Bold", fontSize=12, spaceBefore=8, spaceAfter=4)
B = ParagraphStyle("B", parent=ss["BodyText"], fontName="Times-Roman", fontSize=11.5, leading=16, alignment=TA_JUSTIFY, spaceAfter=7)
C = ParagraphStyle("C", parent=B, fontSize=9.5, leading=12, alignment=0, spaceAfter=0)
CAP = ParagraphStyle("CAP", parent=B, fontSize=10, alignment=1)
REF = ParagraphStyle("REF", parent=B, fontSize=10.5, leading=14, alignment=0, leftIndent=14, firstLineIndent=-14)


def table(rows, widths):
    t = Table([[Paragraph(f"<b>{c}</b>" if i == 0 else str(c), C) for c in r] for i, r in enumerate(rows)],
              colWidths=[w * cm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .5, colors.black), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t


def fig(name, caption, w=14):
    img = Image(str(FIG / name)); img.drawHeight = img.drawHeight * (w * cm) / img.drawWidth; img.drawWidth = w * cm
    return [Spacer(1, 4), img, Paragraph(caption, CAP), Spacer(1, 6)]


def P(text):
    return Paragraph(text, B)


def footer(canvas, doc):
    canvas.saveState(); canvas.setFont("Times-Roman", 9)
    canvas.drawCentredString(A4[0] / 2, 1.2 * cm, str(doc.page)); canvas.restoreState()


def report(p, dd):
    cc, cd = p["class_counts"], p["class_counts_dedup"]
    s = [Paragraph("Week 2 Report: Literature Review and Dataset Collection", H1),
         P("Project: Determining the Role of Big Data Applications in Fraud Detection and Financial Security in "
           "Financial Institutions of Ireland<br/>Student: Yashwanth<br/>Supervisor: Dr. Prasanth Nayak<br/>"
           "Module: Open Data Practice, Research Practicum"),
         Paragraph("1. What this week covers", H2),
         P("My Gantt chart has the literature review running from Week 1 to Week 3 and dataset collection in Weeks "
           "2 and 3. So this week I did two things. I compared the fifteen papers from Week 1 with each other to see "
           "where they agree and what they miss, and I collected and checked the dataset. Data preprocessing starts "
           "next week and full exploratory analysis is planned for Week 4, so the data checks here are only the "
           "ones I need to plan that work."),

         Paragraph("2. Literature review progress", H2),
         P("Looking across the papers, Random Forest and other tree ensembles are the models that keep doing best. "
           "Albalawi and Dardouri (2025) and Andrade-Arenas and Yactayo-Arias (2025) both found Random Forest had the "
           "best F1 on the Kaggle European card data (0.8256 and 0.872). Preciado Martinez et al. (2025) found the "
           "same on 565,000 real bank transfers, and the review by Baisholan et al. (2025) says tree ensembles are the "
           "most common choice across the field. Jamil et al. (2025) and Salunke et al. (2025) compare the same three "
           "models I plan to use, Logistic Regression, Decision Tree and Random Forest, and Random Forest or a "
           "combination of the three comes out ahead."),
         P("The second point is that accuracy does not tell the full story. Andrade-Arenas and Yactayo-Arias (2025) "
           "report accuracy of 0.999 for several models, yet Logistic Regression only managed an F1 of 0.110. Haider "
           "et al. (2024) and Alrasheedi (2025) report mainly accuracy, which makes it hard to know how many frauds "
           "were caught. Baisholan et al. (2025) point out that AUC-PR is used much less than it should be. I will "
           "therefore report precision, recall, F1 and AUC-PR, not just accuracy."),
         P("Third, SMOTE is used in many papers, but it is not always a clear win. Ma et al. (2026) found that "
           "resampling is not always helpful and that it should be judged on a test set that keeps the real class "
           "balance. Most other papers do not say clearly whether they applied SMOTE before or after splitting the "
           "data. If it is applied before the split, synthetic copies of test frauds end up in training and the "
           "results look better than they are. I will only apply it to the training data and compare it with class "
           "weights."),
         P("Fourth, almost every experimental paper uses the same Kaggle dataset. This makes results easy to "
           "compare, but none of them mention the duplicate rows I found in the file (Section 3). The features are "
           "also PCA components, so the models are hard to explain to a bank or a regulator."),
         P("Finally, the regulatory side is thin. Horobets et al. (2025) show that EU rules on anti-money laundering "
           "and the AI Act ask for explainability and fairness that current AI systems do not fully deliver. Gkegkas "
           "et al. (2025) and Bian (2025) also call for more explainable models. Jamil et al. (2025) is set in the "
           "USA and Khan et al. (2026) in Pakistan. None of the papers look at Irish institutions, which is the gap my "
           "project focuses on."),
         P("Table 1 summarises the experimental papers I will compare my results against."),
         table([["Paper", "Data", "Models", "Main result"],
                ["Albalawi and Dardouri (2025)", "Kaggle European cards, PaySim", "LR, DT, RF, XGBoost, deep learning", "RF best: F1 0.8256, ROC-AUC 0.9759"],
                ["Andrade-Arenas and Yactayo-Arias (2025)", "Kaggle European cards", "Seven models with SMOTE", "RF F1 0.872, AUC 0.978; LR F1 0.110"],
                ["Ma et al. (2026)", "Kaggle European cards", "RF feature selection, tuned XGBoost", "PR-AUC 0.798, fraud F1 0.809"],
                ["Preciado Martinez et al. (2025)", "565,000 bank transfers", "RF, neural network, Naive Bayes", "RF 95.79% fraud detection"],
                ["Jamil et al. (2025)", "US transaction data", "LR, DT, RF", "RF fewest errors"],
                ["Salunke et al. (2025)", "Public card dataset", "LR, DT, RF, hybrid", "Hybrid ensemble best"],
                ["Haider et al. (2024)", "Imbalanced card dataset", "Six models with PCA and SMOTE", "About 96 to 97% accuracy"],
                ["Alrasheedi (2025)", "Three datasets", "Seven models", "RF 0.97 accuracy on imbalanced data"]],
               [4.3, 3.6, 4.4, 4.7]),
         Paragraph("Table 1. Experimental papers used for comparison.", CAP),
         P("From this I have narrowed my research gaps to five points: SMOTE timing is often not reported, accuracy "
           "is overused, duplicates in the benchmark are ignored, the PCA features are hard to explain, and there is "
           "no Irish context. Each one links to a step in my method."),

         Paragraph("3. Dataset collection", H2),
         P("Before choosing a dataset I wrote down what I needed: labelled card or payment transactions, an open "
           "licence, European data if possible, no personal information, and a dataset used by the papers I compare "
           "with. I looked at four options. IEEE-CIS has many raw identity fields and a competition-only licence. "
           "PaySim (Lopez-Rojas et al., 2016) is simulated mobile money. The Bank Account Fraud dataset (Jesus et al., "
           "2022) is about account applications. The Kaggle Credit Card Fraud Detection dataset from ULB meets all "
           "five points and is the one named in my proposal, so I chose it."),
         P("For the Irish context I also collected the Central Bank of Ireland payment fraud statistics for 2022 to "
           "2024. These are summary figures, not training data. They show 160 million euro of fraudulent payments "
           "and about 815,000 fraudulent transactions in 2024 (Central Bank of Ireland, 2025)."),
         P(f"I downloaded the dataset with the Kaggle API. Kaggle lists the licence as DbCL-1.0. The file is "
           f"{p['file']} ({p['size_mb']} MB). I saved its SHA-256 checksum so I can show later that I used the same "
           f"file: <font face='Courier' size='8'>{p['sha256']}</font>"),
         P("The data owners replaced the original features with 28 PCA components, V1 to V28, to protect "
           "cardholders. Only Time and Amount keep their original meaning. Table 2 describes the columns."),
         table([["Column", "Type", "Range", "Meaning"]] +
               [[r["column"], r["dtype"], f"{r['min']} to {r['max']}", r["meaning"]]
                for _, r in dd[dd.column.isin(["Time", "Amount", "Class"])].iterrows()] +
               [["V1 to V28", "float64", f"{dd[dd.column.str.match(r'V[0-9]')]['min'].min()} to "
                 f"{dd[dd.column.str.match(r'V[0-9]')]['max'].max()}", "PCA components, already centred on zero"]],
               [2.5, 2, 4, 8.5]),
         Paragraph("Table 2. Data dictionary (the full 31 columns are in data_dictionary.csv).", CAP),
         P(f"The file has {p['rows']:,} rows and {p['columns']} columns with no missing values. It covers "
           f"{p['time_span_hours']:.0f} hours, which is two days of transactions. I found {p['duplicate_rows']:,} "
           f"rows that are exact copies of other rows, and {p['duplicate_fraud_rows']} of them are fraud. If these "
           f"stay in, the same transaction can end up in both the training and the test set, so I will remove them "
           f"before splitting. That leaves {cd['0']:,} legitimate and {cd['1']:,} fraud transactions. There are also "
           f"{p['zero_amount_rows']:,} transactions with an amount of zero, which I will keep because small or zero "
           f"charges are often used to test a stolen card."),
         P(f"Only {cc['1']:,} of the {p['rows']:,} transactions ({p['fraud_rate_pct']}%) are fraud, about one in "
           f"{p['imbalance_ratio']:.0f}. A model that always says legitimate would score "
           f"{100 - p['fraud_rate_pct']:.2f}% accuracy, which is exactly why accuracy is not a good measure here. "
           f"The train and test split has to be stratified so both sets keep some fraud cases."),
         *fig("w2_class_balance.png", "Figure 1. Legitimate and fraud transactions (log scale).", 8),
         P(f"A first look at the data shows a few useful patterns. The median fraud amount is "
           f"{p['median_amount_by_class']['1']}, lower than {p['median_amount_by_class']['0']} for legitimate "
           f"transactions, but the average fraud is higher because of some large ones (Figure 2). Fraud is also "
           f"more common at night: {p['night_fraud_rate_pct']}% of transactions between midnight and 6am are fraud "
           f"compared with {p['day_fraud_rate_pct']}% for the rest of the day (Figure 3), so an hour of day feature "
           f"may help. The components most linked to fraud are V17, V14, V12 and V10 (Figure 4)."),
         *fig("w2_amounts.png", "Figure 2. Transaction amounts by class on a log scale."),
         *fig("w2_hourly.png", "Figure 3. Transactions per hour (bars) and fraud rate (line)."),
         *fig("w2_top_corr.png", "Figure 4. Features most correlated with fraud."),

         Paragraph("4. Ethics", H2),
         P("The dataset has no names, card numbers or other personal details. Only PCA components, Time and Amount "
           "are released, so no one can be identified from it. I use it for academic research under its licence, "
           "keep it on my own machine and do not share it. The Central Bank figures are public. Because the data is "
           "from European cardholders in 2013 and not from Irish banks, I will present my results as a test of the "
           "methods and base the Irish recommendations on the literature and Central Bank data."),

         Paragraph("5. Next week", H2),
         P("In Week 3 I will finish the literature review with a few more papers on SMOTE and evaluation, and on EU "
           "rules for automated fraud decisions. I will also start preprocessing: removing the duplicates, scaling "
           "Time and Amount, and creating one fixed stratified train and test split that I will use for every model."),

         Paragraph("References", H2)]
    refs = [
        "Albalawi, T. and Dardouri, S. (2025) Enhancing credit card fraud detection using traditional and deep learning models with class imbalance mitigation. Frontiers in Artificial Intelligence, 8, 1643292. https://doi.org/10.3389/frai.2025.1643292",
        "Alrasheedi, M.A. (2025) Enhancing fraud detection in credit card transactions: a comparative study of machine learning models. Computational Economics, 68(1), pp. 779-805. https://doi.org/10.1007/s10614-025-11071-3",
        "Andrade-Arenas, L. and Yactayo-Arias, C. (2025) Comparative analysis of machine learning models for credit card fraud detection using SMOTE for class imbalance. International Journal of Safety and Security Engineering, 15(5), pp. 893-901. https://doi.org/10.18280/ijsse.150504",
        "Baisholan, N., Dietz, J.E., Gnatyuk, S., Turdalyuly, M., Matson, E.T. and Baisholanova, K. (2025) A systematic review of machine learning in credit card fraud detection under original class imbalance. Computers, 14(10), 437. https://doi.org/10.3390/computers14100437",
        "Bian, C. (2025) Credit card fraud detection: machine learning and deep learning advances, challenges, and future directions. ITM Web of Conferences, 78, 02023. https://doi.org/10.1051/itmconf/20257802023",
        "Central Bank of Ireland (2025) Payment fraud statistics. Available at: https://www.centralbank.ie/statistics/data-and-analysis/payment-fraud-statistics",
        "Gkegkas, M., Kydros, D. and Pazarskis, M. (2025) Using data analytics in financial statement fraud detection and prevention: a systematic review of methods, challenges, and future directions. Journal of Risk and Financial Management, 18(11), 598. https://doi.org/10.3390/jrfm18110598",
        "Haider, Z.A., Khan, F.M., Zafar, A., Nabila and Khan, I.U. (2024) Optimizing machine learning classifiers for credit card fraud detection on highly imbalanced datasets using PCA and SMOTE techniques. VAWKUM Transactions on Computer Sciences, 12(2), pp. 28-49. https://doi.org/10.21015/vtcs.v12i2.1921",
        "Horobets, N., Reznik, O., Maliyk, V., Vyhivskyi, I. and Bobrishova, L. (2025) Artificial intelligence technologies in banking: challenges and opportunities for anti-money laundering in the context of EU regulatory initiatives. Journal of Money Laundering Control, 28(4-5), pp. 593-608. https://doi.org/10.1108/JMLC-03-2025-0041",
        "Jamil, M.H., Talukder, S.I., Hosen, A., Arafat, Y. and Sozib, H.M. (2025) Big data analytics and its usage on financial fraud detection in the USA. Advances in Machine Learning, IoT and Data Security, 1(2). https://doi.org/10.63471/amlid25001",
        "Jesus, S., Pombal, J., Alves, D., Cruz, A., Saleiro, P., Ribeiro, R., Gama, J. and Bizarro, P. (2022) Turning the tables: biased, imbalanced, dynamic tabular datasets for ML evaluation. NeurIPS Datasets and Benchmarks Track.",
        "Kaggle (2018) Credit Card Fraud Detection, Machine Learning Group, ULB. Available at: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud",
        "Khan, S.U., Zafar, U., Imran, S. and Ali, M. (2026) Artificial intelligence-driven fraud detection in FinTech: strengthening cybersecurity against digital financial scams. Journal of Business Insight and Innovation, 5(6), pp. 72-82. https://doi.org/10.63544/jbii.v5i6.116",
        "Lopez-Rojas, E.A., Elmir, A. and Axelsson, S. (2016) PaySim: a financial mobile money simulator for fraud detection. 28th European Modeling and Simulation Symposium.",
        "Ma, C., Zhang, L., Xing, Z. and Su, J. (2026) Credit card fraud detection under extreme class imbalance using leakage-safe feature selection and GA-based hyperparameter optimization. Applied Sciences, 16(13), 6734. https://doi.org/10.3390/app16136734",
        "Preciado Martinez, P.M., Reier Forradellas, R.F., Garay Gallastegui, L.M. and Nanez Alonso, S.L. (2025) Comparative analysis of machine learning models for the detection of fraudulent banking transactions. Cogent Business and Management, 12(1), 2474209. https://doi.org/10.1080/23311975.2025.2474209",
        "Salunke, Y., Phalke, S., Madavi, M., Kumre, P. and Bobhate, G. (2025) Fraud detection: a hybrid approach with logistic regression, decision tree, and random forest. Cureus Journal of Computer Science, 2(1). https://doi.org/10.7759/s44389-024-02350-5",
    ]
    s += [Paragraph(r, REF) for r in refs]
    doc = SimpleDocTemplate(str(HERE / "Week2_Report.pdf"), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm, title="Week 2 Report, Yashwanth")
    doc.build(s, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    df, hour, corr, p = profile()
    dd = data_dictionary(df)
    dd.to_csv(HERE / "data_dictionary.csv", index=False)
    (HERE / "dataset_profile.json").write_text(json.dumps(p, indent=2))
    figures(df, hour, corr)
    report(p, dd)
    print(json.dumps(p, indent=2))
