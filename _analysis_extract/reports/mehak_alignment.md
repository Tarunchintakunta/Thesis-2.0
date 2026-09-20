# Mehak alignment residual (formal CA2)

**Updated:** 2026-09-20  
**Formal file:** `mehak-thesis/MAHEK NAAZ.docx`  
**Alignment to formal CA2:** **~54/100** (was ~88 vs superseded Thapliyal proxy)

## Compact
`RQ5 Obj6 Method5 Impl10 Exp8 Metrics5 Evidence7 Claims4 Rubric4` → **~54/100**

## Formal extract (binding)
| Field | Formal CA2 |
|-------|------------|
| RQ | MHSA-TDL cluster-health / failure prediction vs hybrid DL + traditional monitors |
| Data | **Google Cluster Trace** |
| Metrics | Acc, Prec, Rec, F1, ROC-AUC, prediction latency |
| Baseline | Aldomi-style hybrid / RF·KNN·SVM·GRU — **not** Thapliyal |
| AWS | Colab **or** EC2 GPU for training — **not** required for alignment |
| Gantt | Present (docx media + timeline) |

## Artefact vs formal
MHSA-TDL **name/domain** match; code+5-seed eval exist. Artefact RQ is Thapliyal cross-head fusion on **synthetic** telemetry with underprediction metrics — **not** formal GCT + Aldomi comparison + ROC-AUC suite.

## True blockers to 100% (vs formal)
1. Google Cluster Trace pipeline + labels (synthetic-only **is** a blocker here)
2. Baselines/metrics per formal (Prec/Rec/ROC-AUC; Aldomi/hybrid comparison) — retire Thapliyal-as-CA2-baseline claims
3. Soft: claims/STATUS/report rewrite to formal RQ

**AWS required:** **no** (do not deploy Lambda/SAM)
