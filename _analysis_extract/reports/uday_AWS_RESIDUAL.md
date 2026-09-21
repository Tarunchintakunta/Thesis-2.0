# Uday — AWS residual gate note

**Date:** 2026-09-21  
**Branch:** `main`  
**Artefact:** `uday-thesis/mqtt-qos-iot-core/`

## Non-AWS alignment (evidence)
- Formal RQ/method encoded: QoS × disconnect × rate factorial; device-side ID log; matcher; Holm–Bonferroni plan.
- Local **mock** dry-run proves the harness (`results/mock/`). Mock ≠ IoT Core.
- Terraform modules for IoT Core things/certs/policy + rule → Lambda → DynamoDB (`msg_id`,`delivery_id`). Names: `mqtt-qos-*` only.
- Federated-RF proxy quarantined.
- Free-tier guard **blocks** formal 5×1000×16×5; **allows** lite (~6k msgs, ~97.6% headroom) and smoke (~96 msgs).

## Live AWS (smoke fold — 2026-09-21)
- `READY_FOR_AWS=yes` after tags + destroy hook + cost plan.
- Terraform apply `stage=smoke` `device_count=2` in `eu-west-1`.
- `scripts/run_live.py --scale smoke` → `results/live/LIVE_EVIDENCE.json` (4 cells).
- `scripts/destroy_stack.sh` → 25 resources destroyed; terraform state empty; `.certs` scrubbed.

## Residuals (AWS still required for 100%; not sole)
1. Formal-scale live (or multi-month staged formal) — free-tier blocked as single month
2. Optional full lite 16-cell live fold
3. Stats + Shvaika contrast in report
4. Report fold

## READY_FOR_AWS_ALIGNMENT_PATH

```
AWS_CLASS=required
READY_FOR_AWS=yes
SOLE_AWS_RESIDUAL=no
LIVE_APPLIED=smoke_destroyed
FORMAL_LIVE=blocked_free_tier
```

## Discipline
Free Tier only for authorised scales; destroy after rounds; no student name/ID in resource names; no mock-as-live claims; smoke ≠ formal CA2 completion.
