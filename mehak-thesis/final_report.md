# Final Report: MHSA-TDL (Mehak) — formal CA2 alignment note

## Abstract
Formal CA2 evaluates MHSA-TDL for cluster health / failure prediction on **Google Cluster Trace** with Acc/Prec/Rec/F1/ROC-AUC/latency vs hybrid and traditional monitors. A 2011 subset is scored (`results/gct/initial_eval_1/`; 4 event + 2 usage parts; `net` = sampled CPU, not network bytes). Classical RF Acc 0.944; Aldomi GRU-RF Acc 0.943 / Macro-F1 0.676; MHSA-Fused Acc 0.922 — MHSA is not claimed to win. Full dump / 2019 cells remain absent. See `STATUS.md` and `DESIGN_RATIONALE_BEYOND_CA2.md`. **INITIAL_EVAL_PASS=yes**.

## 1. Introduction
See `latex_report/text/introduction.tex`. Binding RQ/objectives = formal CA2 (`CA2_COMMITMENTS.md`).

## 2. Literature
Formal baseline family: Aldomi et al. (2026) and RF/KNN/SVM/GRU-style monitors. Thapliyal (2026) = related MHSA architecture only.

## 3. Methodology
GCT loader joins usage↔events. Synthetic generator remains for harness development. Metrics: formal suite + legacy transient diagnostics. Channel honesty: `mhsa-tdl-framework/data/gct/CHANNEL_HONESTY.md`.

## 4. Experimental Results
See `mhsa-tdl-framework/results/gct/results_summary.csv` (`dataset=gct`). Synthetic CSVs under `results/` are not GCT evidence.

## 5. Conclusion
Residuals: remaining 2011 parts / 2019 Borg cells; true network-byte channel (impossible on 2011 without invention). AWS deploy not required. **NOT COMPLETE** (~90%).

## Bibliography
See `latex_report/refs.bib` (`Aldomi26`, `Thapliyal26` note).
