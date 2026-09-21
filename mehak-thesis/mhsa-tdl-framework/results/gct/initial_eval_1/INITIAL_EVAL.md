# Initial evaluation pass (local GCT)

**Date:** 2026-09-21  
**Command:** `python scripts/train_and_evaluate.py --dataset gct --epochs 15 --out-dir results/gct/initial_eval_1`  
**Seeds:** 42–46 (STATUS policy)  
**INITIAL_EVAL_PASS:** **yes**

## Verdict
Formal CA2 metric suite completed on disclosed 2011 GCT subset. Classical RF and Aldomi GRU-RF lead accuracy / Macro-F1; MHSA-Fused does **not** beat them on this subset (negative result retained). High FN on last-seed CMs.

## Artefacts
- `results_summary.csv`, `results_per_seed.csv`
- `confusion_mhsa_fused_last_seed.csv`, `confusion_aldomi_gru_rf_last_seed.csv`
- `gct_load_meta.json`, `RESULTS_PROVENANCE.md`, `gct_train.log`

Final-3 confirmatory local full runs are **not** started here; only after this initial pass stays at 100%.
