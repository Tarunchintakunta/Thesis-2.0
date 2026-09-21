# Design rationale — Uday (Free-Tier MQTT lite floor)

## Binding floor
Formal CA2 requires live MQTT QoS 0 vs 1 loss under controlled disconnect on
**AWS IoT Core** with rules → Lambda → DynamoDB matching. Synthetic devices are allowed.

## Delivered at floor
- Artefact `mqtt-qos-iot-core/` with mock harness + Free-Tier-safe **lite/smoke** live path
- Live **smoke** campaign on eu-west-1 (4 cells), measured QoS0 vs QoS1 loss, then **destroyed**
- Evidence: `mqtt-qos-iot-core/results/live/LIVE_EVIDENCE.json`
- READY_FOR_AWS gates for lite/smoke; project tags; destroy hook

## Beyond-floor (optional, not blockers)
The literal formal factorial (5 devices × 1000 msgs × 16 cells × 5 reps ≈ 600k IoT
messages) **exceeds** a single-month IoT Core Free Tier message allowance (~250k).
Multi-month staging or accepted paid overage is **optional beyond CA2 floor**.
The research-scope method (live IoT Core QoS disconnect campaign with matching and
loss metrics) is demonstrated by the Free-Tier-safe smoke/lite envelope.

## Thesis writing
Report smoke/lite live numbers honestly as Free-Tier-safe evidence; do not claim
formal N=1000×5 without running it.
