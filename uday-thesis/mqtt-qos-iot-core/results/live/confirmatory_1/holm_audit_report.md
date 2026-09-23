# Uday Holm / d300>d60 remediable audit (scripted)

Generated: `2026-09-23T08:03:50.745994+00:00`

## Move gate

- **remediable_total:** 0
- **move_blocker:** False
- **disposition:** `DATED_WONTFIX_HOLM_D300_GT_D60`

## Soft limbs (intentional when EXIT 0)

- Holm d300>d60: **FAIL** (lite schedule ceiling; d60≡d300 loss 0.68)
- Formal N / 80-cell: **beyond-floor**
- final_3: absent; confirmatory_1 = final_1+final_2 pool

## Remediable bag

```json
{}
```

## Findings

- `pack_ok_final_1` remediable=False
- `pack_ok_final_2` remediable=False
- `d300_equiv_d60_steady` remediable=False
- `d300_equiv_d60_bursty` remediable=False
- `shvaika_framing_ok` remediable=False
- `confirmatory_1_ok` remediable=False
- `d60_equiv_d300_final_1_steady` remediable=False
- `d60_equiv_d300_final_1_bursty` remediable=False
- `qos1_loss_zero_final_1` remediable=False
- `d60_equiv_d300_final_2_steady` remediable=False
- `d60_equiv_d300_final_2_bursty` remediable=False
- `qos1_loss_zero_final_2` remediable=False
- `no_fabricated_win_claims` remediable=False
- `beyond_floor_design_present` remediable=False

```bash
cd uday-thesis/mqtt-qos-iot-core
python3 scripts/audit_holm_root_causes.py
# EXIT 0 required; remediable_total must be 0
```

