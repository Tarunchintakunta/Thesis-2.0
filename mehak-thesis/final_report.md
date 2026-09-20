# Final Report: MHSA-TDL (Mehak) — formal CA2 alignment note

## Abstract
Formal CA2 evaluates MHSA-TDL for cluster health / failure prediction on **Google Cluster Trace** with Acc/Prec/Rec/F1/ROC-AUC/latency vs hybrid and traditional monitors. GCT files are **absent** (`DATA_GAPS.md`). This artefact wires the formal metric suite and classical RF/KNN/SVM monitors on **synthetic** telemetry only; those numbers are not formal GCT outcomes. Thapliyal-as-CA2-baseline claims are retired.

## 1. Introduction
See `latex_report/text/introduction.tex`. Binding RQ/objectives = formal CA2 (`CA2_COMMITMENTS.md`).

## 2. Literature
Formal baseline family: Aldomi et al. (2026) and RF/KNN/SVM/GRU-style monitors. Thapliyal (2026) = related MHSA architecture only.

## 3. Methodology
Synthetic generator remains for harness development. GCT loader fails closed until `data/gct/` is populated per `DATA_GAPS.md`. Metrics: formal suite + legacy transient diagnostics.

## 4. Experimental Results
See `mhsa-tdl-framework/results/results_summary.csv` and `RESULTS_PROVENANCE.md`. **Dataset = synthetic** unless `--dataset gct` succeeds.

## 5. Conclusion
Blockers: GCT ingest + window join; GCT-scored Aldomi hybrid; FN/FP analysis on GCT. AWS deploy not required.

## Bibliography
See `latex_report/refs.bib` (`Aldomi26`, `Thapliyal26` note).
