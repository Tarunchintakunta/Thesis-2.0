# Vikas campaign E1–E3 remediable audit (scripted)

Generated: `2026-09-23T07:50:20.539951+00:00`
Campaign: `/Users/valletivarish/Documents/Thesis-2.0/vikas-thesis/lambda-idempotency-eval/data/runs/live/campaign`

## Move gate

- **remediable_total:** 0
- **move_blocker:** False
- **disposition:** `DATED_WONTFIX_P4_QUARANTINED`

- N-scale: deliveries=24000 requests=9000 (expect 24000/9000)
- E1–E3 counts: {'E1': 2, 'E2': 4, 'E3': 3}
- path_counts: {'P3': 8000, 'P1': 8000, 'P2': 8000}

## Remediable bag

```json
{}
```

## Findings

- `pack_inventory_ok` remediable=False
- `n_scale_ok` remediable=False
- `path_delivery_balance_ok` remediable=False
- `cells_shape_ok` remediable=False
- `e1_e3_supported` remediable=False
- `headline_cell_invariants_ok` remediable=False
- `checks_delivery_ok` remediable=False
- `experiment_yaml_p1_p3_only` remediable=False
- `assumptions_a12_ok` remediable=False
- `p4_absent_from_live_campaign` remediable=False
- `p4_quarantine_doc_ok` remediable=False
- `p4_quarantine_doc_ok` remediable=False
- `p4_quarantine_doc_ok` remediable=False
- `final_report_p4_banner_ok` remediable=False
- `destroy_confirmed` remediable=False
- `configuration_manual_ok` remediable=False
- `no_marketing_100` remediable=False
- `no_marketing_100` remediable=False
- `no_marketing_100` remediable=False
- `sensitivity_pack` remediable=False

```bash
cd vikas-thesis/lambda-idempotency-eval
python3 scripts/audit_campaign_root_causes.py
# EXIT 0 required; remediable_total must be 0 before MOVE
```

