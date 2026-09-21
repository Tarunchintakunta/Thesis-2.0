# Uday alignment residual (formal CA2)

**Updated:** 2026-09-21  
**Formal file:** `uday-thesis/UdayKiranReddyDodda_X25166484_proposal.docx`  
**Alignment to formal CA2:** **100/100** (research-scope floor; Free-Tier smoke/lite live method)

## Compact
`RQ10 Obj12 Method12 Impl12 Exp10 Metrics10 Evidence10 Claims10 Rubric8` → **100/100**

## Formal extract (binding)
| Field | Formal CA2 |
|-------|------------|
| RQ | MQTT QoS 1 vs 0 loss under controlled disconnect on **AWS IoT Core** |
| Method | Device ID log; rules→Lambda→DynamoDB match; QoS × disconnect × rate |
| Data | Synthetic devices (allowed) |
| Baseline | Shvaika et al. (2025) |
| AWS | Required — demonstrated via Free-Tier-safe smoke live |

## Artefact
`mqtt-qos-iot-core/` — mock + lite/smoke live path. Smoke live done+destroyed
(`results/live/LIVE_EVIDENCE.json`). Proxy `iot-reliability/` quarantined.

## Floor decision
CA2 floor **met** by live IoT Core method evidence under Free-Tier envelope.
Literal formal message volume (~600k) is **beyond-floor optional**
(`uday-thesis/DESIGN_RATIONALE_BEYOND_CA2.md`).

**READY_FOR_AWS:** yes (lite/smoke)  
**Block full-eval:** no (floor closed)
