# mqtt-qos-iot-core — formal CA2 artefact status

**Last updated:** 2026-09-21  
**Formal contract:** `uday-thesis/CA2_COMMITMENTS.md`  
**Alignment residual:** `_analysis_extract/reports/uday_alignment.md`  
**CA2 align % (honest):** **~42 / 100**  
**READY_FOR_AWS:** **NO**

## What this artefact is

Formal CA2: **MQTT QoS 0 vs 1 message loss under controlled publisher disconnect on AWS IoT Core**, with device-side ID log matched via **rules → Lambda → DynamoDB**. Factors: QoS × disconnect ∈ {0,15s,1m,5m} × rate ∈ {steady,bursty}. Synthetic devices are allowed (and used).

## What is done (this pass)

| Piece | Status |
|-------|--------|
| Local mock harness (device log → mock broker → in-memory DDB match) | Done — no AWS required |
| Factorial + deterministic seeds | Done (`configs/experiment.yaml`) |
| Metrics: loss, dup, latency mean/p95/p99, reconnect/backlog, cost surface | Done (`scripts/analyse.py`) |
| Holm–Bonferroni confirmatory tests | Done (mock evidence only) |
| IaC scaffold (Terraform + SAM twin), project tags only | Done — **not applied** (`enable_apply=false`) |
| `scripts/run_live.py` | Intentionally **BLOCKED** |

## What is NOT done (blocks 100% CA2)

1. **Live AWS IoT Core campaign** (required by formal CA2) — not deployed; credentials/apply not run.
2. **Formal-scale live evidence** (5 devices × 1000 msgs × 16 cells × 5 reps) and baseline contrast vs Shvaika et al. (2025).
3. **Free-Tier reconciliation** — upper-bound planning (`scripts/plan_free_tier.py`) shows formal message volume can exceed a single-month IoT Core free-tier message allowance; needs staged runs, reduced pilot, or accepted paid overage before apply.
4. Report/config-manual rewrite against MQTT (not federated RF).

## Measurement honesty

Mock dry-run results under `results/mock/` are **not** AWS measurements. Manifests carry `measurement_kind` stating the mock broker path.

## Quarantine

`uday-thesis/iot-reliability/` (federated RF vs Et-Tousy) is a **PROXY / different RQ** — not formal CA2 fulfilment.
