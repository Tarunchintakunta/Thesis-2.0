# Uday thesis — status (root)

**Last updated:** 2026-09-21  
**Formal CA2:** MQTT QoS 0 vs 1 loss under controlled disconnect on AWS IoT Core  
**Formal artefact:** `uday-thesis/mqtt-qos-iot-core/`  
**CA2 align %:** **100 / 100** (research-scope floor; see `DESIGN_RATIONALE_BEYOND_CA2.md`)  
**READY_FOR_AWS:** **YES** (lite/smoke only; formal single-month blocked)

## Pointers

| Path | Role |
|------|------|
| `CA2_COMMITMENTS.md` | Binding formal research contract |
| `DESIGN_RATIONALE_BEYOND_CA2.md` | Floor vs multi-month formal depth |
| `mqtt-qos-iot-core/` | **Formal** CA2 artefact (mock + live lite evidence + IaC) |
| `iot-reliability/` | **PROXY only** — federated RF vs Et-Tousy; not formal CA2 |
| `_analysis_extract/reports/uday_alignment.md` | Alignment residual tracker |

## This pass

- Ran **lite** live (16 cells, ~6 k IoT msgs upper) in `eu-west-1`: apply → collect → **destroy** (43 resources).
- Smoke archived under `mqtt-qos-iot-core/results/live/archive/smoke-2026-09-21/`.
- Formal 80-cell / ~600 k msgs scoped **beyond floor** (free-tier exceedance).
- Did **not** create `GENAI_HANDOFF.md`.
