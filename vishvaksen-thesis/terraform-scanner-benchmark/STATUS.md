# Project Status: terraform-scanner-benchmark (formal CA2)

**Last Updated:** 2026-09-21  
**Branch:** `cursor/vishvaksen-tf-scanner-ca2-8385`  
**Research Alignment to CA2:** **~72%**  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMIT-READY)

## Summary

Labelled Terraform corpus (N=240; 4 AWS categories; ~60% defective) evaluated
with scripted checklist + Checkov/tfsec + OPA/Rego. War hybrid is under
`../_superseded_proxy/` / `../iac-security/STATUS.md` (PROXY) and is **not**
evidence. **No terraform apply.**

## Evidence-bound results (this host)

Source: `results/metrics_per_category.csv`, `results/rq_summary.json`.  
Pinned: Checkov 3.3.19, tfsec v1.28.14, OPA 1.4.2 (see `results/tool_versions.json`).

| Stage | Prec | Rec | F1 | FN | Identified % |
|-------|-----:|----:|---:|---:|-------------:|
| Scripted checklist | 0.951 | 0.812 | 0.876 | 0.188 | 81.2 |
| Checkov | 0.771 | 0.562 | 0.651 | 0.438 | 56.2 |
| tfsec | 0.788 | 0.618 | 0.693 | 0.382 | 61.8 |
| Checkov ∨ tfsec | 0.729 | 0.708 | 0.718 | 0.292 | 70.8 |
| OPA/Rego gate | 1.000 | 0.604 | 0.753 | 0.396 | 60.4 |

Dual-review subsample: **PROVISIONAL** same-author dual-pass
(`results/second_review_subsample.json`, κ≈0.775). Not independent human κ.

Checklist is **not** independent human review.

## Blockers to 100%

1. Independent human checklist
2. Independent second-human 20% subsample (provisional recorded)
3. Thesis prose vs Verdet (Holm–Bonferroni write-up)

## AWS

**Not required.** Do not apply insecure modules.
