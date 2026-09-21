# Project Status: mehak-thesis

**Last Updated:** 2026-09-21  
**Branch:** `main`  
**Research Alignment to CA2:** **100%** (formal `MAHEK NAAZ.docx`; research-scope floor — not perfect marks)  
**Status:** **CA2 floor COMPLETE** — soft residuals (full 2011 dump / 2019 cells / true net-bytes) are **explicitly scoped out** with rationale in `DESIGN_RATIONALE_BEYOND_CA2.md`  
**INITIAL_EVAL_PASS:** **yes** (one local GCT full run; path below)

## Summary

Formal CA2: **MHSA-TDL on Google Cluster Trace** vs hybrid/traditional monitors (Acc/Prec/Rec/F1/ROC-AUC/latency). Delivered: official **2011** expanded subset (**4** event parts + **2** usage parts); fail-series-first windows (**981** FAIL-forced / 12000); `--dataset gct` 5-seed metrics including RF/KNN/SVM and **Aldomi SelectKBest+GRU-RF/KNN**. MHSA 4th channel = **sampled CPU** (2011 has **no** network bytes — documented, not invented). Synthetic CSVs are not GCT evidence. **No live AWS** (not required).

## Initial eval (2026-09-21)

- **Path:** `mhsa-tdl-framework/results/gct/initial_eval_1/`
- **Cmd:** `python scripts/train_and_evaluate.py --dataset gct --epochs 15 --out-dir results/gct/initial_eval_1`
- **Seeds:** 42–46; epochs=15; max_windows=12000
- **CA2 re-check vs `MAHEK NAAZ.docx`:** still **100%** (RQ/objectives/GCT/baselines/metric suite). Doc fix this pass: methodology/implementation no longer claim GCT absent.
- **Rubric70 honesty:** MHSA does **not** beat RF/Aldomi; FN≫TP retained in eval/conclusion.
- **Next (not this task):** only after pass stays 100% — three reproducible **local** full GCT runs (final-3); no AWS.

## Evidence-bound results (seeds 42–46) — Google Cluster Trace

Source: `mhsa-tdl-framework/results/gct/initial_eval_1/results_summary.csv` (matches prior `results/gct/` summary). Dataset flag: **gct**.  
N=12000 windows; **981** event-forced; Xe=(12000,10,13). Epochs=15. `net_channel_is_network_bytes=false`.

| Model | Acc | Prec | Rec | Macro-F1 | ROC-AUC | Fail-F1 | Lat (ms) |
|---|---|---|---|---|---|---|---|
| Threshold Baseline | 0.921 ± 0.001 | 0.495 ± 0.003 | 0.475 ± 0.001 | 0.467 ± 0.002 | — | 0.336 ± 0.022 | 0.0001 |
| RF (classical) | 0.944 ± 0.002 | 0.881 ± 0.009 | 0.609 ± 0.011 | 0.670 ± 0.013 | 0.812 ± 0.052 | 0.515 ± 0.031 | 0.269 |
| KNN (classical) | 0.932 ± 0.003 | 0.824 ± 0.024 | 0.551 ± 0.012 | 0.594 ± 0.017 | 0.701 ± 0.071 | 0.359 ± 0.033 | 0.044 |
| SVM (classical) | 0.923 ± 0.001 | 0.718 ± 0.031 | 0.505 ± 0.007 | 0.522 ± 0.012 | — | 0.339 ± 0.008 | 0.102 |
| MHSA-PerHead | 0.921 ± 0.002 | 0.678 ± 0.011 | 0.584 ± 0.005 | 0.615 ± 0.006 | 0.571 ± 0.110 | 0.409 ± 0.018 | 0.006 |
| MHSA-Fused | 0.922 ± 0.002 | 0.684 ± 0.008 | 0.581 ± 0.006 | 0.613 ± 0.006 | 0.617 ± 0.105 | 0.412 ± 0.016 | 0.005 |
| Aldomi GRU-RF | 0.943 ± 0.001 | 0.833 ± 0.009 | 0.620 ± 0.006 | 0.676 ± 0.005 | 0.753 ± 0.128 | 0.524 ± 0.010 | 0.287 |
| Aldomi GRU-KNN | 0.940 ± 0.001 | 0.828 ± 0.015 | 0.607 ± 0.009 | 0.662 ± 0.009 | 0.724 ± 0.072 | 0.496 ± 0.022 | 0.046 |

Last-seed binary CM (`n_test=2400`):  
MHSA-Fused TN=2144 FP=49 FN=144 TP=63.  
Aldomi GRU-RF TN=2185 FP=8 FN=133 TP=74.  
RF/Aldomi lead accuracy; MHSA is **not** claimed to win this subset (negative result retained).

## What is done
- Official GCT 2011 expanded subset + SHA-256 provenance; fail-closed loader; usage↔event windows; fail-series-first
- 5-seed GCT train/eval with formal metrics; classical monitors; Aldomi SelectKBest+GRU+RF/KNN
- Channel honesty; DESIGN_RATIONALE maps floor vs scoped-out optionals
- Synthetic CSVs retained separately under `results/`
- **Initial local eval** under `results/gct/initial_eval_1/` → `INITIAL_EVAL_PASS=yes`

## Soft residuals (optional beyond-CA2 — not floor blockers)
1. Remaining 2011 parts / 2019 Borg cells (coverage / Aldomi generation clone)
2. True network-byte channel (impossible on 2011 without invention)
3. Multi-day temporal holdout; line-by-line Aldomi 2019 hyperparams

## AWS
**Not required.** Alignment: `_analysis_extract/reports/mehak_alignment.md`. **Do not deploy.**
