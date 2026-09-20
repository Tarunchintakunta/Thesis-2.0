# Anji alignment residual (AWS-goal, not sole-AWS)

**Updated:** 2026-09-20  
**Alignment after claim hygiene:** **~78/100** (was ~72%)

## Compact
`RQ8 Obj11 Method12 Impl12 Exp9 Metrics9 Evidence7 Claims5 Rubric5` → **~78/100**

## Hygiene done
- H1–H3 ↔ `stats_H1_H2_H3.json`; DIVE/adaptive_vt softened; Obj4 cost estimator-only
- STATUS <100%; live SQS not claimed; bib `note={doi:…}` sweep
- Softened “live would not change findings” overclaim

## Top blockers to 100%
1. Live SQS / CloudWatch key-cell campaign (AWS residual)
2. Optional dedicated adaptive_vt campaign if DIVE retained as a claim
3. Phase run-count table reconciliation (documented vs on-disk) without inventing metrics

**AWS residual:** yes (live SQS) — **not sole** (localsim packaging gaps remain)

```
GATE_READY=no AWS_CLASS=required SOLE_AWS_RESIDUAL=no
```
