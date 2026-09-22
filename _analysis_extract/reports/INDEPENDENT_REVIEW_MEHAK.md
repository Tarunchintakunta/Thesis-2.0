# Independent review — Mehak (mhsa-tdl-framework)

**Date:** 2026-09-22  
**STATUS claim:** `CA2 100%` — **conditionally acceptable** only if negative MHSA result + channel honesty stay front-and-centre.  
**Honest CA2 floor:** **met (~88)** with retained scientific negative

## RQ (formal CA2 `MAHEK NAAZ.docx` / `CA2_COMMITMENTS.md`)
> What is the performance of the proposed MHSA-TDL framework in predicting cloud cluster health and detecting potential failures from cloud telemetry, compared with existing hybrid deep learning and traditional monitoring approaches?

Objectives: MHSA-TDL on GCT; compare Aldomi hybrid + classical; Acc/Prec/Rec/F1/ROC-AUC/latency.

## Artefact reality
`mhsa-tdl-framework/` with GCT loader, MHSA models, RF/KNN/SVM, Aldomi SelectKBest+GRU-RF/KNN. AWS not required. `net` channel = sampled CPU (`net_channel_is_network_bytes=false`).

## Evidence (disk)

| Claim | Verdict | Path / numbers |
|-------|---------|----------------|
| Official GCT 2011 subset | **Demonstrated** | `results/gct/gct_load_meta.json`: 4 event + 2 usage parts; n_windows=12000; fail_forced=981 |
| Metric suite 5-seed | **Demonstrated** | `results/gct/initial_eval_1/results_summary.csv` (and final_*): RF Acc **0.9439±0.0022** Fail-F1 **0.515**; Aldomi GRU-RF Acc **0.9425** Fail-F1 **0.524**; MHSA-Fused Acc **0.9223** Fail-F1 **0.412** |
| MHSA improves over baselines | **Not supported** | Last-seed CM MHSA-Fused TN=2144 FP=49 FN=**144** TP=63 |
| Final-3 independence | **Partial** | Acc identical across final_1–3 at reported precision (deterministic re-seed); not three fresh data draws |
| True network-byte channel | **Not met / scoped out** | Documented impossibility on 2011 |

## Floor
**Met** for formal offline GCT RQ **as a negative result**. STATUS 100% is only honest if the report leads with “MHSA does not beat RF/Aldomi.” Calling the thesis a success for MHSA superiority would be **Claimed**.

## Highest-value next steps
1. Temporal holdout / more 2011 parts — test whether negative persists.  
2. Fold FN≫TP into conclusions (already in STATUS — keep).  
3. Do not invent net-bytes; optional 2019 cells only as beyond-CA2.
