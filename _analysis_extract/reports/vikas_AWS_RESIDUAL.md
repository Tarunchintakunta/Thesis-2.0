# Vikas AWS residual (sole hard)

**Updated:** 2026-09-21  
**Alignment:** **100/100** — **COMPLETE**  
**AWS_CLASS:** required (Lambda + DynamoDB; formal CA2)  
**SOLE_AWS_RESIDUAL:** **no** — live full campaign closed  
**READY_FOR_AWS:** n/a (campaign already run)  
**Block full-eval cycle:** **NO**

## Verified state (no invented results)

- Pilot complete: `data/runs/live/pilot/` (300 deliveries; N=1000 chosen).
- Campaign **complete:** `data/runs/live/campaign/deliveries.jsonl` = **24000 lines** (9000 requests; N=1000 × 3 × 3).
- Sensitivity complete: 1400 deliveries; streams + CloudWatch folded.
- Analysis: `results/live/summary.md` — E1/E2/E3 all **supported**.
- Free-Tier guards: `WORKERS=6` under account `ConcurrentExecutions=10`; project tags only (no student IDs).
- **Destroy confirmed:** terraform destroy 8 resources; Lambda `idem-eval-fn`, table `idem-eval`, role, alarms, log group absent in eu-west-1.

## Residual

None hard. Soft only: fold live cells into LaTeX Evaluation as primary tables.

```
SOLE_AWS_RESIDUAL=no CAMPAIGN=done PILOT=done ALIGNMENT=100 DESTROY_CONFIRMED=yes ConcurrentExecutions=10 WORKERS=6
```
