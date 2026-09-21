# Uday alignment residual (formal CA2)

**Updated:** 2026-09-21  
**Formal file:** `uday-thesis/UdayKiranReddyDodda_X25166484_proposal.docx`  
**Alignment to formal CA2:** **~42/100** (was ~18 before `mqtt-qos-iot-core` scaffold; prior ~90 was vs superseded Et-Tousy federated proxy)

## Compact
`RQ5 Obj4 Method5 Impl6 Exp3 Metrics5 Evidence2 Claims4 Rubric3` → **~42/100**

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
- **`mqtt-qos-iot-core/`** — formal CA2 artefact: mock dry-run harness + IaC scaffold + stats/cost scripts. **Live AWS not applied.**
- **`iot-reliability/`** — **PROXY** (federated RF vs Et-Tousy). Quarantined in its `STATUS.md`.

## True blockers to 100% (vs formal)
1. Live AWS IoT Core campaign per method (synthetic devices OK)
2. Free-Tier / cost plan reconciled for formal message volume (or accepted overage)
3. Formal-scale live evidence + Shvaika baseline contrast in report
4. Soft: keep federated-RF claims quarantined (done in STATUS)

**AWS required:** **yes** — **not deployed** this pass  
**READY_FOR_AWS:** **NO**  
**Synthetic:** **not** a blocker (formal commits to synthetic)
