# Alignment — terraform-scanner-benchmark vs formal CA2

**Date:** 2026-09-21  
**Binding:** `../CA2_COMMITMENTS.md` (formal proposal extract).  
**Status:** **NOT COMPLETE**. Alignment **~82%** (was ~72% before checklist
protocol + Verdet Holm/McNemar prose; was ~62% before dual-review artefact).

## Compact (same axes as residual note)

`RQ7 Obj9 Method10 Impl9 Exp7 Metrics10 Evidence10 Claims10 Rubric10` → **~82/100**

Measured on this pass (N=240 insecure=144): Checkov identified **56.2%**,
tfsec **61.8%**, union **70.8%**, OPA **60.4%** of labelled defects.
Scripted checklist **81.2%** (not a human rater). Per-category tables:
`../results/METRICS.md`. Holm–Bonferroni: only checklist vs OPA rejects
(`docs/VERDET_COMPARISON.md`).

## Objectives vs this tree

| Objective | Evidence | Gap |
|-----------|----------|-----|
| 1 Labelled 4-category corpus ~60/cat, ~60% defective | `corpus/` N=240, `labels.csv` | Independent second human **not run** (provisional same-author κ recorded) |
| 2 Manual vs Checkov+tfsec vs OPA on same inputs | runners + `results/verdicts.csv` + human protocol/sheet | Manual **metrics** still scripted; human sheets not filled |
| 3 Scan time + remediation LOC | `scan_times.csv`, `remediation_loc.csv` | Checkov/tfsec per-module time is a **sample** |
| 4 P/R/F1/FN per category | `metrics_per_category.csv` + McNemar/Holm write-up | Closed for statistical prose |

## What is not evidence

- `../_superseded_proxy/iac-security/` War TF-IDF hybrid
- Any `terraform apply` (forbidden)
- Invented dual-review κ / invented independent human sheets
- Scripted checklist cited as human-review accuracy
