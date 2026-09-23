# DATED_WONTFIX — N-Uday (Holm d300 > d60)

**Date:** 2026-09-23  
**Thesis:** Uday / `mqtt-qos-iot-core`  
**Limb:** Holm-controlled claim that QoS0 loss at disconnect **300 s > 60 s**

## Decision

**WONTFIX** under disclosed **lite** Free-Tier schedule. Evidence shows **d60 ≡ d300 loss = 0.68** (steady and bursty). Confirmatory pack marks limb **FAIL**. Not a silent park.

## Evidence

- `mqtt-qos-iot-core/results/live/confirmatory_1/holm_stats.json` → `holm_d300_gt_d60_limb.status = FAIL`
- `mqtt-qos-iot-core/results/live/final_1|final_2/LIVE_EVIDENCE.json` — identical QoS0 losses at 60/300
- Root cause: lite publish wall-clock (~49 s) → both cuts cover remaining messages

## Gate

```bash
cd uday-thesis/mqtt-qos-iot-core
python3 scripts/audit_holm_root_causes.py
# expect EXIT 0; disposition DATED_WONTFIX_HOLM_D300_GT_D60
```

## Authority

`uday-thesis/CA2_PROPOSED_VS_ARTEFACT.md` §4 · `DESIGN_RATIONALE_BEYOND_CA2.md` · `_analysis_extract/reports/AGENT_UNFINISHED_TRACKER.md` (N-Uday CLOSED).

Formal N / longer schedule that could separate d60 vs d300 remains **beyond-floor** (Free Tier), not reopened by this WONTFIX.
