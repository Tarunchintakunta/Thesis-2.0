# Project Status: vishvaksen-thesis

**Last Updated:** 2026-09-20  
**Branch:** `cursor/vishvaksen-tf-scanner-c8e3`  
**Research Alignment to CA2:** **~62%** (formal scanner/PaC CA2)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMIT-READY)

## Summary

Formal artefact: `terraform-scanner-benchmark/` (N=240 labelled AWS
Terraform modules; Checkov + tfsec + OPA). War hybrid quarantined at
`_superseded_proxy/iac-security/`. Ethics: **no terraform apply**.

## Evidence-bound scanner results

`terraform-scanner-benchmark/results/metrics_per_category.csv`

| Stage | Precision | Recall | F1 | Identified % of labelled defects |
|-------|----------:|-------:|---:|---------------------------------:|
| Scripted checklist | 0.951 | 0.812 | 0.876 | 81.2 |
| Checkov 3.3.19 | 0.771 | 0.562 | 0.651 | 56.2 |
| tfsec v1.28.14 | 0.788 | 0.618 | 0.693 | 61.8 |
| Static union | 0.729 | 0.708 | 0.718 | 70.8 |
| OPA 1.4.2 gate | 1.000 | 0.576 | 0.731 | 57.6 |

Do **not** cite `_superseded_proxy/iac-security/results/` as scanner recall.

## Blockers to 100%

1. Human checklist (scripted regex is a procedure, not a rater)
2. Dual-reviewer 20% subsample
3. Verdet-aligned statistical write-up in the thesis text

## AWS

**Not required** (do not apply). Residual:
`_analysis_extract/reports/vishvaksen_alignment.md`.
