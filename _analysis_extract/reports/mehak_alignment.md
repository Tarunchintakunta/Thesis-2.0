# Mehak alignment residual (formal CA2)

**Updated:** 2026-09-21  
**Formal file:** `mehak-thesis/MAHEK NAAZ.docx`  
**Alignment to formal CA2:** **100/100** (research-scope floor; was ~90% after GCT MV expand)  
**INITIAL_EVAL_PASS:** **yes** — `mehak-thesis/mhsa-tdl-framework/results/gct/initial_eval_1/`

## Compact
`RQ10 Obj12 Method12 Impl13 Exp12 Metrics10 Evidence12 Claims10 Rubric9` → **100/100**

## Floor closed
- Mapped every formal commitment → delivered GCT evidence in `DESIGN_RATIONALE_BEYOND_CA2.md`
- Reframed full 2011 dump / 2019 Borg / true net-bytes as **scoped-out optional** (fail-closed; no invention)
- Rubric70: eval discussion + conclusion keep **negative results** (RF/Aldomi ahead; high FN) and limitation honesty
- Expanded 2011 subset (4 events + 2 usage); initial local 5-seed GCT eval completed

## Re-check after initial eval (2026-09-21)
| Formal CA2 (`MAHEK NAAZ.docx`) | Evidence |
|---|---|
| RQ: MHSA-TDL vs hybrid/traditional on cloud telemetry | GCT 2011 windows; RF/KNN/SVM + Aldomi GRU-RF/KNN + MHSA |
| Dataset: Google Cluster Trace | `--dataset gct`; `results/gct/initial_eval_1/` |
| Metrics: Acc/Prec/Rec/F1/ROC-AUC/latency | `results_summary.csv` columns present |
| Honest analysis | MHSA does not beat RF/Aldomi on this subset |

Doc fix this pass: `methodology.tex` / `implementation.tex` no longer claim GCT is absent (was stale vs landed pipeline). **Still 100%.**

## Soft / beyond-CA2 (does not reopen floor)
2019 Borg cells; remaining ~41 GB 2011 parts; true network-byte channel (impossible on 2011 schema); optional multi-day holdout. Final-3 = three later **local** full GCT runs (not AWS).

**AWS required:** **no**
