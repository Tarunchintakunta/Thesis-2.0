# Uday alignment residual (formal CA2)

**Updated:** 2026-09-21  
**Formal file:** `uday-thesis/UdayKiranReddyDodda_X25166484_proposal.docx`  
**Alignment to formal CA2:** **~65/100** (was ~42 after scaffold; ~18 vs formal before MQTT artefact; prior ~90 was vs superseded Et-Tousy federated proxy)

## Compact
`RQ6 Obj6 Method7 Impl8 Exp6 Metrics6 Evidence5 Claims5 Rubric4` → **~65/100**

## Formal extract (binding)
| Field | Formal CA2 |
|-------|------------|
| RQ | MQTT QoS 1 vs 0 loss under controlled disconnect on **AWS IoT Core** |
| Objectives | Loss; duplication+latency; reconnection/backlog; reliability–cost surface |
| Method | Device-side ID log; rules→Lambda→DynamoDB match; 16 configs × 5 reps |
| Data | **Synthetic** telemetry (allowed) |
| Baseline | Shvaika et al. (2025) |
| AWS | **Required** (IoT Core + Lambda + DynamoDB IaC) |

## Artefact vs formal
- **`mqtt-qos-iot-core/`** — formal CA2 artefact: mock harness + Free-Tier **lite/smoke** live path + IaC. **Smoke live applied, measured, destroyed** (2026-09-21). Formal-scale not run (free-tier exceedance).
- **`iot-reliability/`** — **PROXY** (federated RF vs Et-Tousy). Quarantined.

## Closed this pass
1. Free-Tier reconciliation documented (`plan_free_tier.py`: lite ~6k / 250k; formal ~600k blocked).
2. READY_FOR_AWS gates (tags, destroy hook, cost plan, STATUS latch) → **YES** for lite/smoke.
3. Live IoT Core smoke evidence under `results/live/LIVE_EVIDENCE.json` (QoS1 loss 0; QoS0 loss higher under disconnect) — pilot N only.
4. Stack destroyed completely after campaign.

## True blockers to 100% (vs formal)
1. Formal-scale live campaign (5×1000×16×5) or accepted multi-month / overage plan
2. Shvaika et al. (2025) baseline contrast in report
3. Report/config-manual rewrite against MQTT (federated RF remains quarantined)

**AWS required:** **yes**  
**READY_FOR_AWS:** **YES** (lite/smoke only)  
**LIVE_APPLIED (smoke):** **yes → destroyed**  
**Synthetic:** **not** a blocker (formal commits to synthetic)
