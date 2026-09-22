# GENAI_HANDOFF.md — Mehak (MHSA-TDL)

## 0. Document meta

| Field | Value |
|-------|-------|
| Student | Mehak (Mahek Naaz) |
| Artefact root | `mehak-thesis/mhsa-tdl-framework/` |
| Programme | MSc Cloud Computing Research Project |
| Honest CA2 floor | **met (~88)** — independent review 2026-09-22; STATUS “100%” only valid if negative MHSA result stays front-and-centre |
| Eval completeness | **3 full-scale local GCT finals done** (`results/gct/final_1\|2\|3/`) + `initial_eval_1/` |
| AWS | **N/A — not required** for CA2 experiment |
| Handoff date | 2026-09-22 |
| Authority | `CA2_COMMITMENTS.md`, `_analysis_extract/reports/INDEPENDENT_REVIEW_MEHAK.md`, on-disk `results/gct/` |

## 1. Research problem, motivation, research question, and objectives

**Problem:** Predict cloud cluster health / early failures from multi-metric telemetry.

**RQ (formal CA2):** What is the performance of the proposed MHSA-TDL framework in predicting cloud cluster health and detecting potential failures from cloud telemetry, compared with existing hybrid deep learning and traditional monitoring approaches?

**Objectives (must evidence):**
1. Build MHSA-TDL (multi-head self-attention over multi-metric telemetry).
2. Train/evaluate on Google Cluster Trace (GCT), not synthetic-only.
3. Compare vs Aldomi hybrid + classical monitors (RF/KNN/SVM).
4. Report Accuracy, Precision, Recall, F1, ROC-AUC, prediction latency (+ CM FN/FP).

## 2. Identified literature gap and how this research addresses it

Gap addressed: apply MHSA fusion over GCT multi-metric windows vs hybrid GRU+feature-selection (Aldomi-style) and classical monitors. Full lit depth is in formal CA2 `MAHEK NAAZ.docx`.

## 3. CA2 proposal alignment and any extensions beyond the proposal

- **Aligned:** GCT 2011 subset, MHSA models, Aldomi GRU-RF/KNN, classical RF/KNN/SVM, full metric suite, latency.
- **Honesty scope:** `net` channel is **sampled CPU**, not network bytes. True net-bytes / full dump / 2019 are beyond-CA2 optional.
- **Prior proxy** (Thapliyal / synthetic-only) **superseded** by formal CA2.

## 4. Research methodology and experimental design

- Offline supervised failure prediction on sliding windows from GCT task events + usage.
- Seeds 42–46 (5 seeds) per final pack; `--dataset gct --epochs 15`.
- Models: MHSA-Fused, MHSA-PerHead, Aldomi GRU-RF/KNN, RF/KNN/SVM, threshold baseline.

## 5. Artefact purpose and artefact-only project structure

**Purpose:** Implement and evaluate MHSA-TDL vs baselines on GCT.

```
mhsa-tdl-framework/
  src/data/          # gct_loader.py (fail-closed)
  src/models/        # MHSA + Aldomi + classical
  src/lambda_handler/# optional; not the CA2 live experiment
  scripts/           # train_and_evaluate runners
  data/gct/          # disclosed 2011 parts used in finals
  results/gct/       # initial_eval_1 + final_1..3
  tests/
```

## 6. AWS architecture, services, configurations, and experimental setup

**N/A — AWS not required / not applied** for the CA2 evaluation. Do not deploy Lambda/SAM under alignment policy for this thesis.

## 7. Evaluation metrics and why they were selected

Accuracy/Prec/Rec/F1/ROC-AUC + Fail-F1 for imbalance; latency for operational cost; confusion matrices for FN/TP honesty.

## 8. Baseline definition and baseline comparison

| Role | Model |
|------|--------|
| Classical baseline | RF (primary), also KNN/SVM |
| Hybrid baseline (CA2) | Aldomi GRU-RF / GRU-KNN |
| Proposed | MHSA-Fused (primary), MHSA-PerHead |

Improvement is **not** assumed.

## 9. Complete evaluation process and number of runs

