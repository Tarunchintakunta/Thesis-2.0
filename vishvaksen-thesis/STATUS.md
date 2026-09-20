# Project Status: vishvaksen-thesis

**Last Updated:** 2026-09-20  
**Branch:** `cursor/vishvaksen-tf-scanner-c8e3`  
**Research Alignment to CA2:** **~62%** (formal `VishvaksenMachana_25173421_proposal.docx`; prior ~28% was artefact≠CA2)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMIT-READY)

## Summary

Formal CA2 is a **labelled Terraform corpus** evaluated with **manual review +
Checkov/tfsec + OPA/Rego gate** (P/R/F1/FN per category; scan time;
remediation effort). Formal artefact:
`terraform-scanner-benchmark/`. War comment-ablation hybrid is quarantined
at `_superseded_proxy/iac-security/` and is **not** formal evidence.
Ethics: **no live infra apply**. Synthetic corpus: **allowed**.

## Evidence-bound results (formal scanners)

Source: `terraform-scanner-benchmark/results/metrics_per_category.csv` and
`results/rq_summary.json` (populated by `scripts/run_all.py`). Cite those
files, not the superseded War hybrid CSVs.

## What is done

- Formal tree: labelled N=240, four AWS categories, runners, OPA policies
- War proxy quarantined under `_superseded_proxy/`
- `CA2_COMMITMENTS.md` remains the binding contract

## Blockers to 100% (vs formal)

1. Independent human checklist (current checklist stage is scripted)
2. Dual-reviewer 20% subsample
3. Statistical write-up (Holm–Bonferroni / category McNemar in the thesis
   text) and Verdet-aligned discussion
4. Soft: do not cite War-hybrid numbers as scanner recall

## AWS

**Not required** (do not apply insecure modules). Residual:
`_analysis_extract/reports/vishvaksen_alignment.md`.
