# Project Status: mehak-thesis

**Last Updated:** 2026-09-20  
**Branch:** `cursor/mehak-gct-formal-raise-9dc9`  
**Research Alignment to CA2:** **~84%** (formal `MAHEK NAAZ.docx`; was ~64%)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMIT-READY)

## Summary

Formal CA2 commits to **MHSA-TDL on Google Cluster Trace** vs hybrid/traditional monitors (Acc/Prec/Rec/F1/ROC-AUC/latency). This pass: official **2011 GCT MV subset** under `data/gct/2011/`; `gct_loader` joins `task_usage`↔`task_events` (FAIL/EVICT/KILL/LOST in a 5-step horizon forces L2); `--dataset gct` 5-seed metrics including classical RF/KNN/SVM and an Aldomi-style GRU+FS **scaffold** in `results/gct/` (`dataset=gct`). Synthetic CSVs are not GCT evidence. **No live AWS** (not required).

## Evidence-bound results (seeds 42–46) — Google Cluster Trace

Source: `mhsa-tdl-framework/results/gct/results_summary.csv` (+ `results/gct/RESULTS_PROVENANCE.md`). Dataset flag: **gct**.  
Subset: `task_usage` part-00000 + `task_events` parts 00000–00001 + `machine_events` (`data/gct/PROVENANCE.md`). **N=12000** windows; **489** event-forced (FAIL-family in horizon). 4th channel = sampled CPU (2011 schema has no network bytes).

| Model | Acc | Prec | Rec | Macro-F1 | ROC-AUC | Fail-F1 | Lat (ms) |
|---|---|---|---|---|---|---|---|
| Threshold Baseline | 0.924 ± 0.003 | 0.484 ± 0.003 | 0.496 ± 0.002 | 0.490 ± 0.002 | — | 0.575 ± 0.012 | 0.0001 |
| RF (classical) | 0.951 ± 0.003 | 0.883 ± 0.020 | 0.615 ± 0.014 | 0.672 ± 0.018 | 0.915 ± 0.007 | 0.725 ± 0.010 | 0.278 |
| KNN (classical) | 0.944 ± 0.003 | 0.863 ± 0.033 | 0.567 ± 0.014 | 0.607 ± 0.021 | 0.854 ± 0.012 | 0.680 ± 0.011 | 0.051 |
| SVM (classical) | 0.938 ± 0.003 | 0.598 ± 0.164 | 0.507 ± 0.002 | 0.504 ± 0.005 | — | 0.674 ± 0.012 | 0.140 |
| MHSA-PerHead | 0.698 ± 0.043 | 0.573 ± 0.009 | 0.771 ± 0.016 | 0.509 ± 0.022 | 0.858 ± 0.015 | 0.464 ± 0.029 | 0.006 |
| MHSA-Fused | 0.694 ± 0.027 | 0.569 ± 0.007 | 0.769 ± 0.011 | 0.504 ± 0.020 | 0.862 ± 0.009 | 0.464 ± 0.013 | 0.006 |
| Aldomi-style GRU+FS (scaffold) | 0.715 ± 0.037 | 0.556 ± 0.008 | 0.762 ± 0.011 | 0.517 ± 0.020 | 0.853 ± 0.007 | 0.477 ± 0.022 | 0.003 |

Last-seed MHSA-Fused binary CM (`results/gct/confusion_mhsa_fused_last_seed.csv`): TN=672, FP=1213, FN=13, TP=502 (high fail-recall, many false positives).

## What is done
- Official GCT 2011 MV files + SHA-256 provenance; fail-closed loader; usage↔event windows
- 5-seed GCT train/eval with Acc/Prec/Rec/F1/ROC-AUC/latency + Fail-* ; RF/KNN/SVM; Aldomi-family scaffold
- Synthetic CSVs retained separately under `results/`

## Blockers to 100% (vs formal)
1. Broader GCT coverage (remaining `task_usage`/`task_events` parts; no 2011 network-byte channel)
2. Aldomi scaffold ≠ paper-faithful hybrid reproduction
3. Soft: richer FN/FP write-up + optional multi-day temporal holdout (CM CSV exists)

## AWS
**Not required.** Residual: `_analysis_extract/reports/mehak_alignment.md`. **Do not deploy.**
