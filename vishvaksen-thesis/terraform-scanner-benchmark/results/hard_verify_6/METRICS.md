# Evaluation metrics (this pass)

**N = 240** modules (60 × 4 categories; 144 insecure / 96 secure).  
**Do not terraform apply.**  
Tools: Checkov **3.3.19**, tfsec **v1.28.14**, OPA **1.4.2** (parser only).

## RQ — % of labelled insecure modules identified (recall)

| Stage | Identified % | Precision | Recall | F1 | FN rate | Acc |
|-------|-------------:|----------:|-------:|---:|--------:|----:|
| Scripted checklist | 81.2 | 0.951 | 0.812 | 0.876 | 0.188 | 0.863 |
| Checkov (defaults) | 91.7 | 0.759 | 0.917 | 0.830 | 0.083 | 0.775 |
| tfsec (defaults) | 61.8 | 0.788 | 0.618 | 0.693 | 0.382 | 0.671 |
| Static union (Checkov ∨ tfsec) | 93.8 | 0.730 | 0.938 | 0.821 | 0.062 | 0.754 |
| OPA/Rego category gate | 60.4 | 1.000 | 0.604 | 0.753 | 0.396 | 0.762 |

## Per category (recall)

| Stage | public_storage | overpermissive_access | encryption_at_rest | weak_logging |
|-------|---------------:|----------------------:|-------------------:|-------------:|
| Checklist | 0.722 | 0.944 | 0.778 | 0.806 |
| Checkov | 1.000 | 0.917 | 1.000 | 0.750 |
| Tfsec | 0.417 | 0.667 | 0.722 | 0.667 |
| Static union | 1.000 | 0.917 | 1.000 | 0.833 |
| Opa | 0.500 | 0.389 | 0.722 | 0.806 |

**Mapping note (2026-09-23):** Checkov ALL recall **0.917** after classifying fired-but-unmatched catalog IDs into `mappings/checkov_ids.json` (labels unchanged). Residual FN (12/144) retained as evidenced negative.

## Scan time (batch seconds from verdict payloads)

| Tool | Corpus batch (s) |
|------|-----------------:|
| Checklist | 0.0038009972777217627 |
| Checkov | 3.904719916987233 |
| Tfsec | 0.6823047499929089 |
| OPA | 2.793894547765376 |

## Verdet / McNemar / Holm–Bonferroni

See `docs/VERDET_COMPARISON.md` and `results/mcnemar_pairs.csv` / `holm_bonferroni.csv` (recomputed by `scripts/evaluate.py` on this pass).

