# Anji — status gate (CA2 / live eval)

**Updated:** 2026-09-21  
**Thesis:** Reliability and Recovery of Amazon SQS Messaging under Injected Consumer and Downstream Failures  
**Artefact:** `sqs-reliability-recovery/`

## Gates

```
CA2_ALIGNMENT=100
INITIAL_EVAL_PASS=yes
FINAL3=not_started
DESTROY_CONFIRMED=yes
GENAI_HANDOFF=deferred
```

## Initial live evaluation (ONE)

| Field | Value |
|-------|-------|
| Config | `configs/live_key_cells.yaml` (lite 4 cells × n=1) |
| Region | eu-west-1 |
| Deploy | Terraform `sqs-rr-dev`, ESM `max_concurrency=2` (shared ConcurrentExecutions=10) |
| Tags | project only (`sqs-reliability-recovery`) — no student name/ID |
| Results | `sqs-reliability-recovery/results/live/initial_eval_1/` |
| Wall | 793.0 s |
| Cost sum | ≈ $0.00132 |
| Destroy | verified 0 TF resources; Lambda/SQS/DynamoDB absent |

### Measured cells (evidence-only)

| Campaign | Fault | VT | MRC | loss | dup | DLQ | recovery_s | thr | success |
|----------|-------|---:|----:|-----:|----:|----:|-----------:|----:|--------:|
| L_vt_consumer_kill | consumer_kill | 30 | 5 | 0.0 | 0.025 | 0.0 | 3.123 | 2.979 | 1.0 |
| L_vt_consumer_kill | consumer_kill | 90 | 5 | 0.0 | 0.015 | 0.0 | 2.609 | 1.530 | 1.0 |
| L_mrc_unhandled_error | unhandled_error | 30 | 1 | 0.0 | 0.0 | 0.23 | — | 4.688 | 0.805 |
| L_mrc_unhandled_error | unhandled_error | 30 | 5 | 0.0 | 0.08 | 0.0 | 39.329 | 2.313 | 1.0 |

## CA2 re-check (after initial_eval_1)

| Element | Still aligned? | Evidence |
|---------|:--------------:|----------|
| RQ (SQS config → reliability/recovery under fault) | **yes** | VT + MRC varied; loss/dup/DLQ/recovery/thr measured live |
| Objectives (VT/MRC/DLQ; recovery; baseline-under-fault; trade-off) | **yes** | Same lite IVs/DVs; Obj3 framed via MRC=1 DLQ vs success trade-off |
| Gap (beyond Kyrychenko steady-state) | **yes** | Fault injection on live SQS, not throughput-only |
| Method (controlled fault campaigns + manifests) | **yes** | `experiment_runner --live` + Terraform outputs |
| Artefact (SAM/TF SQS+Lambda+DLQ+Dynamo) | **yes** | Applied then destroyed |
| Eval scope (lite key cells; confirmatory stats = localsim) | **yes** | Live = smoke; H1–H3 remain `results/summary/stats_H1_H2_H3.json` |

**Verdict: CA2 still 100.** Gate `INITIAL_EVAL_PASS=yes`. Final-3 **not** started this step.

## Rubric70 (light, honest)

- **Pos vs prior lite:** loss remains 0; MRC=1 again shows DLQ capture (0.23; prior 0.16).
- **Neg / mixed:** VT→recovery not monotone this n=1 round (VT30 3.12s vs VT90 2.61s; prior was 2.34 vs 7.53) — lite protocol does not recover campaign-A 1:1 VT law; MRC=1 success 0.805 (prior 0.91).
- **Limitations:** n=1; 200 orders; concurrency=2; underpowered for Holm; authoritative stats stay localsim 350-cell.

Detail: `sqs-reliability-recovery/STATUS.md`, `_analysis_extract/reports/anji_AWS_RESIDUAL.md`.
