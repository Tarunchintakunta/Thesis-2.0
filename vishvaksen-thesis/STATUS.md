# Project Status: vishvaksen-thesis

**Last Updated:** 2026-09-20  
**Branch:** `feature/aws-ca2-alignment`  
**Research Alignment to CA2:** **~28%** (formal `VishvaksenMachana_25173421_proposal.docx`; prior ~86% was vs superseded War proxy)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMIT-READY)

## Summary

Formal CA2 is a **labelled Terraform corpus** evaluated with **manual review + Checkov/tfsec + OPA/Rego gate** (P/R/F1/FN per category; scan time; remediation effort). Current `iac-security/` still implements **War comment-ablation hybrid** — a **different** programme. Formal ethics: **no live infra apply**. Synthetic corpus: **allowed**.

## Evidence-bound results (seeds 42–46) — artefact as-built (War hybrid; not formal scanners)

Source: `iac-security/results/results_summary.csv` (+ `results_per_seed.csv`).

| Model | Precision | Recall | F1 |
|--------|----------:|-------:|---:|
| ML (rich context) | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| ML (code-only, baseline gap) | 0.768 ± 0.045 | 0.708 ± 0.064 | 0.733 ± 0.019 |
| Rule-Based Only | 1.000 ± 0.000 | 0.483 ± 0.028 | 0.651 ± 0.025 |
| Hybrid (code-only) | 1.000 ± 0.000 | 0.483 ± 0.028 | 0.651 ± 0.025 |

These numbers do **not** answer the formal Checkov/tfsec/OPA CA2.

## What is done
- War-hybrid code + seeds (proxy-era); `CA2_COMMITMENTS.md` rewritten from formal Terraform-scanner proposal

## Blockers to 100% (vs formal)
1. Labelled 4-category Terraform secure/insecure corpus (+ dual review)
2. Manual vs Checkov/tfsec vs OPA gate on identical inputs
3. Per-category metrics + scan time + remediation LOC; pinned tool versions
4. Soft: retire War-hybrid-as-CA2 claims

## AWS
**Not required** (do not apply insecure modules). Residual: `_analysis_extract/reports/vishvaksen_alignment.md`.
