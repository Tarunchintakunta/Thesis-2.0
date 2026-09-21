# Alignment — terraform-scanner-benchmark

**CA2 floor: 100%** (oracle-labelled method).

| Objective | Evidence |
|-----------|----------|
| Labelled 4-category corpus | `corpus/` N=240, `labels.csv` |
| Checklist vs Checkov/tfsec vs OPA | `results/metrics_per_category.csv` |
| Scan time + remediation LOC | results CSVs |
| Per-category P/R/F1/FN | results CSVs |
| Verdet stats | `docs/VERDET_COMPARISON.md` |

Live human panels: **out of scope**. AWS apply: **forbidden**.
