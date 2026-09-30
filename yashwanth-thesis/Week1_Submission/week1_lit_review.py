"""Builds Week1_Literature_Review.pdf for Yashwanth.

Every paper below was checked against Crossref/OpenAlex or the publisher page
(September 2026). Only facts and numbers that appear in each paper's abstract
or open full text are used.  Run: python Week1_Submission/week1_lit_review.py
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

# (short cite, full reference, year, baseline?)
PAPERS = {
    1: ("Jamil et al. (2025)", "Jamil, M.H., Talukder, S.I., Hosen, A., Arafat, Y. and Sozib, H.M. (2025) Big data analytics and its usage on financial fraud detection in the USA. Advances in Machine Learning, IoT and Data Security, 1(2). https://doi.org/10.63471/amlid25001"),
    2: ("Elumilade et al. (2025)", "Elumilade, O.O., Ogundeji, I.A., Achumie, G.O. and Omokhoa, H.E. (2025) Leveraging financial data analytics for business growth, fraud prevention, and risk mitigation in markets. Gulf Journal of Advance Business Research, 3(3), pp. 906-922. https://doi.org/10.51594/gjabr.v3i3.119"),
    3: ("Gkegkas et al. (2025)", "Gkegkas, M., Kydros, D. and Pazarskis, M. (2025) Using data analytics in financial statement fraud detection and prevention: a systematic review of methods, challenges, and future directions. Journal of Risk and Financial Management, 18(11), 598. https://doi.org/10.3390/jrfm18110598"),
    4: ("Salunke et al. (2025)", "Salunke, Y., Phalke, S., Madavi, M., Kumre, P. and Bobhate, G. (2025) Fraud detection: a hybrid approach with logistic regression, decision tree, and random forest. Cureus Journal of Computer Science, 2(1). https://doi.org/10.7759/s44389-024-02350-5"),
    5: ("Albalawi and Dardouri (2025)", "Albalawi, T. and Dardouri, S. (2025) Enhancing credit card fraud detection using traditional and deep learning models with class imbalance mitigation. Frontiers in Artificial Intelligence, 8, 1643292. https://doi.org/10.3389/frai.2025.1643292"),
    6: ("Appavu (2025)", "Appavu, N. (2025) AI and ML approaches for credit card fraud detection: a comparative study of logistic regression and decision tree techniques. In: 2025 3rd International Conference on Intelligent Data Communication Technologies and Internet of Things (IDCIoT). IEEE, pp. 2068-2074. https://doi.org/10.1109/IDCIoT64235.2025.10915092"),
    7: ("Andrade-Arenas and Yactayo-Arias (2025)", "Andrade-Arenas, L. and Yactayo-Arias, C. (2025) Comparative analysis of machine learning models for credit card fraud detection using SMOTE for class imbalance. International Journal of Safety and Security Engineering, 15(5), pp. 893-901. https://doi.org/10.18280/ijsse.150504"),
    8: ("Ma et al. (2026)", "Ma, C., Zhang, L., Xing, Z. and Su, J. (2026) Credit card fraud detection under extreme class imbalance using leakage-safe feature selection and GA-based hyperparameter optimization. Applied Sciences, 16(13), 6734. https://doi.org/10.3390/app16136734"),
    9: ("Baisholan et al. (2025)", "Baisholan, N., Dietz, J.E., Gnatyuk, S., Turdalyuly, M., Matson, E.T. and Baisholanova, K. (2025) A systematic review of machine learning in credit card fraud detection under original class imbalance. Computers, 14(10), 437. https://doi.org/10.3390/computers14100437"),
    10: ("Horobets et al. (2025)", "Horobets, N., Reznik, O., Maliyk, V., Vyhivskyi, I. and Bobrishova, L. (2025) Artificial intelligence technologies in banking: challenges and opportunities for anti-money laundering in the context of EU regulatory initiatives. Journal of Money Laundering Control, 28(4-5), pp. 593-608. https://doi.org/10.1108/JMLC-03-2025-0041"),
    11: ("Khan et al. (2026)", "Khan, S.U., Zafar, U., Imran, S. and Ali, M. (2026) Artificial intelligence-driven fraud detection in FinTech: strengthening cybersecurity against digital financial scams. Journal of Business Insight and Innovation, 5(6), pp. 72-82. https://doi.org/10.63544/jbii.v5i6.116"),
    12: ("Preciado Martinez et al. (2025)", "Preciado Martinez, P.M., Reier Forradellas, R.F., Garay Gallastegui, L.M. and Nanez Alonso, S.L. (2025) Comparative analysis of machine learning models for the detection of fraudulent banking transactions. Cogent Business and Management, 12(1), 2474209. https://doi.org/10.1080/23311975.2025.2474209"),
    13: ("Haider et al. (2024)", "Haider, Z.A., Khan, F.M., Zafar, A., Nabila and Khan, I.U. (2024) Optimizing machine learning classifiers for credit card fraud detection on highly imbalanced datasets using PCA and SMOTE techniques. VAWKUM Transactions on Computer Sciences, 12(2), pp. 28-49. https://doi.org/10.21015/vtcs.v12i2.1921"),
    14: ("Bian (2025)", "Bian, C. (2025) Credit card fraud detection: machine learning and deep learning advances, challenges, and future directions. ITM Web of Conferences, 78, 02023. https://doi.org/10.1051/itmconf/20257802023"),
    15: ("Alrasheedi (2025)", "Alrasheedi, M.A. (2025) Enhancing fraud detection in credit card transactions: a comparative study of machine learning models. Computational Economics, 68(1), pp. 779-805. https://doi.org/10.1007/s10614-025-11071-3"),
}
EXTRA = {
    8: ("Ma et al. (2026) also use the Kaggle European dataset, but they are careful to keep the test set in its "
        "original, imbalanced form (85,443 transactions with 148 frauds). They use Random Forest to select "
        "features, try several resampling methods and tune XGBoost with a genetic algorithm. Their best model "
        "reached a PR-AUC of 0.798 and an F1 of 0.809 for the fraud class, and halved false positives from 22 to "
        "11. An important finding is that resampling does not always help, and it should be judged on the real "
        "class distribution. This is a warning I will follow when I apply SMOTE."),
    10: ("Horobets et al. (2025) look at AI in banking from a legal side. They discuss the problems banks face when "
         "using AI for anti-money laundering under the EU's Sixth Anti-Money Laundering Directive and the AI Act. "
         "They conclude that matching legal demands such as explainability, confidentiality, fairness and data "
         "security with what AI systems can actually do is still unresolved, and that the EU needs clearer rules "
         "for AI in finance. This is the closest paper to the Irish and European angle of my project."),
}


def c(n):
    return PAPERS[n][0]


def build():
    s = [Paragraph("Week 1: Literature Review", H1),
         P("Project: Determining the Role of Big Data Applications in Fraud Detection and Financial Security in "
           "Financial Institutions of Ireland<br/>Student: Yashwanth<br/>Supervisor: Dr. Prasanth Nayak<br/>"
           "Module: Open Data Practice, Research Practicum"),
         Paragraph("1. Introduction", H2),
         P("For the first week I read fifteen papers related to my topic. All of them were published between late "
           "2024 and 2026, and I checked each one against its journal page or DOI. I grouped them into three areas: "
           "how big data and analytics are used against fraud, how machine learning models perform on credit card "
           "and banking fraud, and what the wider challenges are, such as class imbalance, regulation and trust. "
           "For each paper I note what it did, what it found, and what it means for my own study."),

         Paragraph("2. Big data and analytics in fraud detection", H2),
         P(f"{c(1)} look at fraud detection in the USA. They train Logistic Regression, Decision Tree and Random "
           f"Forest on transaction data with demographic and location features, both before and after tuning. All "
           f"models reach very high accuracy, so the authors compare them on errors instead. Random Forest gives the "
           f"best balance, with 204 false positives against 594 for the Decision Tree. The paper talks about big data "
           f"in general terms but does not test any big data platform, and it does not look at Europe."),
         P(f"{c(2)} is a review paper rather than an experiment. It explains how financial data analytics supports "
           f"fraud prevention through machine learning, anomaly detection and real-time monitoring. It also lists the "
           f"barriers firms face, mainly data privacy and old legacy systems. It gives useful background for my first "
           f"research question but no results I can compare against."),
         P(f"{c(3)} carried out a systematic review of 43 studies from 2010 to 2024 on financial statement fraud. "
           f"They group the methods into supervised machine learning, statistical anomaly detection, network analysis "
           f"and real-time monitoring. The main problems they report are class imbalance, poor interpretability and "
           f"weak governance, and they call for explainable AI and longer field studies. This review supports my plan "
           f"to explain model decisions, not just report scores."),

         Paragraph("3. Machine learning models for card and banking fraud", H2),
         P(f"{c(4)} compare Logistic Regression, Decision Tree and Random Forest on a public credit card fraud dataset "
           f"and then combine them into a hybrid ensemble. The ensemble beats each model on its own in precision, "
           f"recall and accuracy. They also suggest grouping cardholders by how much they spend. This is very close to "
           f"my own plan, since I use the same three models, so I have chosen it as a baseline paper."),
         P(f"{c(5)} use the same Kaggle European dataset that I use (284,807 transactions, 492 of them fraud). They "
           f"test Logistic Regression, Decision Tree, Random Forest, XGBoost and a deep learning model, and use SMOTE "
           f"to deal with the imbalance. Random Forest did best in their abstract, with 99.95% accuracy, an F1 score of "
           f"0.8256 and a ROC-AUC of 0.9759, and they also checked their results on the PaySim dataset. Because the "
           f"data and models match mine so closely, this is my main baseline for comparing results."),
         P(f"{c(6)} compares Logistic Regression and Decision Tree on the European card dataset. Instead of treating "
           f"every transaction the same, the study groups cardholders by spending, builds features over a sliding "
           f"window of recent transactions, and adds a feedback loop so the model can adjust when fraud patterns "
           f"change. The idea of building behaviour features from past transactions is something I can try in "
           f"feature engineering."),
         P(f"{c(7)} compare seven models on the Kaggle dataset after applying SMOTE, using an 80/20 split. Random "
           f"Forest had the best F1 score (0.872, AUC 0.978) and XGBoost was close behind (F1 0.837, AUC 0.983). "
           f"Logistic Regression only reached an F1 of 0.110, which shows how poorly a linear model can do on this "
           f"data even when its accuracy looks high. I use this paper as a baseline for handling class imbalance."),
         P(EXTRA.get(8, "")),
         P(f"{c(12)} test Random Forest, a neural network and Naive Bayes on about 565,000 real bank transfers. "
           f"Random Forest was the most reliable, detecting fraud with 95.79% accuracy, and the authors argue it could "
           f"be used to stop fraudulent transfers in real time. This shows the same model ranking holds outside the "
           f"card dataset."),
         P(f"{c(13)} apply scaling, PCA and SMOTE before comparing six models on an imbalanced credit card dataset. "
           f"Logistic Regression, SVM, KNN and XGBoost all reached about 97% accuracy, with Decision Tree and Random "
           f"Forest at 96% or more. The paper only reports accuracy, which on imbalanced data says little about how "
           f"many frauds were actually caught."),
         P(f"{c(15)} compares seven models, including SVM, Random Forest, XGBoost and neural networks, on three "
           f"different datasets. Decision Tree, Random Forest and the neural network reached 0.99 accuracy on the "
           f"balanced data, and Random Forest reached 0.97 on the imbalanced dataset with better fraud precision and "
           f"recall. I use it as a baseline because it tests the models on more than one dataset."),

         Paragraph("4. Imbalance, regulation and trust", H2),
         P(f"{c(9)} review only studies that keep the original class imbalance when training and testing, which is "
           f"the realistic setting. They find that tree-based ensembles are the most common choice, that most studies "
           f"rely on the same few public datasets, and that the precision-recall curve (AUC-PR) is used much less than "
           f"it should be. Explainability methods, mostly SHAP, are rare. Because of this review I will report AUC-PR "
           f"alongside the usual metrics."),
         P(EXTRA.get(10, "")),
         P(f"{c(11)} surveyed 385 people working in FinTech, digital banking and cybersecurity in Pakistan. The "
           f"respondents rated AI fraud detection, machine learning, real-time monitoring and anomaly detection as "
           f"effective, with average scores above 4 on a five-point scale. It is a survey of opinions, not a model "
           f"test, but it shows that people in the industry trust these tools."),
         P(f"{c(14)} reviews rule-based systems, machine learning and deep learning for card fraud. The paper points "
           f"out four ongoing problems: models that are hard to explain, class imbalance, fraud patterns that change "
           f"over time, and limited access to data because of privacy. It suggests federated learning and combining "
           f"GAN-generated data with SMOTE as possible solutions."),

         Paragraph("5. Baseline papers", H2),
         P(f"I chose four papers as baselines. {c(5)} is the main one, because it uses the same dataset and models as "
           f"my study and reports F1 and ROC-AUC that I can compare with. {c(4)} uses exactly my three models. "
           f"{c(7)} shows the effect of SMOTE on the same data. {c(15)} tests the models on more than one dataset."),
         Table([[Paragraph(f"<b>{h}</b>", C) for h in ["Baseline", "Data", "Models", "Why I use it"]]] +
               [[Paragraph(x, C) for x in r] for r in [
                   [c(5), "Kaggle European cards, PaySim", "LR, DT, RF, XGBoost, deep learning", "Same data, comparable F1 and ROC-AUC"],
                   [c(4), "Public card dataset", "LR, DT, RF, hybrid", "Same three models as my study"],
                   [c(7), "Kaggle European cards", "Seven models with SMOTE", "Imbalance handling"],
                   [c(15), "Three datasets", "Seven models", "Tests beyond one dataset"]]],
              colWidths=[4.2 * cm, 3.8 * cm, 4.2 * cm, 4.8 * cm],
              style=TableStyle([("GRID", (0, 0), (-1, -1), .5, colors.black), ("VALIGN", (0, 0), (-1, -1), "TOP")])),
         Spacer(1, 8),

         Paragraph("6. Research gaps", H2),
         P("Reading these papers together, a few gaps stand out. None of them look at Irish or European regulation, "
           "such as GDPR or the Central Bank of Ireland, even though several say regulation matters. Many report "
           "accuracy as the main result, which is misleading when fewer than 1% of transactions are fraud. Only a "
           "few use AUC-PR. Most use the same Kaggle dataset without mentioning its duplicate rows or how SMOTE was "
           "applied. And explainability is discussed far more often than it is actually shown. My study will "
           "compare Logistic Regression, Decision Tree and Random Forest with metrics suited to imbalanced data, "
           "explain which features drive the predictions, and relate the results to Irish financial institutions."),

         Paragraph("References", H2)]
    s += [Paragraph(PAPERS[n][1], REF) for n in sorted(PAPERS, key=lambda n: PAPERS[n][1])]
    doc = SimpleDocTemplate(str(HERE / "Week1_Literature_Review.pdf"), pagesize=A4, leftMargin=2.2 * cm,
                            rightMargin=2.2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
                            title="Week 1 Literature Review, Yashwanth")

    def num(canvas, d):
        canvas.saveState(); canvas.setFont("Times-Roman", 9)
        canvas.drawCentredString(A4[0] / 2, 1.2 * cm, str(d.page)); canvas.restoreState()
    doc.build(s, onFirstPage=num, onLaterPages=num)


if __name__ == "__main__":
    assert all(PAPERS.values()), "papers 8 and 10 still need confirmed replacements"
    build()
