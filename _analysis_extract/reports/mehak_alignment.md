# Mehak alignment residual (formal CA2)

**Updated:** 2026-09-20  
**Formal file:** `mehak-thesis/MAHEK NAAZ.docx`  
**Alignment to formal CA2:** **~64/100** (was ~54 after formal rescore; prior ~88 was vs superseded Thapliyal proxy)

## Compact
`RQ6 Obj7 Method6 Impl10 Exp8 Metrics7 Evidence8 Claims8 Rubric4` → **~64/100**

## Formal extract (binding)
| Field | Formal CA2 |
|-------|------------|
| RQ | MHSA-TDL cluster-health / failure prediction vs hybrid DL + traditional monitors |
| Data | **Google Cluster Trace** |
| Metrics | Acc, Prec, Rec, F1, ROC-AUC, prediction latency |
| Baseline | Aldomi-style hybrid / RF·KNN·SVM·GRU — **not** Thapliyal |
| AWS | Colab **or** EC2 GPU for training — **not** required for alignment |
| Gantt | Present (docx media + timeline) |

## Artefact vs formal (this pass)
| Gap | Status |
|-----|--------|
| GCT data + labels | **Still missing** — exact checklist in `mehak-thesis/DATA_GAPS.md`; `gct_loader.py` fail-closed |
| Formal metric suite | **Wired + measured on synthetic** (`results_summary.csv`; Acc/Prec/Rec/F1/ROC-AUC/latency) — **not** GCT |
| Classical RF/KNN/SVM | **Scaffold on synthetic** — not Aldomi hybrid on GCT |
| Claim hygiene | **Done** — formal RQ in abstract/intro/eval/STATUS; Thapliyal retired as CA2 baseline |

MHSA-TDL name/domain + code + 5-seed eval remain. Synthetic scores ≠ formal CA2 evidence.

## True blockers to 100% (vs formal)
1. Google Cluster Trace pipeline + labels (synthetic-only **is** a blocker)
2. Aldomi-style hybrid on **same GCT splits** (scaffold RF/KNN/SVM insufficient)
3. Soft: confusion-matrix FN/FP analysis on GCT

**AWS required:** **no** (do not deploy Lambda/SAM)

## Score delta rationale (~54 → ~64)
+Claims/RQ framing (formal RQ stated; proxy retired); +Metrics harness (formal columns evidence-bound on synthetic); +Evidence (exact DATA_GAPS); Method still capped while GCT absent.
