# PROXY STATUS — War comment-ablation hybrid

**Quarantine:** Yes — **not** the binding CA2 artefact.  
**Last Updated:** 2026-09-21  

## What this is
Pre-formal-CA2 artefact implementing War et al.–style comment ablation with
rule + TF-IDF hybrid detectors on synthetic snippets (`results/results_summary.csv`).

## What this is not
It does **not** implement labelled Terraform modules × Checkov × tfsec ×
OPA/Rego gate. Those live in `../../terraform-scanner-benchmark/`.

## Citation rule
Proxy Precision/Recall/F1 figures answer a **different** research question.
Do not fold them into formal scanner identification rates.
