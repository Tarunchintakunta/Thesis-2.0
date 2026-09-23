# Baseline paper — Mehak (formal CA2)

**Student folder:** `mehak-thesis`  
**Citation:** Aldomi, Suleiman, Shatnawi & Alawneh (2026) — *A deep learning approach for early prediction of task failures in cloud computing environments.* Systems and Soft Computing 8:200442. doi:10.1016/j.sasc.2026.200442  
**Binding:** formal CA2 baseline family = **Aldomi hybrid** + classical RF/KNN/SVM monitors.  
**Not binding for CA2:** Thapliyal (2026) MHSA SLA paper — related architecture only (`Thapliyal_2026_MHSA_SLA_baseline.pdf` may remain on disk).

## File
- Formal CA2 names Aldomi et al.; PDF VoR preferred when available.
- Proxy-era Thapliyal PDF (if present) is **not** the CA2 baseline.

## Problem → CA2 commitment
Predict cloud task/cluster failures early from multi-metric telemetry; compare hybrid deep learning (feature selection + GRU + ML head) against classical monitors and the proposed MHSA-TDL.

## Solution (paper)
Aldomi et al.: SelectKBest feature selection + GRU temporal extractor + RF/KNN classifiers on Google Cluster Trace.

## Gap (paper’s own / adapted)
Hybrid GRU+selection is competitive; CA2 asks whether **MHSA multi-head fusion** improves Acc/Prec/Rec/F1/ROC-AUC/latency on GCT vs that hybrid family. On the disclosed 2011 subset the answer is **negative** (RF/Aldomi lead).

## Metrics mapped to eval
| Paper / commitment metric | Ours (CSV) |
|---------------------------|------------|
| Accuracy | Accuracy |
| Precision / Recall / F1 | Precision, Recall, Macro-F1, Fail-F1 |
| ROC-AUC | ROC-AUC / Fail-ROC-AUC |
| Latency | Latency (ms) |

Evidence: `mhsa-tdl-framework/results/gct/{final_1,final_2,final_3,hard_verify_1..5}/` — **not** synthetic-only CSVs.
