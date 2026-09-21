# Evaluation metrics (this pass)

**N = 240** modules (60 × 4 categories; 144 insecure / 96 secure).  
**Do not terraform apply.**  
Checklist stage is **scripted** (`docs/MANUAL_CHECKLIST.md`), not a human rater.  
Tools: Checkov **3.3.19**, tfsec **======================================================**, OPA **1.4.2**, Terraform **v1.15.8** (parser only).

## RQ — % of labelled insecure modules identified (recall)

| Stage | Identified % | Precision | F1 | FN rate |
|-------|-------------:|----------:|---:|--------:|
| Scripted checklist | 81.2 | 0.951 | 0.876 | 0.188 |
| Checkov (defaults) | 56.2 | 0.771 | 0.651 | 0.438 |
| tfsec (defaults) | 61.8 | 0.788 | 0.693 | 0.382 |
| Static union (Checkov ∨ tfsec) | 70.8 | 0.729 | 0.718 | 0.292 |
| OPA/Rego category gate | 60.4 | 1.000 | 0.753 | 0.396 |

## Per category (recall)

| Stage | public_storage | overpermissive_access | encryption_at_rest | weak_logging |
|-------|---------------:|----------------------:|-------------------:|-------------:|
| Stage | public_storage | overpermissive_access | encryption_at_rest | weak_logging |
|-------|---------------:|----------------------:|-------------------:|-------------:|
| Checklist | 0.722 | 0.944 | 0.778 | 0.806 |
| Checkov | 0.500 | 0.583 | 0.667 | 0.500 |
| tfsec | 0.417 | 0.667 | 0.722 | 0.667 |
| Static union | 0.500 | 0.667 | 0.917 | 0.750 |
| OPA | 0.500 | 0.389 | 0.722 | 0.806 |

tfsec public_storage recall **0.42** and OPA overpermissive_access recall **0.39** are below 0.5 — consistent with the formal expectation that at least one instrument is weak on at least one category. No stage is 1.0 on every category.

OPA precision **1.00** (no false positives on this corpus) with residual FNs mainly from `var.*` indirection (i02) and policy-document shapes the category rules do not walk.

## Scan time

| Tool | Corpus batch (s) |
|------|-----------------:|
| Checklist | 0.003 |
| Checkov | 4.469 |
| Tfsec | 0.767 |
| OPA | 3.388 |

## Remediation LOC (insecure ↔ sibling secure)

Mean **13.1** unified-diff lines (min 8, max 30) across 144 insecure modules.

## Oracle labelling

Ground-truth labels in `labels.csv` are the binding oracle. Live dual-rater panels are out of scope (see CA2_COMMITMENTS.md).

## Verdet / McNemar / Holm–Bonferroni

Evidence-only write-up: `docs/VERDET_COMPARISON.md` (latex fragment
`../latex/verdet_comparison.tex`). Measured McNemar on n=144 insecure;
Holm–Bonferroni (α=0.05, m=4) rejects **only** checklist vs OPA
(adjusted p=7.45×10⁻⁹). Checkov vs tfsec p=0.229 (not significant).
CSV: `mcnemar_pairs.csv`, `holm_bonferroni.csv`.

## Honesty

  scripted samples exist under `docs/`; scripted procedure only for metrics)
- War hybrid CSVs: **not this CA2**
- `results/raw/` is local batch JSON (optional)
