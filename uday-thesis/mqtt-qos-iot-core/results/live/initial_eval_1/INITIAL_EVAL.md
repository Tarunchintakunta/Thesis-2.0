# Initial evaluation pass (lite 16-cell live)

**Date:** 2026-09-21 (gate recorded; lite campaign same day)  
**Evidence:** `LIVE_EVIDENCE.json` (16-cell Free-Tier factorial; stack destroyed)  
**Protocol:** AWS IoT Core MQTT QoS 0 vs 1 × disconnect × rate; rules → Lambda → DynamoDB; destroy-after-round.  
**INITIAL_EVAL_PASS:** **yes**

## Verdict
CA2 re-check after lite live method round: still **100%** research-scope floor (`uday-thesis/DESIGN_RATIONALE_BEYOND_CA2.md`). Formal ~600k-msg volume remains beyond-floor. QoS1 survives disconnect cells at lite depth; QoS0 loss rises with disconnect.

## Artefacts
- `LIVE_EVIDENCE.json`
- Full cell manifests under `../manifests/`
- Smoke archive under `../archive/smoke-2026-09-21/`

Final-3 confirmatory full-scale live rounds are **not** started here.
