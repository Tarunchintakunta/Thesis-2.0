# Alignment — terraform-scanner-benchmark vs formal CA2

**Date:** 2026-09-20  
**Binding:** `../CA2_COMMITMENTS.md` (formal proposal extract).  
**Status:** **NOT COMPLETE**. Alignment **~62%** (was ~28% when the only artefact was the War hybrid).

## Compact (same axes as residual note)

`RQ6 Obj7 Method6 Impl7 Exp6 Metrics7 Evidence6 Claims5 Rubric5` → **~62/100**

This is not 100. Dual review, human checklist, statistical write-up, and
the thesis prose (LaTeX vs Verdet) remain.

## Objectives vs this tree

| Objective | Evidence | Gap |
|-----------|----------|-----|
| 1 Labelled 4-category corpus ~60/cat, ~60% defective | `corpus/` N=240, `labels.csv` | 20% second reviewer **not run** |
| 2 Manual vs Checkov+tfsec vs OPA on same inputs | runners + `results/verdicts.csv` | Manual is **scripted checklist**, not a human |
| 3 Scan time + remediation LOC | `scan_times.csv`, `remediation_loc.csv` | Checkov/tfsec per-module time is a **sample** |
| 4 P/R/F1/FN per category | `metrics_per_category.csv` | Holm–Bonferroni / full ANOVA write-up not done |

## What is not evidence

- `../_superseded_proxy/iac-security/` War TF-IDF hybrid
- Any `terraform apply` (forbidden)
- Invented dual-review κ
