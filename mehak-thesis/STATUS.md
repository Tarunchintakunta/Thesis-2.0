# Project Status: mehak-thesis

**Last Updated:** 2026-09-20  
**Branch:** `feature/aws-ca2-alignment`  
**Research Alignment to CA2:** **~88%** (proxy via `CA2_COMMITMENTS.md`; formal CA2 **NOT FOUND**)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMIT-READY)

## Summary

Local synthetic campaign reproduces Thapliyal (2026) MHSA-PerHead underprediction on cluster telemetry and evaluates MHSA-Fused. **No live AWS.** Lambda/SAM/GitHub Actions are scaffolds only.

## Evidence-bound results (seeds 42–46)

Source: `mhsa-tdl-framework/results/results_summary.csv` (+ `results_per_seed.csv`).

| Model | Accuracy | Macro-F1 | Transient Recall | Underprediction Bias |
|---|---|---|---|---|
| Threshold Baseline | 0.847 ± 0.002 | 0.313 ± 0.002 | 0.025 ± 0.002 | 1.715 ± 0.011 |
| MHSA-PerHead (baseline) | 0.873 ± 0.011 | 0.565 ± 0.008 | 0.864 ± 0.022 | 0.290 ± 0.076 |
| MHSA-Fused (improved) | 0.863 ± 0.014 | 0.560 ± 0.010 | 0.884 ± 0.021 | 0.273 ± 0.050 |

Fusion Δ is directionally consistent but **within ~1σ** across seeds — report as modest, not decisive.

## What is done
- Code + 5-seed train/eval pipeline; pytest suite present
- LaTeX report; bib entries carry WhatsApp `note={doi:…}` where DOI known
- `CA2_COMMITMENTS.md` + expanded `baseline_papers/BASELINE_PAPER.md`

## Blockers to 100% (non-AWS)
1. Formal CA2 still missing (proxy commitments only)
2. Synthetic telemetry only (no Borg/IBM traces)
3. Prefer ICDCS VoR PDF over arXiv acceptance claim
4. Soft: diagram placeholders; Lambda packaging never applied (and **must not** be deployed under alignment-only policy)

## AWS
**Not on AWS deploy list.** Residual note: `_analysis_extract/reports/mehak_alignment.md`.
