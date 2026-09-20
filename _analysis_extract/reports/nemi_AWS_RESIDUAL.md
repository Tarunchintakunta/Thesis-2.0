# Nemi alignment residual (AWS-goal, not sole-AWS)

**Updated:** 2026-09-20  
**Alignment after claim hygiene:** **~68/100** (was ~64%)

## Compact
`RQ6 Obj9 Method10 Impl10 Exp6 Metrics8 Evidence7 Claims7 Rubric5` → **~68/100**

## Hygiene done (this pass)
- Methodology demoted: committed PoC = synthetic / 30 rounds; full UNSW + 50-round config = future only
- Pilot (`results/pilot/pilot_results.json`) quarantined vs comparison PoC
- RESULTS_NOTE: removed false “compression reduces communication” checkmark
- DOI `note={doi:…}` verified on wired `refs.bib`; STATUS/README metrics locked to `results/comparison/results.json`
- Terraform present, not applied; no student name/ID tags

## Top blockers to 100%
1. Centralised IDS baseline (CA2 comparator) — **non-AWS**  
   Evidence of absence: no centralised trainer/results path under `Nemi/securefl-ids/`
2. Real UNSW-NB15 (full) experiment — **non-AWS**  
   Evidence: PoC synthetic only; `RESULTS_NOTE.md`; methodology now honest
3. Live cloud-native FL evaluation — **AWS residual**  
   Evidence: `securefl-ids/terraform/` scaffold; README “not applied”

**AWS residual:** yes (cloud FL) — **not sole** (baseline + UNSW still open)

```
GATE_READY=no AWS_CLASS=required SOLE_AWS_RESIDUAL=no READY_FOR_AWS=no
```
