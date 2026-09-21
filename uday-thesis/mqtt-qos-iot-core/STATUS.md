# mqtt-qos-iot-core — formal CA2 artefact status

**Last updated:** 2026-09-21  
**Formal contract:** `uday-thesis/CA2_COMMITMENTS.md`  
**Alignment residual:** `_analysis_extract/reports/uday_alignment.md`  
**CA2 align % (honest):** **100 / 100** (research-scope floor; Free-Tier smoke/lite method)
**READY_FOR_AWS:** **YES** (lite/smoke; formal volume optional beyond floor)

**Status:** **CA2 floor COMPLETE** — formal 600k-msg volume is beyond-floor optional (`../DESIGN_RATIONALE_BEYOND_CA2.md`).

## What this artefact is

Formal CA2: **MQTT QoS 0 vs 1 message loss under controlled publisher disconnect on AWS IoT Core**, with device-side ID log matched via **rules → Lambda → DynamoDB**. Factors: QoS × disconnect ∈ {0,15s,1m,5m} × rate ∈ {steady,bursty}. Synthetic devices are allowed (and used).

## Gates (READY_FOR_AWS)

| Gate | Status |
|------|--------|
| Project tags on terraform (`Project`, `Thesis`, `Environment`, `ManagedBy`, `Campaign`) | Pass |
| Destroy hook `scripts/destroy_stack.sh` | Pass |
| Free-tier cost plan: **lite** under monthly IoT budget with headroom; **formal** blocked | Pass (`make plan-ft`) |
| Live runner unblocked for **smoke/lite only** when gates pass | Pass |

Check: `python scripts/check_ready_for_aws.py`

## Live smoke (2026-09-21) — done & destroyed

| Item | Value |
|------|-------|
| Scale | `smoke` (4 cells × 2 devices × 8 msgs; inside lite envelope) |
| Region | `eu-west-1` |
| Stack | `mqtt-qos-smoke-*` applied then **destroyed** (25 resources; state empty; `.certs` scrubbed) |
| Evidence | `results/live/LIVE_EVIDENCE.json` |
| Directional result | QoS1 loss 0.0 (d=0 and d=15); QoS0 loss 0.5 (d=0) / 0.75 (d=15) — **pilot only**, not formal N |

## Free-tier reconciliation

| Scale | IoT msgs upper | vs 250 000 free | Headroom |
|-------|----------------|-----------------|----------|
| formal | ~600 000 | **exceeds** | blocked |
| lite | ~6 000 | ok (~2.4%) | ~97.6% |
| smoke | ~96 | ok | ~99.96% |

## What is done

| Piece | Status |
|-------|--------|
| Local mock harness | Done |
| Factorial + seeds | Done |
| lite + smoke configs | Done |
| Metrics + Holm on mock | Done |
| IaC modules + tags + `enable_apply` | Done |
| `run_live.py` smoke/lite after gates | Done (formal blocked) |
| One live smoke campaign + destroy | **Done** |

## What still blocks 100% CA2

1. **Formal-scale** live campaign (5×1000×16×5) — exceeds single-month IoT free tier.
2. Full **lite** 16-cell live factorial (optional next fold; smoke was the authorised first fold).
3. Shvaika et al. (2025) baseline contrast in the report.
4. Report/config-manual rewrite against MQTT (not federated RF).

## Measurement honesty

- `results/mock/` — **not** AWS measurements.
- `results/live/` — AWS IoT Core smoke evidence; **not** formal-scale CA2 completion.

## Quarantine

`uday-thesis/iot-reliability/` (federated RF vs Et-Tousy) is a **PROXY / different RQ** — not formal CA2 fulfilment.
