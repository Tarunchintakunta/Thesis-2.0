# Configuration manual (Uday — mqtt-qos-iot-core)

**ONE-file SoT:** [`../../CA2_PROPOSED_VS_ARTEFACT.md`](../../CA2_PROPOSED_VS_ARTEFACT.md)  
**Dated soft N:** [`../../DATED_WONTFIX_N_Uday_2026-09-23.md`](../../DATED_WONTFIX_N_Uday_2026-09-23.md)

## Holm / d300>d60 remediable audit (move gate)

Scripted — not manual chat. Must EXIT 0 before MOVE.

```bash
cd uday-thesis/mqtt-qos-iot-core
python3 scripts/audit_holm_root_causes.py
# Writes results/live/confirmatory_1/holm_audit_report.{json,md}
# EXIT 0 required; remediable_total must be 0
```

Disposition when clean: `DATED_WONTFIX_HOLM_D300_GT_D60` (lite schedule ceiling retained; formal N beyond-floor).

## Evidence packs to rebuild claims

| Pack | Path |
|------|------|
| Lite finals | `results/live/final_{1,2}/` |
| Confirmatory Holm | `results/live/confirmatory_1/` |
| Audit report | `results/live/confirmatory_1/holm_audit_report.md` |
| Baseline mapping | `../baseline_papers/BASELINE_PAPER.md` (Shvaika) |

## Reproduce lite live (costed)

```bash
make plan-ft
python scripts/check_ready_for_aws.py
bash scripts/run_final_lite.sh 1   # then destroy via hook
```

Formal 80-cell scale remains Free-Tier-blocked — see `../DESIGN_RATIONALE_BEYOND_CA2.md`.
