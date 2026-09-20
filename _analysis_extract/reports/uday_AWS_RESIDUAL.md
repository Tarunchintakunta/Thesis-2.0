# Uday — AWS residual gate note

**Date:** 2026-09-20  
**Branch:** `feature/aws-ca2-alignment`  
**Artefact:** `uday-thesis/mqtt-qos-iot-core/`

## Non-AWS alignment (evidence)
- Formal RQ/method encoded: QoS × disconnect × rate factorial; device-side ID log; matcher; Holm–Bonferroni plan.
- Local **mock** dry-run proves the harness (`results/mock/`). Mock ≠ IoT Core.
- Terraform modules for IoT Core things/certs/policy + rule → Lambda → DynamoDB (`msg_id`,`delivery_id`). Names: `mqtt-qos-*` only.
- Federated-RF proxy quarantined at `_superseded_proxy/iot-reliability/`.
- Free-tier guard **blocks** the formal live 5×1000×16×5 message envelope.

## Live AWS
**Not applied this pass.** `scripts/run_live.py` exits 2. No IoT endpoint, no things, no billed messages.

## Residuals (AWS is required and **not** sole)
1. Authorised free-tier-safe **lite live fold** (documented: 16 cells × 5 devices × 50 msgs × 1 rep) then confirmatory scale if credits allow
2. `terraform apply` / campaign / `terraform destroy` with manifests under `results/live/`
3. Stats + cost surface on live counted ops; Shvaika contrast
4. Report fold — still <100% until live evidence exists

## READY_FOR_AWS_ALIGNMENT_PATH
**partial** — harness + IaC ready; full-campaign apply **must not** proceed without lite fold / month-split because of IoT message free tier.

```
AWS_CLASS=required
READY_FOR_AWS=harness_only
SOLE_AWS_RESIDUAL=no
LIVE_APPLIED=no
```

## Discipline
Free Tier only; destroy after rounds; no student name/ID in resource names; no mock-as-live claims.