| Pack | Path | Scale | Destroy |
|------|------|-------|---------|
| initial_eval_1 | `results/gct/initial_eval_1/` | GCT, 5 seeds, epochs=15 | N/A local |
| final_1 | `results/gct/final_1/` | same | N/A |
| final_2 | `results/gct/final_2/` | same | N/A |
| final_3 | `results/gct/final_3/` | same | N/A |

**Independence note:** Acc identical across final_1–3 at reported precision (deterministic re-seed) — pipeline repeatability, not three fresh data draws (independent review: Partial).

## 10. Final results and key findings (committed evidence)

From `results/gct/final_1/results_summary.csv` (final_2/final_3 match — `FINAL3_BASELINE.md`):

| Model | Acc mean±std | Fail-F1 mean±std | Latency ms mean |
|-------|-------------:|-----------------:|----------------:|
| RF (classical) | **0.9439±0.0022** | 0.5154±0.0312 | 0.2624 |
| Aldomi GRU-RF | 0.9425±0.0006 | **0.5244±0.0095** | 0.2713 |
| MHSA-Fused | 0.9223±0.0016 | 0.4116±0.0161 | **0.0051** |
| MHSA-PerHead | 0.9211±0.0022 | 0.4087±0.0184 | 0.0058 |

GCT load (`final_1/gct_load_meta.json`): family=2011; n_windows=12000; fail_forced_windows=981; 4 event + 2 usage parts.

**Last-seed CM (MHSA-Fused):** high FN vs TP (independent review: TN=2144 FP=49 FN=144 TP=63).

## 11. How results satisfy or address each research objective

1. **Build MHSA-TDL:** Demonstrated.
2. **GCT eval:** Demonstrated — 2011 subset.
3. **Compare hybrid/classical:** Demonstrated — table §10.
4. **Metric suite + latency + CM:** Demonstrated.

## 12. How results answer the research question

On this disclosed 2011 GCT subset, **MHSA-TDL does not outperform** classical RF or Aldomi GRU-RF on Accuracy / Macro-F1 / Fail-F1. Honest answer = **negative comparative result**.

## 13. How findings relate to the literature gap and previous research

Addresses CA2 comparison to Aldomi-style hybrids: hybrid GRU-RF remains competitive; attention fusion is **not** superior here.

## 14. Statistical analysis and significance

Per-seed means/std across seeds 42–46. No supported claim that MHSA significantly beats RF/Aldomi.

## 15. Important observations, trends, positive/negative findings, and anomalies

- **Positive:** Reproducible pipeline; classical/hybrid strong Acc; MHSA low latency.
- **Negative (retain):** MHSA Acc/Fail-F1 below RF and Aldomi; FN≫TP.
- **Scope:** final_1≡final_2≡final_3; `net` ≠ network bytes.

## 16. Limitations, validity, reproducibility, and generalisability

Disclosed 2011 subset (not full dump/2019); forced-fail windows; deterministic final-3; channel honesty; local-only.

## 17. Final conclusions and research contribution

Honest negative: MHSA-TDL on this GCT subset does **not** improve failure detection vs RF/Aldomi. Latency alone does not answer the RQ.

## 18. What changed or improved during the evaluation process

Formal CA2 superseded proxy framing; GCT loader fail-closed; negative retained through final-3; independent floor ~88.

## 19. Remaining issues or recommended future work

Temporal holdout / more 2011 parts; optional 2019/net-bytes beyond-CA2; stronger independence protocol if claiming three independent campaigns.

## 20. Important files, scripts, configurations, datasets, and artefacts to reproduce/continue

| Item | Path |
|------|------|
| CA2 contract | `mehak-thesis/CA2_COMMITMENTS.md`, `MAHEK NAAZ.docx` |
| Loader | `mhsa-tdl-framework/src/data/gct_loader.py` |
| Final evidence | `results/gct/final_{1,2,3}/`, `FINAL3_BASELINE.md` |
| Independent review | `_analysis_extract/reports/INDEPENDENT_REVIEW_MEHAK.md` |
