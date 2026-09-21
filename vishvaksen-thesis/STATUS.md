# Project Status: vishvaksen-thesis

**Last Updated:** 2026-09-21  
**Branch:** `main`  
**Research Alignment to CA2:** **~82%** (formal scanner/PaC CA2)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMIT-READY)

## Summary

Formal artefact: `terraform-scanner-benchmark/` (N=240 labelled AWS Terraform
modules; Checkov + tfsec + OPA; scan time; remediation LOC; pinned versions).  
War hybrid quarantined: `iac-security/STATUS.md` → `_superseded_proxy/iac-security/`
(**PROXY — not evidence**). Ethics: **no terraform apply**. AWS **not required**.

## Evidence-bound scanner results

Source: `terraform-scanner-benchmark/results/metrics_per_category.csv`

| Stage | Precision | Recall | F1 | Identified % of labelled defects |
|-------|----------:|-------:|---:|---------------------------------:|
| Scripted checklist | 0.951 | 0.812 | 0.876 | 81.2 |
| Checkov 3.3.19 | 0.771 | 0.562 | 0.651 | 56.2 |
| tfsec v1.28.14 | 0.788 | 0.618 | 0.693 | 61.8 |
| Static union | 0.729 | 0.708 | 0.718 | 70.8 |
| OPA 1.4.2 gate | 1.000 | 0.604 | 0.753 | 60.4 |

Dual-review: **provisional** same-author 20% subsample
(`results/second_review_subsample.json`, κ≈0.775) — **not** an independent human.

Human checklist: **protocol + blank sheet + NON-INDEPENDENT scripted samples**
exist; human pass **not run**.

Verdet prose: McNemar + Holm–Bonferroni on measured pairs
(`docs/VERDET_COMPARISON.md`, `latex/verdet_comparison.tex`) — only
checklist vs OPA significant after Holm (α=0.05).

## Blockers to 100%

1. Independent **human** checklist (scripted regex ≠ human rater; protocol ready)
2. Independent **second human** for 20% subsample (provisional dual-pass exists)

## AWS

**Not required** (do not apply insecure modules). Residual:
`_analysis_extract/reports/vishvaksen_alignment.md`.
