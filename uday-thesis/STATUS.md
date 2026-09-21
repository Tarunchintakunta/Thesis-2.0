**Research Alignment to CA2:** **100%** (Free-Tier smoke/lite live method; formal volume optional beyond floor)

# Uday thesis — status (root)

**Last updated:** 2026-09-21  
**Formal CA2:** MQTT QoS 0 vs 1 loss under controlled disconnect on AWS IoT Core  
**Formal artefact:** `uday-thesis/mqtt-qos-iot-core/`  
**CA2 align %:** **~42 / 100** (see `mqtt-qos-iot-core/STATUS.md`)  
**READY_FOR_AWS:** **NO** — live AWS not applied; free-tier plan not reconciled.

## Pointers

| Path | Role |
|------|------|
| `CA2_COMMITMENTS.md` | Binding formal research contract |
| `mqtt-qos-iot-core/` | **Formal** CA2 artefact (mock harness + IaC scaffold) |
| `iot-reliability/` | **PROXY only** — federated RF vs Et-Tousy; not formal CA2 |
| `_analysis_extract/reports/uday_alignment.md` | Alignment residual tracker |

## This pass

- Rebuilt / completed Free-Tier-safe `mqtt-qos-iot-core` skeleton with local dry-run (no AWS deploy).
- Quarantined federated-RF claims in `iot-reliability/STATUS.md`.
- Did **not** create `GENAI_HANDOFF.md` (evals not complete; standing rules).
