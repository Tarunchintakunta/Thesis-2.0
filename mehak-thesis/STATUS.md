# Project Status: mehak-thesis

**Last Updated:** 2026-09-20  
**Branch:** `cursor/mehak-gct-formal-raise-9dc9`  
**Research Alignment to CA2:** **~82%** (formal `MAHEK NAAZ.docx`; was ~64%)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMIT-READY)

## Summary

Formal CA2 commits to **MHSA-TDL on Google Cluster Trace** vs hybrid/traditional monitors (Acc/Prec/Rec/F1/ROC-AUC/latency). This pass closed the hard data residual: **2011 GCT MV subset downloaded**, `gct_loader` joins usage↔events, and `--dataset gct` produced 5-seed formal metrics (plus Fail-* binary and Aldomi-style GRU scaffold) under `mhsa-tdl-framework/results/gct/`. **No live AWS** (not required).

## Evidence-bound results (seeds 42–46) — Google Cluster Trace

Source: `mhsa-tdl-framework/results/gct/results_summary.csv` (+ `RESULTS_PROVENANCE.md`). Dataset flag: **gct**.  
Subset: `task_usage` part-00000 + `task_events` parts 00000–00001 + `machine_events` (see `data/gct/PROVENANCE.md`). N≈7999 windows.

| Model | Acc | Fail-F1 | Fail-ROC-AUC | Lat (ms) |
|---|---|---|---|---|
| Threshold Baseline | 0.960 ± 0.002 | 0.718 ± 0.010 | — | 0.0001 |
| RF (classical) | 0.973 ± 0.001 | 0.784 ± 0.013 | 0.956 ± 0.003 | 0.239 |
| KNN (classical) | 0.971 ± 0.002 | 0.766 ± 0.016 | 0.944 ± 0.004 | 0.035 |
| SVM (classical) | 0.973 ± 0.002 | 0.785 ± 0.019 | 0.953 ± 0.004 | 0.162 |
| MHSA-PerHead | 0.927 ± 0.008 | 0.695 ± 0.028 | 0.948 ± 0.006 | 0.005 |
| MHSA-Fused | 0.936 ± 0.009 | 0.716 ± 0.027 | 0.951 ± 0.006 | 0.005 |
| Aldomi-style GRU+FS (scaffold) | 0.942 ± 0.014 | 0.732 ± 0.054 | 0.943 ± 0.003 | 0.002 |

## What is done
- GCT 2011 MV files + provenance; fail-closed loader + usage↔event window join
- 5-seed GCT train/eval with formal + Fail-* metrics; classical RF/KNN/SVM; Aldomi-family scaffold
- Synthetic CSVs retained separately; GCT results under `results/gct/`

## Blockers to 100% (vs formal)
1. Broader GCT coverage (more `task_usage`/`task_events` parts; 2011 has no explicit network-byte channel — 4th channel = sampled CPU)
2. Aldomi scaffold ≠ paper-faithful hybrid reproduction
3. Soft: richer FN/FP narrative + optional multi-day temporal holdout

## AWS
**Not required.** Residual: `_analysis_extract/reports/mehak_alignment.md`. **Do not deploy.**
