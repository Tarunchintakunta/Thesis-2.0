# Chaitanya H3/H4 remediable audit (scripted)

Generated: `2026-09-23T07:59:39.857102+00:00`
Root: `/Users/valletivarish/Documents/Thesis-2.0/chaitanya-thesis/lambda-coldstart-isolation`

## Move gate

- **remediable_total:** 0
- **move_blocker:** False
- **disposition:** `DATED_WONTFIX_H4_PRACTICAL_NULL_H3_UNDERPOWERED`

- H3 lite reject=False p_holm=1.0 drop=0.2
- H4 practical_null=True span_ms=11.961000000000013 kw_reject=True
- H1/H2 confirmatory reject ok=True

## Remediable bag

```json
{}
```

## Findings

- `pack_inventory_ok` remediable=False
- `configuration_manual_ok` remediable=False
- `destroy_confirmed` remediable=False
- `destroy_confirmed` remediable=False
- `destroy_confirmed` remediable=False
- `h1_h2_confirmatory_reject_ok` remediable=False
- `h3_null_evidenced_ok` remediable=False
- `h4_practical_null_ok` remediable=False
- `h4_decision_band_ok` remediable=False
- `bluemke_baseline_ok` remediable=False
- `sot_honesty_ok` remediable=False
- `wontfix_ok` remediable=False
- `analysis_plan_h3_h4_deferral_ok` remediable=False
- `status_stamp_ok` remediable=False

```bash
cd chaitanya-thesis/lambda-coldstart-isolation
python3 scripts/audit_h3_h4_root_causes.py
# EXIT 0 required; remediable_total must be 0 before MOVE
```

