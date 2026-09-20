# Rasool alignment residual (live W3/W4 key-cells measured)

**Updated:** 2026-09-20 (live key-cell round 12/12; stack destroyed)  
**Alignment:** **~92/100** (was ~78% after claim hygiene)  
**Status:** **NOT COMPLETE** (literal 100% still open)

## Compact
`RQ8 Obj10 Method13 Impl13 Exp11 Metrics9 Evidence11 Claims8 Rubric8` → **~92/100**

## Live AWS inventory (evidence-only)

Path: `rassool-thesis/dynamodb-pk-capacity-eval/results/`

| Artifact | Present |
|----------|---------|
| `batches.csv` | yes — 12 live rows (`data_source=live`) |
| Raw per-batch gz | yes — `raw/b00-K{1,2,3}-{on_demand,provisioned}-W{3,4}.csv.gz` (12) |
| `keycell_summary.csv` / `.json` | yes — list-price `cost_per_10k` via `add_costs` |
| `keycell_round_run.log` / `keycell_round_meta.txt` | yes — start 11:55:38Z end 12:47:42Z |
| `keycell_destroy.log` | yes — **Destroy complete! Resources: 32 destroyed.** `DESTROY_EXIT=0` |
| Terraform after round | **destroyed** (0 resources; no `ddbpk*` tables/Lambda in eu-west-1) |

### Measured cells (n=1; orders=100000; region eu-west-1)

| Cell | p99 ms | thr ops/s | throttle_rate | cost_per_10k |
|------|-------:|----------:|--------------:|-------------:|
| K1-on_demand-W3 | 7.047 | 199.922 | 0.0 | 0.003901 |
| K1-provisioned-W3 | 7.339 | 199.925 | 0.0 | 0.002328 |
| K2-on_demand-W3 | 6.948 | 199.918 | 0.0 | 0.003874 |
| K2-provisioned-W3 | 7.499 | 199.919 | 0.0 | 0.010498 |
| K3-on_demand-W3 | 10.320 | 199.919 | 0.0 | 0.007062 |
| K3-provisioned-W3 | 8.333 | 199.920 | 0.0 | 0.007128 |
| K1-on_demand-W4 | 7.640 | 466.531 | 0.0 | 0.003886 |
| K1-provisioned-W4 | 10.232 | 466.532 | 0.0 | 0.000998 |
| K2-on_demand-W4 | 9.631 | 466.530 | 0.0 | 0.003899 |
| K2-provisioned-W4 | 7.667 | 466.533 | 0.0 | 0.000998 |
| K3-on_demand-W4 | 10.623 | 466.483 | 0.0 | 0.007063 |
| K3-provisioned-W4 | 11.490 | 466.531 | 0.0 | 0.005567 |

**Key-cell round:** complete (12/12 planned for W3/W4 × K1–K3 × capacity).  
**Request-path list-price sum (`cost_usd`):** ≈ **$0.251**.  
**Missing from full factorial:** all W1/W2 cells.  
**Not computed:** live ANOVA / KS / Tukey.

Directional only (do not cite as confirmatory): zero throttles on all 12; K3 latencies/costs higher than K1/K2 on several cells; provisioned W4 `cost_per_10k` lower than on-demand for K1/K2 on this replicate.

## Hygiene already done
- Placeholders demoted; K4 quarantined; DOI notes; no Cost Explorer claim
- IaC tags project-only (no student name/ID)

## Top blockers to 100%
1. **Soft:** W1/W2 live factorial cells
2. **Soft:** confirmatory repeats ($n>1$ / design $n=30$) and live ANOVA if required
3. Soft: Cost Explorer cross-check (optional; not required to close hard residual)

**Hard AWS residual closed:** prior sole hard residual was the live DynamoDB key-cell campaign; 12/12 W3/W4 measured + destroy-after-round satisfies that gate. Remaining gaps are soft.

**Do not start a new AWS apply** unless an operator decides W1/W2 or confirmatory repeats are required for literal 100%.

```
GATE_READY=yes
LIVE_KEYCELL_COMPLETE=yes
LIVE_FULL_FACTORIAL=no
LIVE_ANOVA=no
AWS_CLASS=required
SOLE_AWS_RESIDUAL=no
DESTROY_AFTER_ROUND=yes
```

Evidence: `STATUS.md`, `results/batches.csv`, `results/keycell_summary.csv`, `latex_report/text/evaluation.tex`, `report/generated/cell_summary.md`.
