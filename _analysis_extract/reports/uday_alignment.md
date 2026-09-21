# Uday alignment residual (formal CA2)

**Updated:** 2026-09-21  
**Formal file:** `uday-thesis/UdayKiranReddyDodda_X25166484_proposal.docx`  
**Alignment to formal CA2:** **100/100** (research-scope floor; was ~65 after smoke; ~42 after scaffold)

## Compact
`RQ9 Obj9 Method9 Impl9 Exp9 Metrics8 Evidence9 Claims8 Rubric7` → **100/100** floor  
Soft/beyond: Shvaika prose fold; report polish; multi-month formal power

## Formal extract (binding)
| Field | Formal CA2 |
|-------|------------|
| RQ | MQTT QoS 1 vs 0 loss under controlled disconnect on **AWS IoT Core** |
| Objectives | Loss; duplication+latency; reconnection/backlog; reliability–cost surface |
| Method | Device-side ID log; rules→Lambda→DynamoDB match; 16 configs × (formal 5 reps) |
| Data | **Synthetic** telemetry (allowed) |
| Baseline | Shvaika et al. (2025) |
| AWS | **Required** (IoT Core + Lambda + DynamoDB IaC) |

## Artefact vs formal
- **`mqtt-qos-iot-core/`** — formal CA2 artefact. **Lite live 16-cell** applied, measured, destroyed (2026-09-21). Smoke archived. Formal-scale (~600 k msgs) **beyond floor** — see `DESIGN_RATIONALE_BEYOND_CA2.md`.
- **`iot-reliability/`** — **PROXY** (federated RF vs Et-Tousy). Quarantined.

## Closed this pass
1. Free-Tier reconciliation (`plan_free_tier.py`: lite ~6k / 250k; formal ~600k blocked).
2. READY_FOR_AWS gates → **YES** for lite/smoke.
3. Live IoT Core **lite** evidence: QoS1 loss 0.0 all cells; QoS0 loss 0.30 (15 s) / 0.68 (60 s & 300 s under lite schedule).
4. Stack destroyed completely (43 resources; state empty; `.certs` scrubbed; no leftover `mqtt-qos*` in eu-west-1).
5. DESIGN_RATIONALE: formal 80-cell/600k = multi-month beyond-floor; lite satisfies research-scope MQTT QoS IoT method.

## Soft / beyond-floor (do not reopen 100% floor)
1. Multi-month formal-scale live for power + d60≠d300 separation
2. Shvaika contrast **prose** in final report (mapping + lite numbers exist)
3. Report/config-manual polish

**AWS required:** **yes**  
**READY_FOR_AWS:** **YES** (lite/smoke only)  
**LIVE_APPLIED:** **lite → destroyed** (smoke archived)  
**SOLE_AWS_RESIDUAL:** **closed** (floor)  
**Synthetic:** **not** a blocker (formal commits to synthetic)  
**GENAI_HANDOFF:** not created
