# Design rationale — Vishvaksen (oracle labelling; no live human panels)

## Binding choice
This thesis evaluates Terraform scanners against a **purpose-built labelled oracle corpus**
(Rahman / GLITCH-style ground truth). Each module’s secure/insecure label is fixed at
construction. Precision, recall, F1 and false-negative rates are computed by comparing
tool outputs to those labels.

## What is in scope
- Labelled N=240 AWS Terraform modules (four misconfiguration categories)
- Label-oracle checklist, Checkov, tfsec, OPA/Rego CI gate on identical inputs
- Scan time and remediation LOC
- Statistical comparison vs Verdet-style claims using measured contingency tables

## What is explicitly out of scope
- Live independent human review panels or dual-rater agreement studies
- Applying insecure Terraform modules to a live AWS account

## Why this still answers the CA2 RQ
The formal RQ asks what **percentage of labelled** AWS misconfigurations scanners and a
policy gate identify. That question is answered by scoring tools against the published
labels — the same oracle design used in prior IaC benchmark work (e.g. Rahman et al.
Kubernetes oracle). Live human panels are a different study (inter-rater reliability) and
are not required to answer the labelled-detection RQ.

## Thesis writing rule
Do **not** claim, recommend, or leave open “second human” / dual-review work in the
report, abstract, or conclusions. Optional future work may mention broader external
validation on public repos — not live human panels as a CA2 residual.
