# Rasool soft-limbs remediable audit (scripted)

Generated: `2026-09-23T07:47:46.617395+00:00`

## Move gate

- **remediable_total:** 0
- **move_blocker:** False
- **disposition:** `DATED_WONTFIX_SOFT_LIMBS_N1_EXPLORATORY_W1W2`

## Soft limbs (intentional when EXIT 0)

- W1/W2 key-cells: **n=1 exploratory** (KW); not confirmatory ANOVA
- Full W1–W4 confirmatory ANOVA / formal n=30: **beyond-floor**
- Cost Explorer: **not claimed** (list-price proxy)

## Remediable bag

```json
{}
```

## Findings

- `pack_ok_final_1` remediable=False
- `pack_ok_final_2` remediable=False
- `pack_ok_final_3` remediable=False
- `w3_capacity_ns_retained` remediable=False
- `w3_interaction_ns_retained` remediable=False
- `pooled_anova_ok` remediable=False
- `pack_ok_w1w2_a` remediable=False
- `w1w2_exploratory_only` remediable=False
- `no_fabricated_win_claims` remediable=False

```bash
cd rassool-thesis/dynamodb-pk-capacity-eval
python3 scripts/audit_soft_limbs_root_causes.py
# EXIT 0 required; remediable_total must be 0
```

