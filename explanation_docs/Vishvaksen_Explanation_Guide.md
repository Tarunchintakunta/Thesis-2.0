# Terraform / IaC Security Scanner Benchmark on Labelled AWS Terraform Modules

**Student:** Vishvaksen Machana  
**Student ID:** 25173421  
**Programme:** MSc Cloud Computing, National College of Ireland  
**Format:** Short explanation guide (target 5–6 pages)

---

## What is the project?

Labelled N=240 AWS Terraform benchmark; Checkov+tfsec+OPA vs label oracle; no apply. Artefact: terraform-scanner-benchmark/ only.

## Problem + example

Scanners may miss labelled defects. Building-inspection analogy.

## Baseline

Verdet et al. 2025 DOI 10.1007/s10664-024-10610-0; gap = labelled recall/F1 + OPA.

## RQ / solution

Oracle F1=0.876; Checkov 0.651; tfsec 0.693; union 0.718; OPA 0.753.

## Dataset

N=240; 4 categories; labels.csv; no PII; no apply.

## AWS / tech

- Checkov 3.3.19, tfsec v1.28.14, OPA 1.4.2
- Python + HCL2; Terraform never applied

## Speaking script

240 labelled modules; checklist+scanners+OPA; Verdet gap = labelled recall.

## STATUS + Q&A

- CA2 COMPLETE; apply forbidden.
- Apply? No.
- Proxy? No.
- Versions pinned.
- Checkov recall 0.562.
- Gap = labelled P/R/F1.
