# Anji alignment residual (AWS-goal)

**Updated:** 2026-09-20 (iter-2 run-count reconcile)  
**Alignment after packaging-dedup hygiene:** **~90/100** (was ~78%)

## Compact
`RQ9 Obj12 Method13 Impl13 Exp10 Metrics10 Evidence9 Claims8 Rubric6` → **~90/100**

## Hygiene done (this pass)
- Phase run-count reconciled: **350 design cells** vs **690 on-disk** manifests (`adaptive_vt` packaging twins) — `evaluation.tex`, `results/README.md`, `STATUS.md`
- Analysis loader dedupes twins (`analysis/load_results.py`); regenerated `stats_H1_H2_H3.json` / `hypotheses.md` with `runs: 350`, n=5/cell
- H3_recovery restored to **fail to reject after Holm** (U=62.5, p_adj=0.084, r=0.667); twin-inflated reject drafts withdrawn
- H1–H2 / exploratory DLQ numbers updated to deduped stats; “first systematic” demoted; DIVE still not claimed

## Top blockers to 100%
1. **Live SQS / CloudWatch key-cell campaign** (sole hard AWS residual)
2. Optional soft: dedicated adaptive_vt campaign *only if* DIVE is re-introduced as a claim

**AWS residual:** yes (live SQS) — **SOLE hard residual**  
**Localsim packaging gap:** closed (documented + deduped in analysis)

```
GATE_READY=yes
READY_FOR_AWS=yes
AWS_CLASS=required
SOLE_AWS_RESIDUAL=yes
```

Evidence paths: `anji-thesis/sqs-reliability-recovery/STATUS.md`, `results/summary/stats_H1_H2_H3.json` (`runs: 350`), `results/README.md`, `latex_report/text/evaluation.tex` (phase table), `analysis/load_results.py`.
