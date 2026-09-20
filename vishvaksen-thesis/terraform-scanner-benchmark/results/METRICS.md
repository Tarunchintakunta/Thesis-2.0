# Evaluation metrics (this pass)

**N = 240** modules (60 × 4 categories; 144 insecure / 96 secure).  
**Do not terraform apply.**  
Checklist stage is **scripted** (`docs/MANUAL_CHECKLIST.md`), not a human rater.  
Tools: Checkov **3.3.19**, tfsec **v1.28.14**, OPA **1.4.2**, Terraform **v1.15.8** (parser only).

## RQ — % of labelled insecure modules identified (recall)

| Stage | Identified % | Precision | F1 | FN rate |
|-------|-------------:|----------:|---:|--------:|
| Scripted checklist | 81.2 | 0.951 | 0.876 | 0.188 |
| Checkov (defaults) | 56.2 | 0.771 | 0.651 | 0.438 |
| tfsec (defaults) | 61.8 | 0.788 | 0.693 | 0.382 |
| Static union (Checkov ∨ tfsec) | 70.8 | 0.729 | 0.718 | 0.292 |
| OPA/Rego category gate | 57.6 | 1.000 | 0.731 | 0.424 |

## Per category (recall)

| Stage | public_storage | overpermissive_access | encryption_at_rest | weak_logging |
|-------|---------------:|----------------------:|-------------------:|-------------:|
| Checklist | 0.722 | 0.944 | 0.778 | 0.806 |
| Checkov | 0.500 | 0.583 | 0.667 | 0.500 |
| tfsec | 0.417 | 0.667 | 0.722 | 0.667 |
| Static union | 0.500 | 0.667 | 0.917 | 0.750 |
| OPA | 0.500 | 0.389 | 0.722 | 0.694 |

tfsec public_storage recall **0.42** and OPA overpermissive_access recall **0.39** are below 0.5 — consistent with the formal expectation that at least one instrument is weak on at least one category. No stage is 1.0 on every category.

OPA precision **1.00** (no false positives on this corpus) with residual FNs mainly from `var.*` indirection (i02) and policy-document shapes the category rules do not walk.

## Scan time

| Tool | Corpus batch (s) | Mean per-module sample (s) |
|------|-----------------:|---------------------------:|
| Checklist | 0.003 | ~1.4e-5 |
| Checkov | 5.5 | ~4.0 (n=12 sample; process start-up) |
| tfsec | 0.9 | ~0.31 |
| OPA | 3.3–3.7 | ~0.015 |

## Remediation LOC (insecure ↔ sibling secure)

Mean **13.1** unified-diff lines (min 8, max 30) across 144 insecure modules.

## Honesty

- Second reviewer: **NOT RUN**
- Human checklist: **NOT RUN**
- War hybrid CSVs: **not this CA2**
- `results/raw/` is local batch JSON (gitignored)
