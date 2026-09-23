# Yashaswini Leg3 reduction remediable audit (scripted)

Generated: `2026-09-23T07:59:12.400613+00:00`
Root: `/Users/valletivarish/Documents/Thesis-2.0/yashaswini-thesis/serverless-fault-localisation`

## Move gate

- **remediable_total:** 0
- **move_blocker:** False
- **disposition:** `DATED_WONTFIX_REDUCTION_050_FAIL_AMENDED_035`

- reductions: {'final_1': 0.38330079316063415, 'final_2': 0.42172067682834413, 'final_3': 0.47170698953499657}
- detection F1: 0.46874999999999994 (Xing 0.938)

## Remediable bag

```json
{}
```

## Findings

- `pack_inventory_ok` remediable=False
- `reduction_050_fail_035_amended_ok` remediable=False
- `final3_baseline_present` remediable=False
- `f1_gap_to_xing_retained_ok` remediable=False
- `causalrca_quarantine_ok` remediable=False
- `xing_baseline_ok` remediable=False
- `sot_honesty_ok` remediable=False
- `design_amendment_ok` remediable=False
- `wontfix_ok` remediable=False
- `configuration_manual_ok` remediable=False
- `status_stamp_ok` remediable=False

```bash
cd yashaswini-thesis/serverless-fault-localisation
python3 scripts/audit_leg3_reduction_root_causes.py
# EXIT 0 required; remediable_total must be 0 before MOVE
```

