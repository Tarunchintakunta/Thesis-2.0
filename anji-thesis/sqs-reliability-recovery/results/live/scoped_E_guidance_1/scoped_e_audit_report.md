# Anji scoped_E / full-IV remediable audit (scripted)

Generated: `2026-09-23T08:04:15.578371+00:00`

## Move gate

- **remediable_total:** 0
- **move_blocker:** False
- **disposition:** `DATED_WONTFIX_FULL_IV_LIVE_AMENDED`

## Soft limbs (intentional when EXIT 0)

- scoped_E_guidance_1: **20/20** E_guidance_transfer (localsim)
- Full IV live matrix: **amended / dated WONTFIX**
- Live Holm H1–H3: **not claimed**

## Remediable bag

```json
{}
```

## Findings

- `scoped_e_20_of_20_ok` remediable=False
- `kyrychenko_framing_ok` remediable=False
- `full_iv_live_absent_as_amended` remediable=False
- `support_pack_present_final_1` remediable=False
- `support_pack_present_final_2` remediable=False
- `support_pack_present_final_3` remediable=False
- `support_pack_present_key_cells_n3` remediable=False
- `no_fabricated_win_claims` remediable=False

```bash
cd anji-thesis/sqs-reliability-recovery
python3 scripts/audit_scoped_e_root_causes.py
# EXIT 0 required; remediable_total must be 0
```

