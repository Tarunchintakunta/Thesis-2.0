# Project Status: uday-thesis (`mqtt-qos-iot-core`)

**Last Updated:** 2026-09-20  
**Branch:** `feature/aws-ca2-alignment`  
**Research Alignment to CA2:** **~56/100** (compact below)  
**Status:** **NOT COMPLETE** — **<100%** (do **not** treat as SUBMIT-READY)

## Compact

`RQ8 Obj6 Method7 Impl7 Exp4 Metrics7 Evidence3 Claims8 Rubric6` → **~56/100**

Prior **~18/100** was the federated-RF proxy scored against the formal MQTT CA2.
Prior **~90%** was that proxy scored against the **wrong** (Et-Tousy) question.

## Summary

Formal CA2 is **MQTT QoS 0 vs 1 loss under controlled disconnect on AWS IoT Core**,
with duplication, E2E latency (mean/p95/p99), reconnection/backlog, and a
reliability–cost surface. This tree implements the harness (device-side ID log,
mock DynamoDB matcher, Terraform for IoT Core → rule → Lambda → DynamoDB) and a
**local mock dry-run**. **No live AWS apply this pass.**

Mock results **must not** be reported as IoT Core measurements.

## Evidence bound this pass

| Artefact | Claim allowed |
|----------|----------------|
| `results/mock/` | Harness works end-to-end on a **documented mock** of publisher disconnect |
| `terraform/` | IaC is valid / ready; **not applied** |
| `_superseded_proxy/iot-reliability/` | Quarantined federated RF — **not CA2 evidence** |
| Live IoT Core campaign | **None** |

## What is done

1. Formal artefact tree `mqtt-qos-iot-core/` (replaces proxy as the CA2 pointer)
2. Device simulator with virtual clock; QoS×disconnect×rate factorial
3. Device-side ID log written **before** publish; matcher counts loss and duplicates
4. Terraform modules: 5 things + certs/policy; rule `devices/+/telemetry` → Lambda → DynamoDB (`msg_id`,`delivery_id`)
5. Analysis: loss/dup/latency percentiles, reconnect/backlog, unit-price cost, Holm–Bonferroni plan
6. Free-tier guard: full 5×1000×16×5 live plan **blocked** (IoT message envelope)
7. Proxy quarantined; claims not mixed

## Blockers to 100% (vs formal)

1. **Live AWS IoT Core campaign** (synthetic devices OK) — not started; `scripts/run_live.py` exits 2
2. Formal scale on live (or a pre-registered lite fold whose limits are stated) with 5 reps
3. Confirmatory Holm–Bonferroni on **live** loss/dup/latency, not mock
4. Reliability–cost surface from **counted live operations** × published prices
5. Contrast with Shvaika et al. (2025) using live delivery-completeness numbers
6. Soft: LaTeX/report body still to be written against live (or explicitly mock-labelled) evidence

## AWS

```
AWS_CLASS=required
READY_FOR_AWS=harness_only
SOLE_AWS_RESIDUAL=no
LIVE_APPLIED=no
DESTROY_AFTER_ROUND=n/a
GATE_READY=no
```

AWS is **required** by the formal CA2 and is **not** the sole remaining gap
(report/live stats/cost surface still open). Residual:
`_analysis_extract/reports/uday_AWS_RESIDUAL.md`.

## Free tier

Formal live 16×5×5×1000 publishes plus QoS 1 PUBACKs exceeds ~250k monthly IoT
messages. Do not apply the full campaign as-is. Lite fold is documented in
`scripts/assert_free_tier_guard.py --mode live_lite` and is **not** run here.
