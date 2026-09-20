# Project Status: mehak-thesis

**Last Updated:** 2026-09-20  
**Branch:** `feature/aws-ca2-alignment`  
**Research Alignment to CA2:** **~54%** (formal `MAHEK NAAZ.docx`; prior ~88% was vs superseded Thapliyal proxy)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMIT-READY)

## Summary

Formal CA2 commits to **MHSA-TDL on Google Cluster Trace** vs hybrid/traditional monitors (Acc/Prec/Rec/F1/ROC-AUC/latency). Current artefact still implements **Thapliyal cross-head fusion on synthetic telemetry**. Gantt present in formal docx. **No live AWS** (EC2 listed only as optional training compute beside Colab).

## Evidence-bound results (seeds 42–46) — artefact as-built (not formal GCT)

Source: `mhsa-tdl-framework/results/results_summary.csv` (+ `results_per_seed.csv`).

| Model | Accuracy | Macro-F1 | Transient Recall | Underprediction Bias |
|---|---|---|---|---|
| Threshold Baseline | 0.847 ± 0.002 | 0.313 ± 0.002 | 0.025 ± 0.002 | 1.715 ± 0.011 |
| MHSA-PerHead (baseline) | 0.873 ± 0.011 | 0.565 ± 0.008 | 0.864 ± 0.022 | 0.290 ± 0.076 |
| MHSA-Fused (improved) | 0.863 ± 0.014 | 0.560 ± 0.010 | 0.884 ± 0.021 | 0.273 ± 0.050 |

These numbers answer the **proxy** experiment, not formal GCT/Aldomi evaluation.

## What is done
- Code + 5-seed train/eval; pytest; LaTeX; `CA2_COMMITMENTS.md` rewritten from formal docx

## Blockers to 100% (vs formal)
1. Google Cluster Trace data + eval (synthetic-only is a blocker)
2. Formal metrics/baselines (Prec/Rec/ROC-AUC; hybrid comparison)
3. Soft: report/claims rewrite off Thapliyal-as-CA2

## AWS
**Not required.** Residual: `_analysis_extract/reports/mehak_alignment.md`. **Do not deploy.**
