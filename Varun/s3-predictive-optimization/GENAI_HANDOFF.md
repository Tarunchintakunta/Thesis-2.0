# GENAI_HANDOFF.md — Varun (s3-predictive-optimization)

## 0. Document meta

| Field | Value |
|-------|-------|
| Student | Varun Gampa |
| Artefact root | `Varun/s3-predictive-optimization/` |
| Honest CA2 floor | **PARTIAL (~70–72)** — live protocol real; e1–e3 independence **not** accepted as three fresh hashes on this worktree |
| Eval completeness | Dry-run + live lite + `evaluation_r1\|r2\|r3` on disk. Fresh r4/r5 packs **MISSING on this branch** (re-run residual) |
| AWS | Live S3 evaluations; destroy-after historically |
| Handoff date | 2026-09-22 |
| Authority | `results/live/`, `_analysis_extract/reports/INDEPENDENT_REVIEW_VARUN.md` |

## 1. Research problem, motivation, research question, and objectives

**RQ:** To what extent does an integrated predictive storage-class optimisation framework reduce Amazon S3 storage cost and improve storage-class allocation accuracy, relative to AWS-native Lifecycle Policies and Intelligent-Tiering, in a live AWS environment?

## 2. Identified literature gap and how this research addresses it

Predictive / RIC-style allocation vs native Lifecycle and Intelligent-Tiering with live cost evidence (not simulator-only).

## 3. CA2 proposal alignment and any extensions beyond the proposal

Artefact covers recommendation, Prophet forecast, savings, simulator, metadata collector, Terraform. Live two-of-three gate vs natives is the confirmatory claim — **independence of e1–e3 disputed** (identical raw_costs SHA on this tree).

## 4. Research methodology and experimental design

Dry-run MAPE/allocation vs naive; live lite PUT latency/CE; live evaluation workloads (static_archival, mixed_access, high_churn) vs Lifecycle + Intelligent-Tiering with Wilcoxon cost deltas.

## 5. Artefact purpose and artefact-only project structure

```
s3-predictive-optimization/
  src/ scripts/ terraform/ results/{data,live}/ tests/
  results/live/evaluation_r{1,2,3}/ summary.json raw_costs.json
```

## 6. AWS architecture, services, configurations, and experimental setup

S3 storage-class trials in live AWS (historically eu-west-1). Destroy-after rounds.

## 7. Evaluation metrics and why they were selected

MAPE / beats_naive; allocation accuracy (dry-run); live modeled $ deltas vs natives; Wilcoxon p-values; CE probe on lite.

## 8. Baseline definition and baseline comparison

| Role | Method |
|------|--------|
| Native baselines | Lifecycle Policies, Intelligent-Tiering |
| Proposed | Predictive / RIC optimisation pipeline |

Do **not** assume proposed is stronger — high_churn null retained.

## 9. Complete evaluation process and number of runs

| Pack | Path | Note |
|------|------|------|
| Dry-run | `results/data/*_results.json` | Demonstrated |
| Live lite | `results/live/live_lite_summary.json` | 48 objects |
| evaluation_r1–r3 | `results/live/evaluation_r{1,2,3}/` | `meets_ca2_two_of_three=true` on r3; **rebuilt_from_run_log=true**; SHA identical across r1–r3 per independent review |
| evaluation_r4–r5 | — | **Not present on this worktree** |

## 10. Final results and key findings (committed evidence)

**Dry-run (review):** pilot MAPE 0.016 vs naive 0.44; baseline 0.006; improved 0.231 — all `beats_naive=true`. Allocation acc: pilot 0.32, baseline 0.504, improved **0.178** (improved worse).

**Live lite:** PUT mean STANDARD 1008.3 ms / IA 681.6; CE sum ~$3.6e-09; Wilcoxon p≈9.63e-07.

**evaluation_r3 summary:** `meets_ca2_two_of_three=true`, `rebuilt_from_run_log=true`, note admits rebuild after mid-run wipe. Independent review: static_archival ΔLC significant; high_churn ΔLC ≈6.53e-05 p≈0.557 (**null**).

## 11. How results satisfy or address each research objective

Cost-vs-natives limb partially evidenced but independence weak. Allocation-accuracy limb **not supported** for improved arm on dry-run (0.178). CE-settled production savings not demonstrated.

## 12. How results answer the research question

Mixed: some workloads beat natives on modeled cost; high_churn null; improved allocation accuracy worse than baseline dry-run. Treating three identical rebuilt packs as independent full-scale successes is **not honest**.

## 13–17. Literature / stats / observations / limitations / conclusions

Keep high_churn null visible. Limitation: rebuilt cost matrix; missing fresh r4/r5 on this branch. Contribution: live protocol + honest null cell, not a clean two-of-three win under independence scrutiny.

## 18–19. Changes / remaining

1. Re-run ≥2 fresh live evaluations with distinct `raw_costs` SHA (r4/r5).  
2. Live allocation-accuracy metric, not only $ deltas.  
3. Do not claim CA2 100% until independence closed.

## 20. Important files

`results/live/evaluation_r{1,2,3}/`, `FINAL3_NOTE.md`, `INDEPENDENT_REVIEW_VARUN.md`, Terraform under artefact root.
