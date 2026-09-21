# Vikas AWS residual (sole hard)

**Updated:** 2026-09-21  
**Alignment:** **~74/100** — **NOT COMPLETE**  
**AWS_CLASS:** required (Lambda + DynamoDB; formal CA2)  
**SOLE_AWS_RESIDUAL:** **yes** — live full campaign  
**READY_FOR_AWS:** yes (non-AWS claim hygiene done; sole gap is the campaign itself)  
**Block full-eval cycle:** **YES** until campaign deliveries exist and Evaluation is live-primary

## Verified state (no invented results)

- Pilot complete: `data/runs/live/pilot/` (300 deliveries; N=1000 chosen).
- Campaign **empty:** `data/runs/live/campaign/deliveries.jsonl` = **0 bytes**.
- `campaign_r2/` and `campaign_r3/` contain only `run.log` start lines — not campaigns.
- Stack remnant: `idem-eval-fn` last modified 2026-09-19 (pilot era). **No apply** in this pass; no finished campaign to fold.

## Sole hard residual

1. `make campaign` (N from `results/live/pilot_choice.json`) → non-empty `deliveries.jsonl` / stream / run_info  
2. Sensitivity + CloudWatch collect  
3. `make analyse` → `results/live/` + `figures/live/`  
4. Replace Evaluation primary tables with live cells (moto stays functional-only)

```
SOLE_AWS_RESIDUAL=yes CAMPAIGN=empty PILOT=done ALIGNMENT=~74 DESTROY_AFTER_ROUND=yes ConcurrentExecutions=10
```
