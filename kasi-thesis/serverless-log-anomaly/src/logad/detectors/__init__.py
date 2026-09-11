"""The three detection approaches (the independent variable).

D1  source-free one-class: OC-SVM and Isolation Forest, trained only on the
    application's own certified-clean logs
D2  transfer: ELFA-Log style pseudo-labelling + feature alignment from a
    labelled public corpus (Loghub BGL)
D3  CloudWatch-style threshold alarms (operational reference line)

Every detector exposes ``score(X)`` (higher = more anomalous) and
``predict(X)`` (bool per window).
"""
