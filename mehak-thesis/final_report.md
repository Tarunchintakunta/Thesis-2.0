# Final Report: MHSA-TDL (Mehak) — formal CA2 alignment note

## Abstract
Formal CA2 evaluates MHSA-TDL for cluster health / failure prediction on **Google Cluster Trace** with Acc/Prec/Rec/F1/ROC-AUC/latency vs hybrid and traditional monitors. A 2011 subset is scored (`results/gct/initial_eval_1/` + final-3 pack; 4 event + 2 usage parts; `net` = sampled CPU, not network bytes). Classical RF Acc 0.944; Aldomi GRU-RF Acc 0.943 / Macro-F1 0.676; MHSA-Fused Acc 0.922 — MHSA is not claimed to win. Full dump / 2019 cells remain scoped beyond-CA2. See `STATUS.md`, `DESIGN_RATIONALE_BEYOND_CA2.md`, `mhsa-tdl-framework/results/gct/FINAL3_BASELINE.md`. **INITIAL_EVAL_PASS=yes.** **Final-3 local GCT = done (3/3).**

## 1. Introduction
See `latex_report/text/introduction.tex`. Binding RQ/objectives = formal CA2 (`CA2_COMMITMENTS.md`).

## 2. Literature
Formal baseline family: Aldomi et al. (2026) and RF/KNN/SVM/GRU-style monitors. Thapliyal (2026) = related MHSA architecture only.

## 3. Methodology
GCT loader joins usage↔events. Synthetic generator remains for harness development. Metrics: formal suite + legacy transient diagnostics. Channel honesty: `mhsa-tdl-framework/data/gct/CHANNEL_HONESTY.md`.

## 4. Experimental Results
Authoritative GCT summaries: `mhsa-tdl-framework/results/gct/{initial_eval_1,final_1,final_2,final_3}/results_summary.csv`. Three final packs are stable (RF/Aldomi lead; MHSA-Fused Acc 0.922). Synthetic CSVs under `results/` are not GCT evidence. Baseline compare: `results/gct/FINAL3_BASELINE.md`.

## 5. Conclusion
**CA2 research-scope floor: 100%.** Soft residuals (remaining 2011 parts / 2019 Borg cells; true network-byte channel) are beyond-CA2 — not blockers. AWS deploy not required. **Negative result retained:** MHSA does not beat RF/Aldomi on this subset.

## Bibliography
See `latex_report/refs.bib` (`Aldomi26`, `Thapliyal26` note).
