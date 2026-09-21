# Design rationale — CA2 floor + scoped residuals (Mehak)

**Policy:** CA2 is a floor (`_analysis_extract/reports/CA2_FLOOR_NOT_CEILING.md`).  
**Bar:** 100% CA2 = RQ / objectives / gap / method / artefact / eval **scope** — not perfect marks.  
**AWS:** not required. No deploy.

## Formal CA2 → delivered (floor met)

| Commitment | Delivered evidence | Scope note |
|------------|-------------------|------------|
| RQ: MHSA-TDL vs hybrid/traditional on cloud telemetry | 5-seed GCT run; RF/Aldomi lead Acc; MHSA **not** claimed to win | Negative result retained (honest) |
| Obj: multi-metric MHSA (CPU, mem, disk, network, scheduling) | 4-channel MHSA + history SCHEDULE/UPDATE features for Aldomi path | Network = sampled CPU on 2011 (`CHANNEL_HONESTY.md`) |
| Dataset: Google Cluster Trace | Official 2011 parts under `data/gct/2011/` (4× events, 2× usage, machine_events); fail-closed loader | Formal CA2 does **not** pin generation or full dump |
| Baselines: hybrid + traditional | RF/KNN/SVM + Aldomi SelectKBest+GRU+RF/KNN on same splits | Paper **family**, not 2019 hyperparam clone |
| Metrics: Acc/Prec/Rec/F1/ROC-AUC/latency + FN/FP | `results/gct/results_summary.csv` + last-seed CMs | Bound numbers only |

## Explicitly scoped out (fail-closed; still CA2-complete)

These are **optional beyond-CA2 enhancements**, not open formal-scope holes:

1. **Full ~41 GB 2011 dump** — not required once a disclosed, joinable usage↔event subset supports the formal metric suite. Expanded subset already yields N=12000 windows with 981 FAIL-forced. Remaining parts would raise coverage, not change the RQ.
2. **2019 Borg cells** — Aldomi et al. used this generation; formal CA2 names *Google Cluster Trace*, not “2019 eight-cell.” Reproducing their exact preprocessing is beyond floor.
3. **True network-byte channel** — **impossible on ClusterData 2011** without inventing a series. Honest proxy (sampled CPU) + `net_channel_is_network_bytes=false` satisfies the multi-metric artefact without fabrication. A true byte channel needs 2019 (out of scope above).
4. **Multi-day temporal holdout / line-by-line Aldomi k-search** — soft validity upgrades; random 5-seed splits already answer the comparison RQ.

**Rationale:** inventing bandwidth or silently swapping synthetic labels would break evidence rules. Disclosing schema limits and retaining RF/Aldomi-ahead results meets research-scope alignment better than chasing optional dumps.

## Beyond-CA2 already present

- Extra usage/events parts beyond MV (fail-series-first → 981 fail-forced)
- Expanded Aldomi feature tensor (13 columns, SelectKBest)
- Dual last-seed confusion matrices (MHSA-Fused + Aldomi GRU-RF)

## Alignment

**Formal CA2 research-scope: 100%.** Soft residuals above remain optional; they do **not** reopen the floor.
