# Yashaswini alignment residual (AWS-goal, not sole-AWS)

**Updated:** 2026-09-20  
**Alignment after claim hygiene:** **~75/100** (was 62%)

## Compact
`RQ8 Obj10 Method12 Impl12 Exp9 Metrics9 Evidence7 Claims5 Rubric3` → **~75/100**

## Hygiene done
- `evaluation.tex` Leg 2 tables rewritten to match `results/rcaeval/*` (AC@3=0.611, F1=0.469)
- CausalRCA quarantined at $n{=}4$; hybrid underperformance retained
- Overhead competitiveness claims demoted to estimator-only; STATUS <100%
- DOI `note={doi:…}` pass on wired bibs where easy

## Top blockers to 100%
1. Live Leg 3 AWS overhead (AWS residual)
2. CausalRCA incomplete ($n{=}4$)
3. Optional PDF rebuild / bib depth

**AWS residual:** yes (Leg 3) — **not sole** (CausalRCA + packaging)

```
GATE_READY=no AWS_CLASS=required SOLE_AWS_RESIDUAL=no
```
