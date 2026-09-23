# Project Status

**Student:** Rasool Basha Durbesula (24205478)  
**Project:** Partition-Key Design and Capacity Mode in Amazon DynamoDB: An Empirical Performance-Cost Evaluation under Serverless Workloads  
**Date:** 2026-09-23

## ONE-file SoT + move gate (binding)

| Artefact | Path |
|----------|------|
| **SoT** | [`../CA2_PROPOSED_VS_ARTEFACT.md`](../CA2_PROPOSED_VS_ARTEFACT.md) |
| **Audit** | `scripts/audit_soft_limbs_root_causes.py` → `results/analysis/soft_limbs_audit_report.{json,md}` |
| **Disposition** | `DATED_WONTFIX_SOFT_LIMBS_N1_EXPLORATORY_W1W2` (`DATED_WONTFIX_N_Rasool_2026-09-23.md`) |
| **Audit exit** | **EXIT 0** · `remediable_total=0` · **MOVE ALLOWED** |

```bash
cd rassool-thesis/dynamodb-pk-capacity-eval
python3 scripts/audit_soft_limbs_root_causes.py
# EXIT 0 required
```

## Alignment note (2026-09-23 — honest floor)

**Honest CA2 floor ≈ 88%** (W3/W4 finals + pooled ANOVA + w1w2_a key-cells). Do **not** market ALIGNMENT=100.  
`INITIAL_EVAL_PASS=yes`. Final-3 **DONE**. W1/W2 = **n=1 exploratory** (dated WONTFIX soft limb). Authority: SoT + `_analysis_extract/reports/CA2_ALIGNMENT_SCOREBOARD.md`.

| Issue | Status |
|-------|--------|
| Live AWS DynamoDB key-cell rounds (W3/W4) | **final_1–3** (12 cells × 3; destroy_confirmed) |
| Pooled confirmatory ANOVA | **`results/pooled_final3_anova.json`** (key effect supported) |
| W1/W2 key-cells | **`results/w1w2_a/`** (12/12; n=1 exploratory) |
| Soft: full W1–W4 confirmatory ANOVA / n=30 | **DATED_WONTFIX** (scripted) |
| INITIAL_EVAL_PASS | **yes** |
| MOVE ALLOWED | **yes** (remediable_total=0) |

```
CA2_FLOOR=~88 ALIGNMENT=honest (no market 100)
INITIAL_EVAL_PASS=yes FINAL3=done_3of3
SOT=CA2_PROPOSED_VS_ARTEFACT.md AUDIT_EXIT=0
SOLE_AWS_RESIDUAL=closed_under_disclosed_scope
AUTHORITY=CA2_PROPOSED_VS_ARTEFACT.md
```

### Rubric quality notes

- **Artefact:** K1–K3 × on-demand/provisioned × W1–W4 measured (W3/W4 confirmatory fleets; W1/W2 n=1); destroy-after.
- **Pos:** pooled Key F significant on W3/W4 mean latency; throttle_rate=0 on measured cells.
- **Neg / mixed retained:** capacity/interaction ns on W3 mean latency; W1/W2 exploratory only; list-price cost (not Cost Explorer).
- **vs Pantelić:** DynamoDB-native PK+capacity under serverless — gap-fill meter DVs; not a SQL/NoSQL re-bench.

### Live evidence (cite SoT §2 for same-metrics tables)

- Finals: `results/final_{1,2,3}/batches.csv` + destroy_confirmed
- ANOVA: `results/pooled_final3_anova.json`
- W1/W2: `results/w1w2_a/` + `W1W2_BASELINE.md`
- Audit: `results/analysis/soft_limbs_audit_report.md`

```
READY_FOR_AWS=done_keycell_and_finals
SOLE_AWS_RESIDUAL=no
AWS_CLASS=required
GATE_READY=yes
LIVE_KEYCELL_COMPLETE=yes
LIVE_FULL_FACTORIAL=partial_w1w2_n1
LIVE_ANOVA=pooled_final3_w3w4
DESTROY_AFTER_ROUND=yes
MOVE_ALLOWED=yes
```

## Executive Summary

Artefact implemented. **Live W3/W4 finals ×3 + pooled ANOVA + w1w2_a** on disk. Soft limbs (n=1 W1/W2; formal n=30) dated WONTFIX under scripted audit EXIT 0. Report/viva fold later.

## What Is NOT Complete (soft — dated WONTFIX, not remediable blockers)

1. **Full W1–W4 confirmatory ANOVA / Holm×12** — beyond floor
2. **Formal n=30 / cell** — beyond floor
3. **Cost Explorer cross-check** — not claimed (list-price)

## Gate

```
GATE_READY=yes AWS_CLASS=required SOLE_AWS_RESIDUAL=no MOVE_ALLOWED=yes AUDIT_EXIT=0
```

**Last Updated:** 2026-09-23  
**Status:** SoT + audit EXIT 0; honest floor ~88; MOVE ALLOWED
