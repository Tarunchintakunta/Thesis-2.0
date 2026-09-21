# Live AWS evidence (Uday / mqtt-qos-iot-core)

Authoritative file: `LIVE_EVIDENCE.json`

- **Scale:** lite (16 cells; Free-Tier-safe; full factorial)
- **When:** 2026-09-21, eu-west-1
- **Stack:** `mqtt-qos-lite-*` — applied, measured, **destroyed** (43 resources)
- **Prior smoke:** archived under `archive/smoke-2026-09-21/`
- **Not** formal-scale (5×1000×16×5 / ~600k IoT msgs) — that depth is beyond floor / multi-month

Directional (bound): QoS1 loss 0.0 all cells; QoS0 loss rises under disconnect; QoS1 pays latency/backlog.
