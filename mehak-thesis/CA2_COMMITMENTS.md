# CA2 Commitments — Mehak (formal)

**Source:** Derived from formal CA2 file `mehak-thesis/MAHEK NAAZ.docx` (MHSA-TDL proposal; Gantt/timeline figures present in docx media).  
**Status:** Binding research contract = **formal CA2**, not the prior proxy. Current artefact answers a **Thapliyal cross-head-fusion** niche that is **not** the formal RQ — treat proxy-era claims as non-binding.  
**AWS deploy:** **Not required** for research alignment. Formal resources list *Google Colab, AWS EC2 (GPU)* as **training compute alternatives**. Experiment is offline model eval on traces — **do not deploy** Lambda/SAM under alignment policy.

## Research question (formal)
What is the performance of the proposed MHSA-TDL framework in predicting cloud cluster health and detecting potential failures from cloud telemetry, compared with existing hybrid deep learning and traditional monitoring approaches?

## Objectives (must evidence)
1. Build MHSA-TDL: Multi-Head Self-Attention over multi-metric telemetry (CPU, memory, disk I/O, network, scheduling) for cluster health / early failure detection.
2. Train/evaluate on **Google Cluster Trace** (not proxy synthetic-only).
3. Compare against hybrid/traditional baselines named in CA2 (e.g. Aldomi et al. 2026 GRU+feature-selection hybrid; RF/KNN/SVM/GRU-style monitors).
4. Report Accuracy, Precision, Recall, F1-Score, ROC-AUC, prediction latency (+ confusion-matrix FN/FP analysis).

## Baseline (formal)
Aldomi et al. (2026) and related hybrid/attention failure-prediction literature cited in the proposal — **not** Thapliyal ICDCS as the CA2 baseline.

## Variables / metrics
| Metric | Formal commitment |
|--------|-------------------|
| Accuracy, Precision, Recall, F1, ROC-AUC | Required |
| Prediction latency | Required |
| Dataset | Google Cluster Trace |

## Non-goals / honesty
- Live Kinesis/Lambda inference campaign is **not** the CA2 experiment.
- Prior proxy “synthetic OK + Thapliyal underprediction” contract is **superseded**.
- Synthetic-only telemetry **is** a blocker vs this formal CA2 (GCT required).
