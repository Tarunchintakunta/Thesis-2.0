# Project Status: terraform-scanner-benchmark (formal CA2)

**Last Updated:** 2026-09-20  
**Branch:** `cursor/vishvaksen-tf-scanner-c8e3`  
**Research Alignment to CA2:** **~62%** (formal scanner/PaC CA2; was ~28% when only the War proxy existed)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMIT-READY)

## Summary

Formal CA2 is a labelled Terraform corpus evaluated with manual review +
Checkov/tfsec + OPA/Rego (P/R/F1/FN per category; scan time; remediation
LOC). This tree implements that programme. The War hybrid is quarantined
under `../_superseded_proxy/` and is **not** evidence. Ethics: **no
terraform apply**.

## Evidence-bound results

See `results/metrics_per_category.csv` and `results/rq_summary.json` after
`python3 scripts/run_all.py`. Numbers in those files are the only scanner
metrics that may be cited. War-hybrid CSV figures must not be cited as
Checkov/tfsec/OPA recall.

## What is done

- Labelled corpus N=240 (60/category, 60% defective, 12 patterns × 5 variants)
- Checkov, tfsec, OPA, scripted-checklist runners
- Category-scoped Rego; a priori check-id maps
- Remediation LOC + scan-time sample + per-category tables
- War artefact quarantined

## Blockers to 100%

1. Independent **human** checklist review (scripted regex is not that)
2. 20% **second-reviewer** subsample (κ not computed)
3. Thesis prose / Verdet comparison / Holm–Bonferroni write-up
4. Optional: extend unmatched check-id maps after first scan (catalog
   classification only)

## AWS

**Not required.** Do not apply insecure modules.
