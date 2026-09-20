# Nemi alignment residual (AWS-goal, not sole-AWS)

**Updated:** 2026-09-20  
**Alignment after claim hygiene:** **~64/100** (was ~58%)

## Compact
`RQ6 Obj9 Method9 Impl10 Exp6 Metrics8 Evidence6 Claims5 Rubric5` → **~64/100**

## Hygiene done
- PoC metrics locked to `results/comparison/results.json` (0.793/0.800, F1 near 0)
- README baseline 91–94% demoted to literature-only; Docker/K8s/AWS overclaims removed
- STATUS <100%; Terraform present not applied; bib `note={doi:…}`

## Top blockers to 100%
1. Centralised IDS baseline (CA2 comparator)
2. Real UNSW-NB15 (full) experiment
3. Live cloud-native FL evaluation (AWS residual)

**AWS residual:** yes (cloud FL) — **not sole**

```
GATE_READY=no AWS_CLASS=required SOLE_AWS_RESIDUAL=no
```
