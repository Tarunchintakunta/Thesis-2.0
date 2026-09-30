"""Week 2 deliverables for Jayanth Akarapu.

Gantt chart, Week 2 activities: Literature Review (continued) and Dataset Collection.
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
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "transactions_Dataset.csv"
FIG = HERE / "figures"
KAGGLE_ID = "charanmaik/bank-transaction-records-along-suspicious-flags"


# ---------------------------------------------------------------- dataset work
def profile():
    raw = DATA.read_bytes()
    df = pd.read_csv(DATA)
    date = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    y = df["isSuspicious"]
    counts = y.value_counts().to_dict()
    both = ((df.debit > 0) & (df.credit > 0)).sum()
    neither = ((df.debit == 0) & (df.credit == 0)).sum()
    prev = df["balance"].shift(1)
    monthly = df.groupby(date.dt.to_period("M"))["isSuspicious"].agg(["size", "mean"])
    by_desc = (df.groupby("description")["isSuspicious"]
                 .agg(n="size", suspicious="sum", rate="mean")
                 .sort_values("n", ascending=False))
    p = {
        "file": DATA.name,
        "size_mb": round(len(raw) / 1e6, 2),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "unparsed_dates": int(date.isna().sum()),
        "date_min": str(date.min().date()),
        "date_max": str(date.max().date()),
        "distinct_days": int(date.nunique()),
        "distinct_descriptions": int(df["description"].nunique()),
        "negative_values": int((df[["debit", "credit", "balance"]] < 0).sum().sum()),
        "rows_debit_and_credit": int(both),
        "rows_no_amount": int(neither),
        "class_counts": {str(k): int(v) for k, v in counts.items()},
        "suspicious_rate": round(float(y.mean()), 4),
        "imbalance_ratio": round(counts[0] / counts[1], 2),
        "median_nonzero_credit_by_class": {str(k): round(float(v), 2) for k, v in df[df.credit > 0].groupby("isSuspicious")["credit"].median().items()},
        "median_nonzero_debit_by_class": {str(k): round(float(v), 2) for k, v in df[df.debit > 0].groupby("isSuspicious")["debit"].median().items()},
        "negative_balances": int((df["balance"] < 0).sum()),
        "months": int(monthly.shape[0]),
        "median_rows_per_month": int(monthly["size"].median()),
        "busiest_month": str(monthly["size"].idxmax()),
        "busiest_month_rows": int(monthly["size"].max()),
        "busiest_month_rate": round(float(monthly.loc[monthly["size"].idxmax(), "mean"]), 4),
        "median_monthly_rate": round(float(monthly["mean"].median()), 4),
        "balance_unique": bool(df["balance"].is_unique),
        "balance_follows_prev_row_pct": round(float(((prev + df.credit - df.debit - df.balance).abs() < 0.01).mean() * 100), 2),
        "descriptions_always_clean": int((by_desc.suspicious == 0).sum()),
        "descriptions_with_suspicious": int((by_desc.suspicious > 0).sum()),
    }
    # sanity checks: the report must never quote numbers that do not add up
    assert sum(p["class_counts"].values()) == p["rows"]
    assert p["descriptions_always_clean"] + p["descriptions_with_suspicious"] == p["distinct_descriptions"]
    assert p["unparsed_dates"] == 0, "date column is not dd-mm-yyyy throughout"
    return df, date, by_desc, p


def data_dictionary(df):
    meaning = {
        "date": "Transaction date (dd-mm-yyyy string, parsed to datetime in preprocessing)",
        "description": "Channel / merchant code, e.g. NETTXN:EBAY (categorical text)",
        "debit": "Amount leaving the account (0 when the row is a credit)",
        "credit": "Amount entering the account (0 when the row is a debit)",
        "balance": "Account balance after the transaction",
        "isSuspicious": "Target label: 1 = flagged suspicious, 0 = normal",
    }
    rows = []
    for c in df.columns:
        s = df[c]
        num = pd.api.types.is_numeric_dtype(s)
        rows.append({
            "column": c, "dtype": str(s.dtype), "role": "target" if c == "isSuspicious" else "feature",
            "missing": int(s.isna().sum()), "unique": int(s.nunique()),
            "min": round(float(s.min()), 2) if num else "", "max": round(float(s.max()), 2) if num else "",
            "example": str(s.iloc[0]), "meaning": meaning[c],
        })
    return pd.DataFrame(rows)


def figures(df, date, by_desc):
    FIG.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

    c = df["isSuspicious"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(["Normal (0)", "Suspicious (1)"], c.values, color=["#4C72B0", "#C44E52"])
    for i, v in enumerate(c.values):
        ax.text(i, v, f"{v:,}\n({v / c.sum():.1%})", ha="center", va="bottom")
    ax.set_ylabel("Transactions"); ax.set_ylim(0, c.max() * 1.2); ax.set_title("Class distribution")
    fig.tight_layout(); fig.savefig(FIG / "w2_class_balance.png", dpi=160); plt.close(fig)

    top = by_desc.head(15).sort_values("rate")
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.barh(top.index, top["rate"] * 100, color="#C44E52")
    ax.set_xlabel("% of transactions flagged suspicious"); ax.set_title("Suspicious rate by description (top 15 by volume)", loc="right")
    fig.tight_layout(); fig.savefig(FIG / "w2_rate_by_description.png", dpi=160); plt.close(fig)

    m = df.assign(month=date.dt.to_period("M")).groupby("month")["isSuspicious"].agg(["size", "mean"])
    fig, ax = plt.subplots(figsize=(6.5, 3))
    ax.plot(m.index.to_timestamp(), m["size"], color="#4C72B0"); ax.set_ylabel("Transactions / month")
    ax2 = ax.twinx(); ax2.plot(m.index.to_timestamp(), m["mean"] * 100, color="#C44E52", ls="--")
    ax2.set_ylabel("% suspicious", color="#C44E52"); ax.set_title("Monthly volume and suspicious rate")
    fig.tight_layout(); fig.savefig(FIG / "w2_monthly.png", dpi=160); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.8))
    for ax, col in zip(axes, ["credit", "debit"]):
        for lab, colr in [(0, "#4C72B0"), (1, "#C44E52")]:
            v = df.loc[(df.isSuspicious == lab) & (df[col] > 0), col]
            ax.hist(v.clip(lower=1).apply(lambda x: __import__("math").log10(x)), bins=40, alpha=.6, color=colr,
                    density=True, label=["Normal", "Suspicious"][lab])
        ax.set_xlabel(f"log10({col} amount)"); ax.set_title(col.capitalize() + " (non-zero rows)")
    axes[0].legend(frameon=False)
    fig.tight_layout(); fig.savefig(FIG / "w2_amounts.png", dpi=160); plt.close(fig)


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
    cc = p["class_counts"]
    s = [Paragraph("Week 2 Report: Literature Review and Dataset Collection", H1),
         P("Project: Analysing the Role of Big Data Analytics for Cyber Threat Detection and Prevention in Banking "
           "Organisations of Ireland<br/>Student: Jayanth Akarapu<br/>Supervisor: Dr. Prasanth Nayak<br/>"
           "Module: Open Data Practice, Research Practicum"),
         Paragraph("1. What this week covers", H2),
         P("In my Gantt chart the literature review runs from August to the end of September, and dataset collection "
           "happens in August. So this week I did two things. First, I went back over the 15 papers from Week 1 and "
           "compared them with each other, instead of looking at them one at a time. Second, I chose the dataset, "
           "downloaded it and checked it properly before any preprocessing starts in September."),

         Paragraph("2. Literature review progress", H2),
         P("When I compared the papers, the first thing I noticed is that tree ensembles keep coming out on top. "
           "Random Forest was the best model in Sanda et al. (2026), with 97.2% accuracy, and Dhammayogi and "
           "Pramartha (2026) found Random Forest and XGBoost almost level (ROC-AUC 0.992 and 0.995), with SVM "
           "further behind at 0.935. Kumar et al. (2025) also report Random Forest ahead of SVM. This supports my "
           "plan to compare Decision Tree, Random Forest and SVM, with Random Forest as the model to beat."),
         P("The second thing is that the results are hard to compare. The papers use different datasets, "
           "different splits and different ways of handling imbalance, and two of them, Naeem et al. (2026) and "
           "Ullah et al. (2026), use simulated data. None of the papers compare their models with the simple rules "
           "that banks already use, so it is not clear how much machine learning really adds. Because of this I will "
           "use one fixed train and test split for every model, report precision, recall, F1 and ROC-AUC, and add a "
           "simple rule-based baseline."),
         P("Third, big data tools are described more than they are measured. Sathupadi et al. (2025) show Spark and "
           "Kafka working with a BiLSTM at up to 1000 Mbps, but most other papers only mention these tools. I cannot "
           "build a full Spark cluster in this project, but I can measure how training and prediction time grow as "
           "the data gets bigger."),
         P("Fourth, robustness is a known concern but rarely tested. Padmanaban et al. (2026) show that making a "
           "model harder to fool brings accuracy down to 88.2%, and Kovacevic et al. (2025) warn about data "
           "poisoning and evasion attacks. A simple check I can do is to train on earlier months and test on later "
           "ones, and to test on merchants the model has not seen."),
         P("Finally, explainability and regulation matter for banks. Dhammayogi and Pramartha (2026) and Baisholan "
           "et al. (2025) use SHAP to explain predictions, and Laddi et al. (2025) keep data private with federated "
           "learning. For an Irish bank, being able to explain why a transaction was flagged is a GDPR requirement, "
           "so I will include feature importance in my results."),
         P("Table 1 summarises what each paper used and found. Papers marked with * are my baseline papers."),
         table([["No.", "Paper", "Method", "Data", "Main result"],
                ["1*", "Sathupadi et al. (2025)", "BiLSTM with Spark and Kafka", "Internet banking transactions", "98.5% fraud detection accuracy"],
                ["2", "Kumar et al. (2025)", "DL, RF, SVM, K-Means", "500,000 security incidents", "DL 96.8%, RF 94.1%, SVM 92.3%"],
                ["3", "Kokogho et al. (2025)", "Review", "Fintech", "No experiments"],
                ["4*", "Pospichal et al. (2026)", "RF with feature selection, SMOTE", "UNSW-NB15", "F1 0.93 to 0.98"],
                ["5", "Baisholan et al. (2025)", "RF and XGBoost ensemble, SHAP", "European card data", "Recall 95%, AUC-PR 97%"],
                ["6", "Padmanaban et al. (2026)", "RL with adversarial training", "Simulated attacks", "88.2% accuracy, 5.1% false positives"],
                ["7*", "Hozouri et al. (2025)", "Survey of IDS", "CIC-IDS2017, KDDCup99, UNSW-NB15", "No experiments"],
                ["8", "Laddi et al. (2025)", "Federated anomaly detection", "Kaggle network intrusion", "Privacy-preserving IDS"],
                ["9", "Zhang (2025)", "Ensemble of 21 DL models", "BoT-IoT", "99.985% accuracy"],
                ["10", "Naeem et al. (2026)", "LR, SVM, RF, LightGBM, XGBoost", "Simulated, 400 rows", "XGBoost 98.2% (template only)"],
                ["11", "Dhammayogi and Pramartha (2026)", "RF, XGBoost, SVM with SHAP", "Digital banking fraud", "ROC-AUC 0.995, 0.992, 0.935"],
                ["12*", "Sanda et al. (2026)", "LR, RF, SVM, GB, NN with SMOTE", "Kaggle banking fraud", "RF 97.2%, AUC 98.4%"],
                ["13", "Eshra et al. (2025)", "Threat intelligence study", "Financial institutions", "33.7% lower breach likelihood"],
                ["14", "Ullah et al. (2026)", "XGBoost and LSTM hybrid", "Simulated, 125,000 rows", "96.4% accuracy, ROC-AUC 0.982"],
                ["15", "Kovacevic et al. (2025)", "Discussion paper", "Banking", "Adversarial AI risks"]],
               [1, 3.6, 4, 3.8, 4.2]),
         Paragraph("Table 1. Summary of the reviewed papers.", CAP),
         P("From this comparison I have narrowed my research gaps to five points. There is no comparison with simple "
           "rules. Results use different setups and cannot be compared. Big data claims are rarely measured. Changes "
           "over time and attacks are rarely tested. And there is very little Irish or EU regulatory context. Each "
           "of these is covered by a specific test in my plan."),
         P("I also noticed that most of these studies use network traffic datasets such as UNSW-NB15 and BoT-IoT, "
           "or simulated data. Network traffic is not the same as bank transactions, and simulated data cannot show "
           "real performance. This is why I wanted an open dataset of labelled bank transactions."),

         Paragraph("3. Dataset collection", H2),
         P("Before choosing, I wrote down what I needed: bank transaction records, a label for suspicious or "
           "fraudulent activity, an open licence, a size I can train on my laptop, and no personal data. I looked at "
           "four options. The Bank Account Fraud dataset (Jesus et al., 2022) is about account applications, not "
           "transactions. PaySim (Lopez-Rojas et al., 2016) is mobile money. CICIDS2017 is network traffic. The Kaggle "
           "dataset \"Bank Transaction Records along Suspicious Flags\", which I named in my proposal, meets all five "
           "points, so I chose it."),
         P(f"I downloaded it with the Kaggle API. Kaggle lists the licence as MIT and describes the data as a "
           f"simulation of bank transactions. The file is {p['file']} ({p['size_mb']} MB). I saved its SHA-256 "
           f"checksum so I can show later that I used the same file throughout: "
           f"<font face='Courier' size='8'>{p['sha256']}</font>"),
         P(f"The dataset has {p['rows']:,} rows and {p['columns']} columns. Table 2 describes each column."),
         table([["Column", "Type", "Unique values", "Range", "Meaning"]] +
               [[r["column"], r["dtype"], f"{r['unique']:,}",
                 f"{r['min']} to {r['max']}" if r["min"] != "" else "text", r["meaning"]] for _, r in dd.iterrows()],
               [2.3, 1.5, 2.1, 3.6, 7.1]),
         Paragraph("Table 2. Data dictionary.", CAP),
         P(f"I then checked the data quality. There are no missing values and no duplicate rows. All dates follow "
           f"the day-month-year format and run from {p['date_min']} to {p['date_max']}. Debit and credit are never "
           f"negative, and every row has either a debit or a credit, never both. {p['negative_balances']} rows have "
           f"a negative balance, which I read as overdrafts. The balance is different on every row and only matches "
           f"the previous row's balance in {p['balance_follows_prev_row_pct']}% of cases, so the rows are not one "
           f"running account. Because of that I will test the models with and without the balance column."),
         P(f"{cc['1']:,} of the {p['rows']:,} transactions ({p['suspicious_rate']:.1%}) are marked as suspicious. That "
           f"is much more balanced than real bank fraud, where the rate is well under 1%. It means class weights "
           f"should be enough to handle the imbalance, but it also means I should not treat the number of alerts as "
           f"realistic."),
         *fig("w2_class_balance.png", "Figure 1. Normal and suspicious transactions.", 8),
         P(f"The most important thing I found is how much the description column matters. {p['descriptions_always_clean']} "
           f"of the {p['distinct_descriptions']} descriptions are never flagged. These are payment channels such as "
           f"PCA, IMPS and cash deposits. Online shops, ticket booking sites and crypto exchanges are flagged in about "
           f"70 to 75% of their rows (Figure 2). So a model could learn the labelling rule instead of real threat "
           f"behaviour. To check this I will add a test where some descriptions are kept out of training."),
         *fig("w2_rate_by_description.png", "Figure 2. Share of suspicious transactions for the 15 most common descriptions."),
         P(f"Suspicious transactions are also bigger. For debits, the median suspicious amount is "
           f"{p['median_nonzero_debit_by_class']['1']:,.0f} compared with {p['median_nonzero_debit_by_class']['0']:,.0f} "
           f"for normal ones. Amounts vary a lot, so I will use a log transform (Figure 4). The data is also not "
           f"spread evenly over time. A normal month has about {p['median_rows_per_month']:,} rows, but "
           f"{p['busiest_month']} has {p['busiest_month_rows']:,} rows and a much higher suspicious rate (Figure 3). "
           f"This is another reason to test on later months as well as on a random split."),
         *fig("w2_monthly.png", "Figure 3. Transactions per month (solid line) and suspicious rate (dashed line)."),
         *fig("w2_amounts.png", "Figure 4. Credit and debit amounts on a log scale."),

         Paragraph("4. Ethics", H2),
         P("The data is simulated and has no names, real account numbers or other personal details, so GDPR does not "
           "apply to the raw file. The account-style numbers inside some descriptions are placeholders. The MIT "
           "licence allows academic use. I keep the file on my own machine and do not upload it anywhere. Since the "
           "data is simulated and not Irish, I will present my results as a test of the methods, not as a measurement "
           "of Irish banks."),

         Paragraph("5. Next week", H2),
         P("In Week 3 I will keep reading, mainly papers on fraud patterns changing over time and on rules compared "
           "with machine learning. I will also start preprocessing: converting the dates, splitting the description "
           "into channel and merchant, log-transforming the amounts, and creating one fixed 80/20 train and test "
           "split that I will use for all experiments."),

         Paragraph("References", H2)]
    refs = sorted([
    "Baisholan, N., Dietz, J.E., Gnatyuk, S., Turdalyuly, M., Matson, E.T. and Baisholanova, K. (2025) FraudX AI: an interpretable machine learning framework for credit card fraud detection on imbalanced datasets. Computers, 14(4), 120. https://doi.org/10.3390/computers14040120",
    "Dhammayogi, M.B.D. and Pramartha, C.R.A. (2026) Early detection of digital transaction fraud in banking systems using the Random Forest algorithm. Journal of Information Technology and Computer Science, 11(2), pp. 267-279. https://doi.org/10.25126/jitecs.2026112912",
    "Eshra, S.A., Zohora, F.T., Akter, S., Rasul, I. and Hossain, A. (2025) The role of threat intelligence in preventing financially motivated cyberattacks. Journal of Engineering and Computational Intelligence Review, 3(2), pp. 20-37. https://doi.org/10.63544/f7hdvf20",
    "Hozouri, A., Mirzaei, A. and Effatparvar, M. (2025) A comprehensive survey on intrusion detection systems with advances in machine learning, deep learning and emerging cybersecurity challenges. Discover Artificial Intelligence, 5(1), 314. https://doi.org/10.1007/s44163-025-00578-1",
    "Kokogho, E., Okon, R., Omowole, B.M., Ewim, C.P. and Onwuzulike, O.C. (2025) Enhancing cybersecurity risk management in fintech through advanced analytics and machine learning. International Journal of Frontiers in Science and Technology Research, 8(1), pp. 1-23. https://doi.org/10.53294/ijfstr.2025.8.1.0023",
    "Kovacevic, A., Radenkovic, S.D. and Nikolic, D. (2025) Artificial intelligence and cybersecurity in banking sector: opportunities and risks. In: Proceedings of the 8th International Scientific Conference Contemporary Issues in Economics, Business and Management (EBM 2024). Kragujevac: Faculty of Economics, pp. 425-433. https://doi.org/10.46793/ebm24.425k",
    "Kumar, B.H., Nuka, S.T., Malempati, M., Sriram, H.K., Mashetty, S. and Kannan, S. (2025) Big data in cybersecurity: enhancing threat detection with AI and ML. Metallurgical and Materials Engineering, 31(3), pp. 12-20. https://doi.org/10.63278/1315",
    "Laddi, M., Allagi, S., Rachh, R., Sambrekar, K. and Athanikar, S. (2025) An advanced cyber security model using federated machine learning approach for intrusion detection in networks. Journal of Computational and Cognitive Engineering, 4(2), pp. 223-235. https://doi.org/10.47852/bonviewjcce42023751",
    "Naeem, W., Butt, M.A. and Javeid, U. (2026) Machine learning-based fraud detection systems and their effectiveness in reducing cybersecurity risks in digital banking. Social Science Review Archives, 4(2), pp. 2553-2573. https://doi.org/10.70670/sra.v4i2.2344",
    "Padmanaban, H., Sharma, Y.K., Sharma, P. and Verma, C. (2026) Adversarial machine learning framework for robust banking security: the automated cyber threat detection and prevention (ACTP) tool. Journal of The Institution of Engineers (India): Series B, 107(3), pp. 1605-1623. https://doi.org/10.1007/s40031-026-01337-1",
    "Pospichal, J., Augustin, A., Huraj, L., Strelec, P. and Gabriska, D. (2026) Random forest-based network intrusion detection with feature selection and class balancing on UNSW-NB15 traffic. Information, 17(9), 836. https://doi.org/10.3390/info17090836",
    "Sanda, A.M., Mukhtar, U.S. and Abdulazeez, A.M. (2026) Enhanced banking fraud detection: a comparative analysis of supervised machine learning algorithms. FETICON Proceedings, 4(2), pp. 1-7. https://doi.org/10.63748/h1qaz029",
    "Sathupadi, K., Achar, S., Bhaskaran, S.V., Faruqui, N. and Uddin, J. (2025) BankNet: real-time big data analytics for secure internet banking. Big Data and Cognitive Computing, 9(2), 24. https://doi.org/10.3390/bdcc9020024",
    "Ullah, N., Ishaq, M., Rahman, F., Aslam, M.U. and Adil, F. (2026) An advanced AI-driven risk assessment framework for U.S. banking institutions: integrating predictive financial analytics, regulatory-aware governance and cybersecurity risk intelligence. Journal of Management Science Research Review, 5(2), pp. 3176-3204.",
    "Zhang, H. (2025) Development of an intelligent intrusion detection system for IoT networks using deep learning. Discover Internet of Things, 5, 74. https://doi.org/10.1007/s43926-025-00177-7",
    "Jesus, S., Pombal, J., Alves, D., Cruz, A., Saleiro, P., Ribeiro, R., Gama, J. and Bizarro, P. (2022) Turning the tables: biased, imbalanced, dynamic tabular datasets for ML evaluation. NeurIPS Datasets and Benchmarks Track.",
    "Kaggle (2025) Bank Transaction Records along Suspicious Flags. Available at: https://www.kaggle.com/datasets/charanmaik/bank-transaction-records-along-suspicious-flags",
    "Lopez-Rojas, E.A., Elmir, A. and Axelsson, S. (2016) PaySim: a financial mobile money simulator for fraud detection. 28th European Modeling and Simulation Symposium.",
    ])
    s += [Paragraph(r, REF) for r in refs]
    doc = SimpleDocTemplate(str(HERE / "Week2_Report.pdf"), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm, title="Week 2 Report, Jayanth Akarapu")
    doc.build(s, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    df, date, by_desc, p = profile()
    dd = data_dictionary(df)
    dd.to_csv(HERE / "data_dictionary.csv", index=False)
    (HERE / "dataset_profile.json").write_text(json.dumps(p, indent=2))
    by_desc.to_csv(HERE / "suspicious_rate_by_description.csv")
    figures(df, date, by_desc)
    report(p, dd)
    print(json.dumps(p, indent=2))
