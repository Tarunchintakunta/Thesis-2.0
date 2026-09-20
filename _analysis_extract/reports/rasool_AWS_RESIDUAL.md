# Rasool alignment residual (AWS-goal)

**Updated:** 2026-09-20 (live K1–K3 × capacity × W3/W4 matrix complete)  
**Alignment:** **~92/100** (was ~78% after claim hygiene)

## Compact
`RQ10 Obj12 Method13 Impl13 Exp11 Metrics10 Evidence11 Claims8 Rubric4` → **~92/100**

## Live AWS evidence (measured)
- Driver: `scripts/run_matrix.py --blocks 1 --workloads W3,W4 --key-designs K1,K2,K3 --orders 100000`
- Region `eu-west-1`; results bucket `ddbpk-results-…`; `data_source=live`
- **12/12 cells** in `results/batches.csv` (all throttle_rate=0)

| Cell | ok | p99 ms | thr/s | $ proxy |
|------|---:|-------:|------:|--------:|
| K2-prov-W3 | 18000 | 7.5 | 199.9 | 0.0098 |
| K3-od-W4 | 84000 | 10.6 | 466.5 | 0.0593 |
| K3-prov-W4 | 84000 | 11.5 | 466.5 | 0.0289 |
| K2-od-W4 | 84000 | 9.6 | 466.5 | 0.0328 |
| K3-prov-W3 | 18000 | 8.3 | — | 0.0202 |
| K1-od-W3 | 18000 | 7.0 | — | 0.0070 |
| K3-od-W3 | 18000 | 10.3 | — | 0.0127 |
| K2-od-W3 | 18000 | 6.9 | — | 0.0070 |
| K1-prov-W3 | 18000 | 7.3 | — | 0.0098 |
| K1-od-W4 | 84000 | 7.6 | — | 0.0326 |
| K1-prov-W4 | 84000 | 10.2 | — | 0.0140 |
| K2-prov-W4 | 84000 | 7.7 | — | 0.0140 |

- Log estimate ≈ **$0.32** request-path (prices 2026-09-11); wall ~0.85 h of load
- W1/W2 and multi-block replicates not in this round (disclosed)

## Remaining to literal 100%
1. Soft: fold tables into `evaluation.tex` / `cell_summary.md` if fold agent pending; optional KS/ANOVA if pre-registered
2. Soft: W1/W2 + extra blocks if formal CA2 demands full factorial depth
3. Destroy IaC after fold documented

**AWS residual:** **soft** (hard live DDB factorial for K×capacity×W3/W4 closed)

```
GATE_READY=yes READY_FOR_AWS=yes AWS_CLASS=required
SOLE_AWS_RESIDUAL=no LIVE_KEYCELLS_12=yes
```
