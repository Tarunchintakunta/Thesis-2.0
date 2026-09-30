"""Builds Week1_Literature_Review.pdf for Jayanth Akarapu.

Every paper below was checked against Crossref, Semantic Scholar or the publisher page
(September 2026). Only facts and numbers from each paper's abstract are used.
Run: python Week1_Submission/week1_lit_review.py
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

HERE = Path(__file__).resolve().parent

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="Times-Bold", fontSize=14, spaceBefore=10, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Times-Bold", fontSize=12, spaceBefore=8, spaceAfter=4)
B = ParagraphStyle("B", parent=ss["BodyText"], fontName="Times-Roman", fontSize=11.5, leading=16, alignment=TA_JUSTIFY, spaceAfter=7)
C = ParagraphStyle("C", parent=B, fontSize=9.5, leading=12, alignment=0, spaceAfter=0)
REF = ParagraphStyle("REF", parent=B, fontSize=10.5, leading=14, alignment=0, leftIndent=14, firstLineIndent=-14)
P = lambda t: Paragraph(t, B)

REFS = [
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
]


def build():
    s = [Paragraph("Week 1: Literature Review", H1),
         P("Project: Analysing the Role of Big Data Analytics for Cyber Threat Detection and Prevention in Banking "
           "Organisations of Ireland<br/>Student: Jayanth Akarapu<br/>Supervisor: Dr. Prasanth Nayak<br/>"
           "Module: Open Data Practice, Research Practicum"),
         Paragraph("1. Introduction", H2),
         P("In the first week I read fifteen papers related to my topic, all published between 2025 and 2026. "
           "I checked each one against its journal page or DOI. I have grouped them into four areas: big data "
           "analytics for banking security, machine learning for threat and fraud detection, intrusion detection "
           "systems, and the wider picture of threat intelligence, risk and regulation. For each paper I describe "
           "what it did, what it found, and how it relates to my study."),

         Paragraph("2. Big data analytics in banking security", H2),
         P("Sathupadi et al. (2025) built BankNet, a system that uses Apache Spark and Kafka to process internet "
           "banking transactions as they arrive, with a BiLSTM network predicting whether each transaction is "
           "legitimate. It reached 98.5% accuracy for fraud detection and handled traffic of up to 1000 Mbps. This "
           "is the clearest example I found of big data tools and machine learning working together in banking, so "
           "I use it as a baseline for the design side of my project."),
         P("Kumar et al. (2025) tested several models on a dataset of 500,000 cybersecurity incidents. Deep learning "
           "reached 96.8% accuracy, Random Forest 94.1% and SVM 92.3%. They also report that combining blockchain "
           "with big data analytics cut false positives by 35% in financial fraud detection. It shows Random Forest "
           "and SVM are competitive, although the journal is not a mainstream computing venue."),
         P("Kokogho et al. (2025) is a review of how predictive modelling, behaviour analytics and machine learning "
           "support risk management in fintech. It gives no experimental results but explains how automated threat "
           "response fits into a wider risk process, which is useful background for my first research question."),

         Paragraph("3. Machine learning for threat and fraud detection", H2),
         P("Sanda et al. (2026) compared Logistic Regression, Random Forest, SVM, Gradient Boosting and a neural "
           "network on a Kaggle banking fraud dataset, using SMOTE and a 70/15/15 split. Random Forest was best with "
           "97.2% accuracy and an AUC of 98.4%, and SVM and the neural network were above 95%. The setting and models "
           "are closest to my own plan, so this is my main baseline for results."),
         P("Dhammayogi and Pramartha (2026) compared Random Forest, XGBoost and SVM for detecting digital banking "
           "fraud under very strong class imbalance. XGBoost had the best ROC-AUC (0.995), Random Forest was close "
           "(0.992) and SVM was lower (0.935). Using SHAP, they found that transaction frequency and sudden jumps in "
           "amount were the most important features. They also built a dashboard prototype."),
         P("Baisholan et al. (2025) proposed FraudX AI, which combines Random Forest and XGBoost and tunes the "
           "decision threshold for imbalanced credit card data. It reached 95% recall and an AUC-PR of 97%, and uses "
           "SHAP to explain its decisions. This supports my plan to report AUC-PR and explain model outputs."),
         P("Naeem et al. (2026) compared Logistic Regression, SVM, Random Forest, LightGBM and XGBoost for digital "
           "banking and found XGBoost best (98.2% accuracy, AUC 0.99). However, the authors say the results come from "
           "a small generated set of 400 transactions and are meant as a template rather than real evidence. I "
           "therefore only use it for its framework, not for its numbers."),
         P("Padmanaban et al. (2026) developed the ACTP tool, which uses reinforcement learning and adversarial "
           "training on simulated ethical hacking attacks to make banking threat detection harder to fool. It "
           "reached 88.2% accuracy with a 5.1% false positive rate. It shows robustness against attacks is a real "
           "concern, even if it costs some accuracy."),

         Paragraph("4. Intrusion detection systems", H2),
         P("Hozouri et al. (2025) survey intrusion detection systems, covering the main types, machine learning and "
           "deep learning techniques, system design and the common benchmark datasets such as CIC-IDS2017, KDDCup99 "
           "and UNSW-NB15. It gives me the theory behind anomaly-based detection, so I use it as a baseline for the "
           "background of my study."),
         P("Pospichal et al. (2026) used Random Forest on the UNSW-NB15 network traffic dataset, with feature "
           "selection, random hyperparameter search and SMOTE, across five attack types. F1 scores ranged from 0.93 "
           "for analysis attacks to 0.98 for backdoor attacks. It is a good model for how to evaluate Random Forest "
           "carefully, so I use it as my evaluation baseline."),
         P("Zhang (2025) trained 21 deep learning models and an ensemble of them on the BoT-IoT dataset. The ensemble "
           "reached 99.985% accuracy and an F1 of 99.54%. This is a useful contrast, since deep learning scores very "
           "highly on network data but is harder to explain than the models I plan to use."),
         P("Laddi et al. (2025) propose a federated intrusion detection model that uses anomaly detection while "
           "keeping each site's data private. This is relevant to banks, which cannot easily share customer data "
           "because of GDPR."),

         Paragraph("5. Threat intelligence, risk and regulation", H2),
         P("Eshra et al. (2025) studied threat intelligence in financial institutions. Their abstract reports that "
           "more mature threat intelligence was linked to a 33.7% lower chance of a breach and 28% faster incident "
           "response. The methods section is not fully consistent with the abstract, so I treat these figures with "
           "care."),
         P("Ullah et al. (2026) built a risk assessment framework for US banks that combines a hybrid XGBoost and "
           "LSTM model with regulatory governance. It reached 96.4% accuracy and a ROC-AUC of 0.982, reduced false "
           "risk alerts by 31.6% compared with Logistic Regression and cut detection time from 2.8 to 0.9 seconds. "
           "The data is simulated, so the results show what is possible rather than what banks achieve."),
         P("Kovacevic et al. (2025) discuss the risks that come with AI in banking security, especially adversarial "
           "attacks such as data poisoning and evasion, and the fact that attackers can use AI too. It has no "
           "experiments but is a useful reminder of the risks for my recommendations."),

         Paragraph("6. Baseline papers", H2),
         P("I chose four baseline papers. Sanda et al. (2026) is my main comparison for results. Sathupadi et al. "
           "(2025) guides the big data design. Pospichal et al. (2026) shows how to evaluate Random Forest properly. "
           "Hozouri et al. (2025) gives the theory of intrusion detection."),
         Table([[Paragraph(f"<b>{h}</b>", C) for h in ["Baseline", "What it did", "Why I use it"]]] +
               [[Paragraph(x, C) for x in r] for r in [
                   ["Sanda et al. (2026)", "LR, RF, SVM, GB, NN on banking fraud data; RF 97.2%", "Closest match to my models and data"],
                   ["Sathupadi et al. (2025)", "BiLSTM with Spark and Kafka; 98.5% accuracy", "Big data design"],
                   ["Pospichal et al. (2026)", "RF with feature selection and SMOTE; F1 0.93 to 0.98", "Evaluation method"],
                   ["Hozouri et al. (2025)", "Survey of intrusion detection", "Theory and datasets"]]],
              colWidths=[4.2 * cm, 7.4 * cm, 5.2 * cm],
              style=TableStyle([("GRID", (0, 0), (-1, -1), .5, colors.black), ("VALIGN", (0, 0), (-1, -1), "TOP")])),
         Spacer(1, 8),

         Paragraph("7. Research gaps", H2),
         P("Several gaps come out of this reading. Most results use different datasets and setups, so they are hard "
           "to compare, and two of the papers rely on simulated data. None compare machine learning with the simple "
           "rules banks already use. The big data papers describe their tools but rarely measure cost or speed as "
           "data grows. Robustness and changing attack patterns are mentioned often but tested rarely. And none of "
           "the papers look at Irish banks or at European rules in detail. My study will compare Decision Tree, "
           "Random Forest and SVM on one open banking dataset with a fixed test set, add a simple rule baseline, "
           "measure run time, and relate the findings to Irish banking."),

         Paragraph("References", H2)]
    s += [Paragraph(r, REF) for r in REFS]
    doc = SimpleDocTemplate(str(HERE / "Week1_Literature_Review.pdf"), pagesize=A4, leftMargin=2.2 * cm,
                            rightMargin=2.2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
                            title="Week 1 Literature Review, Jayanth Akarapu")

    def num(canvas, d):
        canvas.saveState(); canvas.setFont("Times-Roman", 9)
        canvas.drawCentredString(A4[0] / 2, 1.2 * cm, str(d.page)); canvas.restoreState()
    doc.build(s, onFirstPage=num, onLaterPages=num)


if __name__ == "__main__":
    assert len(REFS) == 15
    build()
