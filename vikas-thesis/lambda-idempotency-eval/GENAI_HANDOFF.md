# GENAI_HANDOFF.md — Vikas (lambda-idempotency-eval)

## 0. Document meta

| Field | Value |
|-------|-------|
| Student | Vikas |
| Artefact root | `vikas-thesis/lambda-idempotency-eval/` |
| Honest CA2 floor | **PARTIAL (~88)** — live E1–E3 campaign Demonstrated; P4 quarantined; do not equate campaign fill with perfect-marks 100 |
| Eval completeness | Primary pack = live campaign N=1000×3×3 = **24000 deliveries** (larger than three lite smokes) |
| AWS | Live Lambda + DynamoDB Streams; destroyed after campaign |
| Handoff date | 2026-09-22 |
| Authority | `data/runs/live/campaign/`, `results/live/FINAL3_NOTE.md` |

## 1. Research problem, motivation, research question, and objectives

Evaluate idempotency / exactly-once delivery patterns for serverless producers under duplicate and capacity pressure (P1 baseline vs P2/P3 proposed patterns).

## 2. Identified literature gap and how this research addresses it

Empirical live comparison of idempotency strategies on Lambda→DynamoDB with streams ground truth — not moto-only.

## 3. CA2 proposal alignment and any extensions beyond the proposal

Live campaign closes the AWS residual for E1–E3. P4 remains quarantined (not evidence for CA2 floor). Soft: optional post-gate lite final_1–3 beyond floor.

## 4. Research methodology and experimental design

Live backend; 9000 requests / 24000 invocations; workers=6; patterns P1/P2/P3; expectations on duplicates and capacity (WCU); streams GT checks.

## 5. Artefact purpose and artefact-only project structure

```
lambda-idempotency-eval/
  src/ scripts/ terraform/ tests/
  data/runs/live/campaign/  # primary evidence
  results/live/FINAL3_NOTE.md
```

## 6. AWS architecture, services, configurations, and experimental setup

From `run_info.json`: region **eu-west-1**; Lambda python3.12 arm64 256MB timeout 2s; DynamoDB on-demand STANDARD with NEW_AND_OLD_IMAGES streams; Terraform 1.15.7 / AWS provider 6.64.0.

## 7. Evaluation metrics and why they were selected

Duplicate rate, capacity/WCU deltas, streams ground-truth cleanliness — map to E1–E3 expectations.

## 8. Baseline definition and baseline comparison

| Role | Pattern |
|------|---------|
| Baseline | P1 (duplicates expected = 1.0) |
| Proposed | P2 / P3 (dup=0.0; P3−P2 capacity trade) |

## 9. Complete evaluation process and number of runs

| Pack | Path | Scale |
|------|------|-------|
| Live campaign | `data/runs/live/campaign/` | invocations=24000, deliveries.jsonl lines=24000 |
| Note | `results/live/FINAL3_NOTE.md` | campaign is primary final-scale pack |

Destroyed after campaign (per FINAL3_NOTE).

## 10. Final results and key findings (committed evidence)

`run_info.json`: phase=campaign; backend=live; requests=9000; invocations=**24000**; workers=6; warmup cold=6; seed=25178849; t_start_utc=2026-09-21T12:20:17Z.

`deliveries.jsonl`: **24000** lines (~12.9 MB).

Independent review (cohort scoreboard): P1 dup=1.0; P2/P3 dup=0.0; P3−P2 = +2 WCU; streams GT checks zeros — E1–E3 **Demonstrated**.

## 11. How results satisfy or address each research objective

E1–E3 live expectations supported by campaign artefacts. P4 not part of floor.

## 12. How results answer the research question

Proposed idempotency patterns eliminate duplicates vs P1 under this live load; capacity trade appears on P3 vs P2 (+2 WCU). Positive for dedup; cost/capacity trade retained.

## 13–17. Literature / stats / observations / limitations / conclusions

Campaign is one large live pack (not three independent lite finals). Limitation: ConcurrentExecutions=10; P4 quarantined; do not invent beyond-disk stats. Contribution: live 24k-delivery evidence with GT streams.

## 18–19. Changes / remaining

Keep P4 quarantined. Optional lite final_1–3 only if needed beyond floor. Honest floor ~88 not marketing 100.

## 20. Important files

`data/runs/live/campaign/{run_info.json,deliveries.jsonl,expectations.csv,checks.csv,ground_truth.jsonl}`, `results/live/FINAL3_NOTE.md`.
