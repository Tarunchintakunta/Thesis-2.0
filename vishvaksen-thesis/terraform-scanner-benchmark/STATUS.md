# Project Status: terraform-scanner-benchmark (formal CA2)

**Last Updated:** 2026-09-20  
**Branch:** `cursor/vishvaksen-tf-scanner-c8e3`  
**Research Alignment to CA2:** **~62%**  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMIT-READY)

## Summary

Labelled Terraform corpus (N=240) evaluated with scripted checklist +
Checkov/tfsec + OPA/Rego. War hybrid is under `../_superseded_proxy/` and is
**not** evidence. **No terraform apply.**

## Evidence-bound results (this host)

Source: `results/metrics_per_category.csv`, `results/rq_summary.json`.  
Pinned: Checkov 3.3.19, tfsec v1.28.14, OPA 1.4.2.

| Stage | Prec | Rec | F1 | FN | Identified % |
|-------|-----:|----:|---:|---:|-------------:|
| Scripted checklist | 0.951 | 0.812 | 0.876 | 0.188 | 81.2 |
| Checkov | 0.771 | 0.562 | 0.651 | 0.438 | 56.2 |
| tfsec | 0.788 | 0.618 | 0.693 | 0.382 | 61.8 |
| Checkov ∨ tfsec | 0.729 | 0.708 | 0.718 | 0.292 | 70.8 |
| OPA/Rego gate | 1.000 | 0.576 | 0.731 | 0.424 | 57.6 |

Per-category recall: see `results/METRICS.md`. tfsec public_storage Rec=0.42;
OPA overpermissive_access Rec=0.39. Mean remediation diff **13.1** LOC.

Checklist is **not** independent human review.

## Blockers to 100%

1. Independent human checklist
2. 20% second-reviewer subsample
3. Thesis prose vs Verdet (Holm–Bonferroni write-up)

## AWS

**Not required.** Do not apply insecure modules.
