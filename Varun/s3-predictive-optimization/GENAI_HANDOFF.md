# GENAI_HANDOFF.md — Varun (s3-predictive-optimization)

## 0. Document meta

| Field | Value |
|-------|-------|
| Student | Varun Gampa |
| Artefact root | `Varun/s3-predictive-optimization/` |
| Honest CA2 floor | **Closed under disclosed scope (~88)** — confirmatory independent live packs **r4 + r5** with distinct `raw_costs` SHAs; archival r1–r3 not counted as independent; allocation Acc vs Lifecycle **negative** (retained) |
| Eval completeness | Dry-run + live lite + archival `evaluation_r1\|r2\|r3` + **fresh `evaluation_r4\|r5`** (destroy-after) |
| AWS | Live S3 eu-west-1; stack destroyed after r5 (2026-09-22) |
| Handoff date | 2026-09-22 |
| Authority | `results/live/`, `FINAL3_NOTE.md`, `_analysis_extract/reports/INDEPENDENT_REVIEW_VARUN.md` |

## 1. Research problem, motivation, research question, and objectives

**RQ:** To what extent does an integrated predictive storage-class optimisation framework reduce Amazon S3 storage cost and improve storage-class allocation accuracy, relative to AWS-native Lifecycle Policies and Intelligent-Tiering, in a live AWS environment?

## 2. Identified literature gap and how this research addresses it

Predictive / RIC-style allocation vs native Lifecycle and Intelligent-Tiering with live cost evidence (not simulator-only).

## 3. CA2 proposal alignment and any extensions beyond the proposal

Artefact covers recommendation, Prophet forecast, savings, simulator, metadata collector, Terraform. Live two-of-three gate vs natives is the confirmatory claim. **Independence residual closed** by r4/r5 (distinct SHAs). Archival r1–r3 remain disputed copies — do not cite as three independent runs.

## 4. Research methodology and experimental design

Dry-run MAPE/allocation vs naive; live lite PUT latency/CE; live evaluation workloads (static_archival, mixed_access, high_churn) vs Lifecycle + Intelligent-Tiering with Wilcoxon cost deltas. Runner: `scripts/live_full_evaluation.py`.

## 5. Artefact purpose and artefact-only project structure

```
s3-predictive-optimization/
  src/ scripts/ terraform/ results/{data,live}/ tests/
  scripts/live_full_evaluation.py
  results/live/evaluation_r{1,2,3,4,5}/ summary.json raw_costs.json
```

## 6. AWS architecture, services, configurations, and experimental setup

S3 storage-class trials in live AWS (eu-west-1). Destroy-after rounds. Bucket used for r4/r5: `s3-pred-opt-6f20925a7e37bceee781030afa` (destroyed after r5).

## 7. Evaluation metrics and why they were selected

MAPE / beats_naive; allocation accuracy (dry-run); live modeled $ deltas vs natives; Wilcoxon p-values; CE probe on lite / eval probes.

## 8. Baseline definition and baseline comparison

| Role | Method |
|------|--------|
| Native baselines | Lifecycle Policies, Intelligent-Tiering |
| Proposed | Predictive / RIC optimisation pipeline |

Do **not** assume proposed is stronger — report per-workload Wilcoxon honestly.

## 9. Complete evaluation process and number of runs

| Pack | Path | Note |
|------|------|------|
| Dry-run | `results/data/*_results.json` | Demonstrated |
| Live lite | `results/live/live_lite_summary.json` | 48 objects |
| evaluation_r1–r3 | `results/live/evaluation_r{1,2,3}/` | Archival; **identical** raw SHA; `rebuilt_from_run_log=true` |
| evaluation_r4 | `results/live/evaluation_r4/` | Fresh; SHA `7babd39c…`; seed 4242; `rebuilt_from_run_log=false` |
| evaluation_r5 | `results/live/evaluation_r5/` | Fresh; SHA `53bec5e5…`; seed 5252; `rebuilt_from_run_log=false` |

## 10. Final results and key findings (committed evidence)

**Dry-run (review):** pilot MAPE 0.016 vs naive 0.44; baseline 0.006; improved 0.231 — all `beats_naive=true`. Allocation acc: pilot 0.32, baseline 0.504, improved **0.178** (improved worse).

**Live lite:** PUT mean STANDARD 1008.3 ms / IA 681.6; CE sum ~$3.6e-09; Wilcoxon p≈9.63e-07.

**Confirmatory independent live (r4 / r5):** both `meets_ca2_two_of_three=true` with **3/3** workloads significant vs both natives (including high_churn; r4 high_churn p≈0.049, r5 p≈0.0098). Modeled monthly $ via SavingsEstimator — not CE-settled per-object bills.

## 11. How results satisfy or address each research objective

Cost-vs-natives limb **supported** on independent r4/r5 under modeled costs. Allocation-accuracy limb **not supported** for proposed vs Lifecycle on offline seed regeneration (r4 proposed Acc≈**0.369** vs Lifecycle ≈**0.854**, Δ≈**−0.485**; see `allocation_accuracy_r4_r5_offline.json`). Proposed slightly above Intelligent-Tiering Acc. CE-settled production savings not demonstrated.

## 12. How results answer the research question

On live modeled cost, proposed beats Lifecycle + Intelligent-Tiering on all three workloads in two independent full packs (r4, r5). **Allocation accuracy vs pattern-oracle is worse than Lifecycle** on the same seeds (honest negative). Archival r1–r3 must not be counted as three independent successes.

## 13–17. Literature / stats / observations / limitations / conclusions

Limitation: costs are modeled monthly storage via SavingsEstimator, not settled CE object bills; fixed 160 KiB body with metadata size attributes; allocation accuracy not instrumented on live recommendations. Contribution: restored live full-eval runner + two independent confirmatory packs with destroy-after.

## 18–19. Changes / remaining

1. ~~Fresh r4/r5 with distinct SHA~~ — done 2026-09-22.  
2. ~~Allocation accuracy on r4/r5 seeds~~ — offline oracle compare written (`allocation_accuracy_r4_r5_offline.json`); **negative vs Lifecycle retained**.  
3. Keep archival r1–r3 labeled non-independent.

## 20. Important files

`scripts/live_full_evaluation.py`, `results/live/evaluation_r{4,5}/`, `FINAL3_NOTE.md`, archival `evaluation_r{1,2,3}/`, Terraform under artefact root.
