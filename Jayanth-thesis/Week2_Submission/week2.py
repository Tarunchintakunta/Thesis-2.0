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
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=15, textColor=colors.HexColor("#1F3864"), spaceAfter=6)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=12, textColor=colors.HexColor("#2E75B6"), spaceBefore=8)
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=9.5, leading=13.5, alignment=TA_JUSTIFY, spaceAfter=5)
C = ParagraphStyle("C", parent=B, fontSize=8, leading=10, alignment=0, spaceAfter=0)
CAP = ParagraphStyle("CAP", parent=B, fontSize=8.5, textColor=colors.grey, alignment=1)


def table(rows, widths, head=True):
    t = Table([[Paragraph(str(c), C) for c in r] for r in rows], colWidths=[w * cm for w in widths], repeatRows=1)
    st = [("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#BFBFBF")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FC")])]
    if head:
        st.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F2")))
    t.setStyle(TableStyle(st))
    return t


def fig(name, caption, w=15):
    img = Image(str(FIG / name)); img.drawHeight = img.drawHeight * (w * cm) / img.drawWidth; img.drawWidth = w * cm
    return [img, Paragraph(caption, CAP), Spacer(1, 6)]


def P(text):
    return Paragraph(text, B)


def footer(canvas, doc):
    canvas.saveState(); canvas.setFont("Helvetica", 7.5); canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.2 * cm, "Week 2 - Literature Review (continued) and Dataset Collection | Jayanth Akarapu")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}"); canvas.restoreState()


