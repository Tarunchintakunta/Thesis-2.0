# Uday — AWS residual gate note

**Date:** 2026-09-21  
**Branch:** `main`  
**Artefact:** `uday-thesis/mqtt-qos-iot-core/`

## Non-AWS alignment (evidence)
- Formal RQ/method encoded: QoS × disconnect × rate factorial; device-side ID log; matcher; Holm–Bonferroni plan.
- Local **mock** dry-run proves the harness (`results/mock/`). Mock ≠ IoT Core.
- Terraform modules for IoT Core things/certs/policy + rule → Lambda → DynamoDB. Names: `mqtt-qos-*` only.
- Federated-RF proxy quarantined.
- Free-tier guard **blocks** formal 5×1000×16×5; **allows** lite (~6k msgs) and smoke (~96 msgs).

## Live AWS (lite fold — 2026-09-21) — CLOSED
- `READY_FOR_AWS=yes` after tags + destroy hook + cost plan.
- Terraform apply `stage=lite` `device_count=5` in `eu-west-1` (43 resources).
- `scripts/run_live.py --scale lite` → `results/live/LIVE_EVIDENCE.json` (**16 cells**).
- `scripts/destroy_stack.sh` → 43 destroyed; terraform state empty; `.certs` scrubbed; no leftover mqtt-qos things/rules/lambda/table.
- Prior smoke archived at `results/live/archive/smoke-2026-09-21/`.

## Residuals
1. Formal-scale live — **beyond floor** (multi-month / overage); not a floor blocker (`DESIGN_RATIONALE_BEYOND_CA2.md`)
2. Soft: Shvaika prose + report polish

## READY_FOR_AWS_ALIGNMENT_PATH

```
AWS_CLASS=required
READY_FOR_AWS=yes
SOLE_AWS_RESIDUAL=closed
LIVE_APPLIED=lite_destroyed
FORMAL_LIVE=beyond_floor_free_tier
CA2_FLOOR=100
```

## Discipline
Free Tier only for authorised scales; destroy after rounds; no student name/ID in resource names; no mock-as-live claims; lite ≠ formal N.
