# Design rationale — beyond CA2 (Mehak)

**Policy:** CA2 is a floor (`_analysis_extract/reports/CA2_FLOOR_NOT_CEILING.md`).  
**AWS:** not required. No deploy this pass.

## CA2 floor (met with evidence)

| Commitment | Evidence |
|------------|----------|
| MHSA-TDL on Google Cluster Trace | 2011 parts: 4× `task_events` + 2× `task_usage` + `machine_events`; join in `gct_loader.py`; `--dataset gct` 5-seed CSVs |
| Metrics Acc/Prec/Rec/F1/ROC-AUC/latency | `results/gct/results_summary.csv` |
| Hybrid + traditional monitors | RF/KNN/SVM **and** Aldomi SelectKBest+GRU+RF/KNN on the same splits |
| FN/FP | `confusion_mhsa_fused_last_seed.csv`, `confusion_aldomi_gru_rf_last_seed.csv` |

## Honesty (not invented)

- **Network channel:** ClusterData **2011 has no network-byte field**. MHSA `net` = sampled CPU (`CHANNEL_HONESTY.md`; `net_channel_is_network_bytes=false`). 2019 Borg cells (paper generation for Aldomi) are absent.
- **Aldomi:** SelectKBest on 13 expanded usage+history-scheduling channels, GRU extractor, RF/KNN heads. **Not** a hyperparameter clone of Aldomi et al. 2026 (they used 2019 traces, k-search to 14). SelectKBest kept k=12/13 on this run.
- **FAIL windows:** extra parts + fail-series-first sampling → 981 fail-forced / 12000 windows (was 489 on the MV subset).
- **Who wins:** classical RF Acc **0.944 ± 0.002**; Aldomi GRU-RF Acc **0.943 ± 0.001**, Macro-F1 **0.676**; MHSA-Fused Acc **0.922**, Macro-F1 **0.613**. MHSA is **not** claimed to beat the hybrid/traditional monitors on this subset.

## Beyond-CA2 this pass

- Second `task_usage` part + two extra `task_events` parts (coverage, not the 41 GB dump)
- Expanded Aldomi feature tensor + history-only SCHEDULE/UPDATE counts
- Last-seed confusion matrices for MHSA-Fused **and** Aldomi GRU-RF

## Residual (NOT COMPLETE)

Full 29-day 2011 dump; 2019 cells; a true network-byte channel (requires 2019 or a documented schema change). Do not fabricate bandwidth.

**Alignment ~90%.** Formal RQ is answered on a disclosed 2011 subset with an honest net-channel proxy.