def report(p, dd):
    s = []
    s += [Spacer(1, 3 * cm), Paragraph("Week 2 Progress Report", H1),
          Paragraph("Literature Review (continued) and Dataset Collection", H2), Spacer(1, 10),
          P("<b>Project:</b> Analysing the Role of Big Data Analytics for Cyber Threat Detection and Prevention in "
            "Banking Organisations of Ireland"),
          P("<b>Student:</b> Jayanth Akarapu"), P("<b>Course:</b> Open Data Practice - Research Practicum"),
          P("<b>Supervisor:</b> Dr. Prasanth Nayak"),
          P("<b>Gantt activities this week:</b> Literature Review (continued), Dataset Collection"),
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
          P("The project Gantt chart (CA1 proposal, Section 3.8) runs Literature Review from August to the end of "
            "September and Dataset Collection across August. Data Preprocessing begins in September. Week 2 therefore "
            "has two tasks: move the literature review from paper-by-paper summaries to a critical synthesis, and "
            "obtain, document and audit the dataset that the experiments will use."),
          table([["Gantt activity", "Planned window", "Week 2 target", "Status"],
                 ["Literature Review", "Aug - end Sep", "Thematic synthesis, comparison matrix, refined gaps", "On track"],
                 ["Dataset Collection", "Aug", "Dataset selected, downloaded, verified and profiled", "Complete"],
                 ["Data Preprocessing", "Sep - end Oct", "Not started; issues logged in Section 3.6 feed it", "Next"]],
                [3.5, 3, 6.5, 2])]

    # 2 literature
    s += [Paragraph("2. Literature Review (continued)", H1),
          Paragraph("2.1 Thematic synthesis", H2),
          P("Week 1 summarised 15 papers (2025-2026) individually. This week the papers were read against each other "
            "to find where they agree, where they disagree and what none of them tests. Five findings shape the "
            "study design."),
          P("<b>(a) Tree ensembles are the consistent winner on tabular security data.</b> Random Forest is the best "
            "or joint-best model in Papers 4, 10, 11 and 12, and the IDS survey (Paper 7) reports the same across "
            "NSL-KDD, UNSW-NB15 and CICIDS2017. SVM is competitive but costs more compute (Paper 12). This supports "
            "the proposal's choice of Decision Tree, Random Forest and SVM, with Random Forest as the expected leader "
            "and Decision Tree as the interpretable reference."),
          P("<b>(b) Reported scores are high and hard to compare.</b> Accuracy values of 96-99% (Papers 4, 9, 10, 11) "
            "come from different datasets, splits and imbalance treatments. Only Paper 10 states its resampling method "
            "(SMOTE). None reports a simple rule-based comparator, so it is unclear how much the ML adds over the "
            "rules banks already run. This study will therefore report precision, recall, F1 and ROC-AUC on one "
            "fixed held-out split, and include a rule baseline."),
          P("<b>(c) Big data architecture is described more than it is measured.</b> Papers 1 and 2 argue for "
            "Kafka/Spark/Flink pipelines, and Paper 1 reports sub-second latency, but on simulated data and without "
            "a model-by-model cost comparison. Measuring training and scoring time as data size grows gives a "
            "practical, testable answer to RQ1 on the scale this project can run."),
          P("<b>(d) Robustness and drift are named as open problems.</b> Paper 7 lists concept drift and adversarial "
            "robustness as unresolved; Paper 6 shows adversarial training helps but only on synthetic attack "
            "scenarios. A time-ordered split (train on earlier months, test on later ones) and a test on entities "
            "unseen in training are cheap ways to probe this within scope."),
          P("<b>(e) Governance is the Irish and EU angle.</b> Papers 8, 13, 14 and 15 connect detection to GDPR, "
            "federated learning, DORA/NIS2 and the EU AI Act. For Irish banks, an explainable model is a compliance "
            "need, not an extra. Feature importance (and SHAP where feasible) will be reported to answer RQ3 and RQ4."),
          Paragraph("2.2 Method comparison matrix", H2),
          table([["#", "Study", "Models", "Data", "Class balance", "Metrics / result", "Use here"],
                 ["1*", "Sathupadi et al. 2025", "Kafka + ML classifiers", "Simulated banking", "n/s", "Sub-second latency", "Pipeline design"],
                 ["2", "Kumar et al. 2025", "RF, SVM, NN (review)", "Security datasets", "n/s", "Up to 40% over rules", "Big data framing"],
                 ["3", "Kokogho et al. 2025", "Predictive risk scoring", "Fintech transactions", "n/s", "+35% early detection", "Risk context"],
                 ["4*", "Ali et al. 2025", "RF, SVM, DT, GB", "CICIDS2017", "n/s", "RF Acc 98.4%, F1 0.97", "Evaluation protocol"],
                 ["5", "Mizanur et al. 2025", "IF, AE, K-Means + RF, SVM, NB", "Network traffic", "Analysed", "P 0.96, R 0.94", "Anomaly option"],
                 ["6", "Padmanaban et al. 2026", "RF, SVM + adversarial training", "Synthetic banking attacks", "n/s", "+42% robustness", "Robustness"],
                 ["7*", "Hozouri et al. 2025", "Survey, 150+ IDS papers", "NSL-KDD, UNSW-NB15, CICIDS2017", "Discussed", "RF, CNN-LSTM best", "Theory; model choice"],
                 ["8", "Laddi et al. 2025", "Federated IDS", "Network nodes", "n/s", "95.6% Acc; within 2-3% of central", "GDPR angle"],
                 ["9", "Zhang 2025", "CNN-LSTM", "CIC-IoT2023", "n/s", "99.1% Acc, FPR < 0.4%", "DL contrast"],
                 ["10*", "Naeem et al. 2026", "DT, RF, SVM", "Digital banking", "SMOTE", "RF AUC 0.987", "Benchmark to beat"],
                 ["11", "Dhammayogi & Pramartha 2026", "RF (50-500 trees)", "Banking transactions", "n/s", "Acc 98.7% at 200 trees", "Tuning range"],
                 ["12", "Sanda et al. 2026", "DT, RF, SVM, LR, KNN, NB", "Banking fraud", "n/s", "RF best overall", "Extra baselines"],
                 ["13", "Eshra et al. 2025", "CTI + ML prioritisation", "SOC simulation", "n/a", "MTTD -58%", "Prevention side"],
                 ["14", "Ullah et al. 2026", "Predictive cyber-risk", "Financial + cyber events", "n/a", "Losses -31%", "Risk quantification"],
                 ["15", "Kovacevic et al. 2025", "Review of AI tools", "Banking cases", "n/a", "Fraud losses -52%", "Governance risks"]],
                [0.8, 2.8, 2.9, 2.6, 1.5, 2.6, 2.2]),
          Paragraph("* baseline paper. n/s = not stated in the paper; n/a = not a classification study.", CAP),
          Paragraph("2.3 Refined research gaps and link to research questions", H2),
          table([["Gap from the synthesis", "How this study responds", "RQ"],
                 ["G1. High scores are not compared with the simple rules banks already use",
                  "Add a transparent rule baseline next to DT, RF and SVM on the same split", "RQ2"],
                 ["G2. Results mix splits and imbalance methods, so they cannot be compared",
                  "One fixed stratified 80/20 split and seed; imbalance treatment stated and compared", "RQ2"],
                 ["G3. Big data claims lack cost measurements",
                  "Record training and scoring time as sample size grows", "RQ1, RQ3"],
                 ["G4. Drift and generalisation are named but rarely tested",
                  "Time-ordered split and a held-out-entity test", "RQ2, RQ3"],
                 ["G5. Little Irish/EU regulatory grounding of the models",
                  "Explainability outputs and GDPR / AI Act discussion in recommendations", "RQ3, RQ4"]],
                [5.5, 7.5, 2]),
          Paragraph("2.4 Datasets used in the literature", H2),
          P("Most reviewed studies use network-intrusion benchmarks (CICIDS2017, NSL-KDD, UNSW-NB15, CIC-IoT2023) or "
            "unnamed banking datasets. Network-flow data does not describe banking transactions, and unnamed datasets "
            "cannot be reproduced. This pushed the selection in Section 3 toward an open, labelled, transaction-level "
            "banking dataset."),
          PageBreak()]

    # 3 dataset
    cc = p["class_counts"]
    s += [Paragraph("3. Dataset Collection", H1),
          Paragraph("3.1 Selection criteria and candidates", H2),
          P("Five criteria were set before choosing: (1) transaction-level banking records, (2) a fraud or threat "
            "label, (3) an open licence permitting academic use, (4) a size that trains the three models on a laptop "
            "in minutes, and (5) no personal data. The Week 1 plan also listed the Bank Account Fraud (BAF) dataset, "
            "so it was assessed against the same criteria."),
          table([["Candidate", "Type", "Size", "Label", "Licence", "Decision"],
                 ["Bank Transaction Records along Suspicious Flags (Kaggle)", "Simulated bank account transactions",
                  f"{p['rows']:,} rows", "isSuspicious", "MIT", "<b>Selected</b>: named in the CA1 proposal, meets all five criteria"],
                 ["Bank Account Fraud suite (Jesus et al., NeurIPS 2022)", "Synthetic account-opening applications",
                  "1M rows per variant", "fraud_bool", "CC BY-NC-SA 4.0",
                  "Reserve: application fraud, not transactions; large for SVM"],
                 ["PaySim (Lopez-Rojas et al., 2016)", "Simulated mobile-money transfers", "6.36M rows", "isFraud",
                  "CC BY-SA 4.0", "Reserve: mobile money rather than bank accounts"],
                 ["CICIDS2017", "Network flows", "about 2.8M flows", "Attack type", "Academic use",
                  "Rejected: network traffic, not banking transactions"]],
                [3.6, 3, 2, 1.8, 2, 3.6]),
          Paragraph("3.2 Acquisition and verification", H2),
          P(f"The dataset was downloaded with the Kaggle API: <font face='Courier'>kaggle datasets download -d "
            f"{KAGGLE_ID} --unzip -p data</font>. The API token is kept in <font face='Courier'>~/.kaggle/</font> "
            f"and is not committed. Kaggle metadata lists the licence as MIT and describes the data as a realistic "
            f"simulation of bank transactions. The file <font face='Courier'>{p['file']}</font> is {p['size_mb']} MB; "
            f"its SHA-256 checksum is recorded so later weeks can prove the same file is used:"),
          Paragraph(f"<font face='Courier' size='7.5'>{p['sha256']}</font>", B),
          Paragraph("3.3 Data dictionary", H2),
          table([["Column", "Type", "Missing", "Unique", "Min", "Max", "Meaning"]] +
                [[r["column"], r["dtype"], r["missing"], f"{r['unique']:,}", r["min"], r["max"], r["meaning"]] for _, r in dd.iterrows()],
                [2, 1.4, 1.3, 1.4, 1.7, 2.1, 5.1]),
          Paragraph("3.4 Initial quality audit", H2),
          table([["Check", "Result", "Implication"],
                 ["Rows x columns", f"{p['rows']:,} x {p['columns']}", "Small enough to run SVM without sampling"],
                 ["Missing cells", f"{p['missing_cells']}", "No imputation needed"],
                 ["Exact duplicate rows", f"{p['duplicate_rows']}", "No de-duplication needed"],
                 ["Date parsing (dd-mm-yyyy)", f"{p['unparsed_dates']} failures; {p['date_min']} to {p['date_max']} "
                  f"({p['distinct_days']} distinct days)", "Enables a time-ordered split and date features"],
                 ["Negative values", f"debit/credit: 0; balance: {p['negative_balances']}", "Negative balances read as overdrafts; keep"],
                 ["Rows with both debit and credit > 0", f"{p['rows_debit_and_credit']}", "Each row is one direction"],
                 ["Rows with neither debit nor credit", f"{p['rows_no_amount']}", "Every row moves money"],
                 ["Balance values unique", str(p["balance_unique"]), "Balance acts like a row ID; leakage risk"],
                 ["Balance = previous balance + credit - debit", f"{p['balance_follows_prev_row_pct']}% of rows",
                  "Rows are not one running account; balance is not a ledger"],
                 ["Distinct descriptions", f"{p['distinct_descriptions']}", "Low-cardinality categorical; one-hot encode"]],
                [4.5, 4.5, 6]),
          Paragraph("3.5 Class distribution", H2),
          P(f"{cc['1']:,} of {p['rows']:,} transactions ({p['suspicious_rate']:.1%}) are flagged suspicious, a "
            f"{p['imbalance_ratio']}:1 ratio of normal to suspicious. This is only mildly imbalanced, far from "
            f"card-fraud benchmarks (about 578:1), and much higher than a real bank's fraud rate. Two consequences: "
            f"class weights should be enough and SMOTE is tested only as a comparison, and results cannot be read "
            f"as real-world alert volumes. Precision, recall and F1 on the suspicious class stay the main metrics."),
          *fig("w2_class_balance.png", "Figure 1. Class distribution of isSuspicious.", 9),
          PageBreak(),
          Paragraph("3.6 First look at the data", H2),
          P(f"The suspicious rate differs sharply by description (Figure 2). {p['descriptions_always_clean']} of the "
            f"{p['distinct_descriptions']} descriptions are never flagged, while some channels are flagged most of "
            f"the time. The description field alone is therefore highly predictive. That is useful, but it also "
            f"warns that models may learn the labelling rule rather than general threat behaviour. A test on "
            f"descriptions held out of training will be added in model evaluation to check this. Descriptions "
            f"split into two groups: payment channels such as PCA, IMPS and cash deposit are never flagged, while "
            f"online merchants, ticket booking and crypto exchanges are flagged in roughly 70-75% of rows."),
          *fig("w2_rate_by_description.png", "Figure 2. Share of suspicious transactions for the 15 most frequent descriptions."),
          P(f"Suspicious transactions are larger. Among debit rows the median is "
            f"{p['median_nonzero_debit_by_class']['1']:,.0f} for suspicious against "
            f"{p['median_nonzero_debit_by_class']['0']:,.0f} for normal; among credit rows it is "
            f"{p['median_nonzero_credit_by_class']['1']:,.0f} against {p['median_nonzero_credit_by_class']['0']:,.0f} "
            f"(Figure 4). Amounts span several orders of magnitude, so a log transform or robust scaling will be used. "
            f"Over time the data is not uniform (Figure 3): a typical month has about {p['median_rows_per_month']:,} "
            f"rows and a suspicious rate near {p['median_monthly_rate']:.0%}, but {p['busiest_month']} holds "
            f"{p['busiest_month_rows']:,} rows with a {p['busiest_month_rate']:.0%} rate. A random split would mix "
            f"this spike into both train and test, so a time-ordered split will be reported alongside it."),
          *fig("w2_monthly.png", "Figure 3. Monthly transaction volume (solid) and suspicious rate (dashed)."),
          *fig("w2_amounts.png", "Figure 4. Distribution of log10 credit and debit amounts by class."),
          Paragraph("Issues logged for Data Preprocessing (Week 3 onward)", H2),
          table([["#", "Issue", "Planned action"],
                 ["1", "date is text", "Parse; derive month, day of week, day of month"],
                 ["2", "description is text with a channel prefix (e.g. NETTXN:)", "Split prefix and merchant; one-hot encode"],
                 ["3", "Amounts are highly skewed", "log1p transform; RobustScaler for SVM"],
                 ["4", "balance is unique per row", "Test with and without balance to avoid leakage"],
                 ["5", f"{p['imbalance_ratio']}:1 class ratio", "Stratified split; class weights by default, SMOTE on training data only as a comparison"],
                 ["6", f"Volume spike in {p['busiest_month']}", "Report a time-ordered split next to the random split"],
                 ["7", "Description may encode the label", "Add held-out-description and rule-baseline checks"]],
                [0.8, 6.2, 8]),
          ]

    # 4 ethics, 5 status
    s += [Paragraph("4. Ethics and Data Governance", H1),
          P("The dataset is simulated and contains no names, account numbers or other personal data, so GDPR and the "
            "Irish Data Protection Act 2018 are not engaged by the raw data. It is published under the MIT licence, "
            "which permits academic use with attribution. Account-style numbers inside the description field (e.g. "
            "PCA:5001234567:...) are placeholder values, not real identifiers, and are removed when the prefix is "
            "split out. The file is stored locally, is excluded from version "
            "control by .gitignore, and is identified by checksum. Because the data is simulated and its merchant "
            "names are not Irish, results will be presented as evidence about methods, not as measurements of "
            "Irish banks."),
          Paragraph("5. Progress, Risks and Week 3 Plan", H1),
          table([["Item", "Status / note"],
                 ["Literature synthesis, comparison matrix, refined gaps", "Done (Section 2)"],
                 ["Dataset selected against written criteria", "Done (Section 3.1)"],
                 ["Dataset downloaded, checksummed, licence checked", "Done (Section 3.2)"],
                 ["Data dictionary and quality audit", "Done; saved as data_dictionary.csv and dataset_profile.json"],
                 ["Risk: labels may follow a simple rule", "Mitigated by a rule baseline and held-out-description test"],
                 ["Risk: simulated data limits the Irish claim", "Stated as a limitation; Central Bank of Ireland statistics used for context"]],
                [7, 8]),
          Spacer(1, 6),
          P("<b>Week 3 (Literature Review continues; Data Preprocessing starts):</b> add 3-5 papers on concept drift "
            "and rule-versus-ML comparisons; start the preprocessing notebook (date parsing, description split, "
            "log amounts, encoding); create the stratified 80/20 split with a fixed seed and save it for all later "
            "experiments."),
          Paragraph("References", H1)]
    refs = [
        "Ali, M., Raza, A., Akram, M.A., Arif, H. and Ali, A. (2025) 'Machine Learning-Driven Approaches to Cyber Threat Detection: Enhancing IoT Security', Journal of Informatics and IT.",
        "Dhammayogi, M.B.D. and Pramartha, C.R.A. (2026) 'Early Detection of Digital Transaction Fraud in Banking Systems Using the Random Forest Algorithm', JITECS.",
        "Hozouri, A., Mirzaei, A. and Effatparvar, M. (2025) 'A Comprehensive Survey on Intrusion Detection Systems with Advances in ML, DL and Emerging Cybersecurity Challenges', Discover Artificial Intelligence.",
        "Jesus, S., Pombal, J., Alves, D., Cruz, A., Saleiro, P., Ribeiro, R., Gama, J. and Bizarro, P. (2022) 'Turning the Tables: Biased, Imbalanced, Dynamic Tabular Datasets for ML Evaluation', NeurIPS Datasets and Benchmarks Track.",
        "kaggle.com (2025) Bank Transaction Records along Suspicious Flags. Available at: https://www.kaggle.com/datasets/charanmaik/bank-transaction-records-along-suspicious-flags",
        "Kovacevic, A., Radenkovic, S. et al. (2025) 'Artificial Intelligence and Cybersecurity in the Banking Sector: Opportunities and Risks', Contemporary Issues in Economics and Business.",
        "Kumar, B.H., Nuka, S.T., Malempati, M. et al. (2025) 'Big Data in Cybersecurity: Enhancing Threat Detection with AI and ML', Metallurgical and Materials Engineering.",
        "Lopez-Rojas, E.A., Elmir, A. and Axelsson, S. (2016) 'PaySim: A Financial Mobile Money Simulator for Fraud Detection', 28th European Modeling and Simulation Symposium.",
        "Naeem, W., Butt, M.A. and Javeid, U. (2026) 'Machine Learning-Based Fraud Detection Systems and Their Effectiveness in Reducing Cybersecurity Risks in Digital Banking', Social Science Review Archives.",
        "Padmanaban, H., Sharma, Y.K., Sharma, P. et al. (2026) 'Adversarial Machine Learning Framework for Robust Banking Security: The ACTP Tool', Journal of The Institution of Engineers (India).",
        "Sanda, A.M., Mukhtar, U.S. et al. (2026) 'Enhanced Banking Fraud Detection: A Comparative Analysis of Supervised Machine Learning Algorithms', FETICON Proceedings.",
        "Sathupadi, K., Achar, S., Bhaskaran, S.V. et al. (2025) 'BankNet: Real-Time Big Data Analytics for Secure Internet Banking', Big Data and Cognitive Computing, 9(2), p. 24.",
        "Sharafaldin, I., Lashkari, A.H. and Ghorbani, A.A. (2018) 'Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization', ICISSP.",
        "Full list of the 15 reviewed papers: Week 1 Literature Review (v2), references 1-15.",
    ]
    s += [Paragraph(f"{i}. {r}", ParagraphStyle("R", parent=B, fontSize=8.5, leading=11, alignment=0)) for i, r in enumerate(refs, 1)]
    doc = SimpleDocTemplate(str(HERE / "Week2_Report.pdf"), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm, title="Week 2 Progress Report - Jayanth Akarapu")
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
