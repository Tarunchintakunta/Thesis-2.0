# Configuration manual (docs pointer + audit reproduce)

**Canonical full manual:** [`../configuration_manual/CONFIGURATION_MANUAL.md`](../configuration_manual/CONFIGURATION_MANUAL.md)

**ONE-file SoT:** [`../../CA2_PROPOSED_VS_ARTEFACT.md`](../../CA2_PROPOSED_VS_ARTEFACT.md)

## Soft-limbs remediable audit (move gate)

Scripted — not manual chat. Must EXIT 0 before MOVE.

```bash
cd rassool-thesis/dynamodb-pk-capacity-eval
python3 scripts/audit_soft_limbs_root_causes.py
# Writes results/analysis/soft_limbs_audit_report.{json,md}
# EXIT 0 required; remediable_total must be 0
```

Disposition when clean: `DATED_WONTFIX_SOFT_LIMBS_N1_EXPLORATORY_W1W2` (W1/W2 n=1 exploratory retained; confirmatory ANOVA = W3/W4 pooled).

## Evidence packs to rebuild claims

| Pack | Path |
|------|------|
| Finals ×3 | `results/final_{1,2,3}/` |
| Pooled ANOVA | `results/pooled_final3_anova.json` |
| W1/W2 key-cells | `results/w1w2_a/` |
| Audit report | `results/analysis/soft_limbs_audit_report.md` |

See also `RUNBOOK.md` and `scripts/run_final_keycell.sh` / `scripts/run_w1w2_keycell.sh`.
