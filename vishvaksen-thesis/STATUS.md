# Project Status: vishvaksen-thesis

**Last Updated:** 2026-09-20  
**Branch:** `feature/aws-ca2-alignment`  
**Research Alignment to CA2:** **~86%** (proxy via `CA2_COMMITMENTS.md`; formal CA2 **NOT FOUND**)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMIT-READY)

## Summary

Local synthetic IaC ablation reproduces War et al. (2025) comment-removal precision collapse with TF-IDF ML, and evaluates hybrid rule+ML. **Not** a CodeBERT/LongFormer replication. **No live AWS.** Baseline is arXiv-only (venue risk).

## Evidence-bound results (seeds 42–46)

Source: `iac-security/results/results_summary.csv` (+ `results_per_seed.csv`).

| Model | Precision | Recall | F1 |
|--------|----------:|-------:|---:|
| ML (rich context) | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| ML (code-only, baseline gap) | 0.768 ± 0.045 | 0.708 ± 0.064 | 0.733 ± 0.019 |
| Rule-Based Only | 1.000 ± 0.000 | 0.483 ± 0.028 | 0.651 ± 0.025 |
| Hybrid (code-only) | 1.000 ± 0.000 | 0.483 ± 0.028 | 0.651 ± 0.025 |

Hybrid restores precision to 1.000 at default threshold 0.8; recall equals rule floor (~0.483).

## What is done
- Dataset + detectors + 5-seed driver; pytest; Makefile
- LaTeX sources expanded (recompile PDF locally if stale)
- Bib `note={doi:…}` (War via arXiv DOI); `CA2_COMMITMENTS.md` + expanded baseline MD

## Blockers to 100% (non-AWS)
1. Formal CA2 missing
2. arXiv-only baseline venue risk (keep Rahman/GLITCH anchors)
3. Method gap: TF-IDF hybrid ≠ War CodeBERT/LongFormer
4. Synthetic easy/hard mix; no real Forge corpora; PDF may need rebuild; Lambda never deployed (**do not deploy**)

## AWS
**Not on AWS deploy list.** Residual: `_analysis_extract/reports/vishvaksen_alignment.md`.
