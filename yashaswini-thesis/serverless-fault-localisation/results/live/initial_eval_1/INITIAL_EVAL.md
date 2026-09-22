# Initial evaluation pass (Leg 3 lite overhead)

**Date:** 2026-09-21 (gate recorded; lite Leg 3 2026-09-20)  
**Evidence:** `overhead.json`, `learned_lower_bound.csv`  
**Protocol:** Terraform `faultlab` lite Leg 3 — 5 min × 3 conditions @ 1 rps; destroy-after-round.  
**INITIAL_EVAL_PASS:** **yes**

## Verdict
CA2 re-check after this live method round: still **100%** research-scope floor (`DESIGN_RATIONALE_BEYOND_CA2.md`). Leg 2 RCAEval tables locked; CausalRCA 90 / PDF rebuild remain soft beyond-CA2. policy vs full reduction_policy_vs_full = 0.803 on lite window.

## Artefacts
- `overhead.json`, `learned_lower_bound.csv`
- Raw under `../../data/runs/live_lite_overhead/`

Final-3 confirmatory full-scale live rounds are **not** started here.
