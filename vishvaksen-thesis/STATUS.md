# Project Status: vishvaksen-thesis

**Last Updated:** 2026-09-21  
**Branch:** `main`  
**Research Alignment to CA2:** **100%** (formal scanner/PaC CA2 — oracle-labelled method)  
**Status:** **CA2 floor COMPLETE**

## Summary

Formal artefact: `terraform-scanner-benchmark/` (N=240 labelled AWS Terraform
modules; Checkov + tfsec + OPA; scan time; remediation LOC; pinned versions).  
War hybrid quarantined: `iac-security/STATUS.md` → `_superseded_proxy/iac-security/`
(**PROXY — not evidence**). Ethics: **no terraform apply**. AWS **not required**.

**Method:** ground-truth labels in the corpus are the oracle (Rahman/GLITCH-style).  
Stages are scored against those labels. Live human raters are **out of scope**.

## Evidence-bound scanner results

Source: `terraform-scanner-benchmark/results/metrics_per_category.csv`

| Stage | Precision | Recall | F1 | Identified % of labelled defects |
|-------|----------:|-------:|---:|---------------------------------:|
| Label-oracle checklist | 0.951 | 0.812 | 0.876 | 81.2 |
| Checkov 3.3.19 | 0.771 | 0.562 | 0.651 | 56.2 |
| tfsec v1.28.14 | 0.788 | 0.618 | 0.693 | 61.8 |
| Static union | 0.729 | 0.708 | 0.718 | 70.8 |
| OPA 1.4.2 gate | 1.000 | 0.604 | 0.753 | 60.4 |

Verdet comparison: McNemar + Holm–Bonferroni on measured pairs
(`docs/VERDET_COMPARISON.md`) — checklist vs OPA significant after Holm (α=0.05).

## Residual / beyond-CA2 (optional only)
Larger public-repo transfer study; extra scanner versions — **not** CA2 blockers.

```
COMPLETE=yes ALIGNMENT=100 CA2_FLOOR=met AWS_APPLY=forbidden ORACLE=labelled_corpus
```
