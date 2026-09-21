# Anji alignment residual (AWS-goal)

**Updated:** 2026-09-21  
**Alignment:** **100/100** (CA2 floor) — re-checked after `initial_eval_1`  
**Status:** **COMPLETE** · `INITIAL_EVAL_PASS=yes` · final-3 **not** started

## Initial live evaluation (ONE)

- Config: `configs/live_key_cells.yaml` (lite 4×n=1)
- Region: eu-west-1; Terraform `sqs-rr-*`; ESM `max_concurrency=2` (ConcurrentExecutions limit=10)
- Evidence: `anji-thesis/sqs-reliability-recovery/results/live/initial_eval_1/`
- Wall 793.0 s; usd sum ≈ $0.00132; destroy verified (0 TF resources; Lambda/SQS/DDB gone)
- Tags: project only — no student name/ID

## CA2 re-check vs formal (RQ / objectives / gap / method / artefact / eval)

| Element | Still 100? | Note |
|---------|:----------:|------|
| RQ | yes | VT + MRC under fault; loss/dup/DLQ/recovery/thr live |
| Objectives | yes | Same IVs/DVs; Obj3 framed by MRC=1 DLQ↔success trade-off |
| Gap | yes | Fault injection beyond Kyrychenko steady-state |
| Method | yes | Live runner + manifests |
| Artefact | yes | Applied then destroyed |
| Eval | yes | Lite smoke; confirmatory H1–H3 remain localsim 350 |

**Neg/mixed (Rubric70):** VT→recovery not monotone this n=1 round (3.12s @ VT30 vs 2.61s @ VT90); MRC=1 success 0.805. Does **not** break CA2 scope.

```
COMPLETE=yes ALIGNMENT=100 INITIAL_EVAL_PASS=yes FINAL3=not_started
SOLE_AWS_RESIDUAL=closed DESTROY_CONFIRMED=yes
```
