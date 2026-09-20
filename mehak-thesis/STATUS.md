# Project Status: mehak-thesis

**Last Updated:** 2026-09-20  
**Branch:** `cursor/mehak-ca2-gct-claim-hygiene-5eff`  
**Research Alignment to CA2:** **~64%** (formal `MAHEK NAAZ.docx`; was ~54%)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMIT-READY)

## Summary

Formal CA2 commits to **MHSA-TDL on Google Cluster Trace** vs hybrid/traditional monitors (Acc/Prec/Rec/F1/ROC-AUC/latency). This pass: (1) exact GCT gaps (`DATA_GAPS.md` + fail-closed `gct_loader.py`); (2) formal metric suite + RF/KNN/SVM scaffold on synthetic (5-seed CSV); (3) claim hygiene retiring Thapliyal-as-CA2-baseline. **GCT data still absent** — synthetic ≠ formal evidence. **No live AWS** (not required).

## Evidence-bound results (seeds 42–46) — artefact-as-built (NOT formal GCT)

Source: `mhsa-tdl-framework/results/results_summary.csv` (+ `RESULTS_PROVENANCE.md`). Dataset flag: **synthetic**.

| Model | Acc | Prec | Rec | Macro-F1 | ROC-AUC | Lat (ms) |
|---|---|---|---|---|---|---|
| Threshold Baseline | 0.847 ± 0.002 | 0.301 ± 0.002 | 0.330 ± 0.002 | 0.313 ± 0.002 | — | 0.0001 |
| RF (classical) | 0.953 ± 0.001 | 0.548 ± 0.003 | 0.507 ± 0.003 | 0.523 ± 0.002 | 0.903 ± 0.013 | 0.383 |
| KNN (classical) | 0.930 ± 0.001 | 0.540 ± 0.003 | 0.452 ± 0.001 | 0.478 ± 0.001 | 0.784 ± 0.010 | 0.064 |
| SVM (classical) | 0.944 ± 0.001 | 0.533 ± 0.004 | 0.490 ± 0.002 | 0.506 ± 0.001 | — | 0.045 |
| MHSA-PerHead | 0.873 ± 0.008 | 0.556 ± 0.011 | 0.719 ± 0.026 | 0.564 ± 0.009 | 0.924 ± 0.008 | 0.006 |
| MHSA-Fused | 0.857 ± 0.026 | 0.550 ± 0.009 | 0.720 ± 0.018 | 0.557 ± 0.012 | 0.922 ± 0.011 | 0.006 |

## What is done
- Code + 5-seed train/eval with formal metric columns; classical RF/KNN/SVM scaffold
- `DATA_GAPS.md` + `gct_loader.require_gct()` fail-closed
- LaTeX/STATUS/README claim hygiene to formal RQ (Aldomi family; Thapliyal retired as CA2 baseline)

## Blockers to 100% (vs formal)
1. **Google Cluster Trace files** + usage↔event window join (`DATA_GAPS.md`)
2. GCT-scored Aldomi-style hybrid (scaffold RF/KNN/SVM ≠ full Aldomi)
3. Soft: confusion-matrix FN/FP narrative on GCT splits

## AWS
**Not required.** Residual: `_analysis_extract/reports/mehak_alignment.md`. **Do not deploy.**
