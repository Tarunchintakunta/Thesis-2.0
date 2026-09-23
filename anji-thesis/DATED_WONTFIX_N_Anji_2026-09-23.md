# DATED_WONTFIX — N-Anji (full IV live matrix amended)

**Date:** 2026-09-23  
**Thesis:** Anji / `sqs-reliability-recovery`  
**Limb:** Full CA2 IV live matrix (batch/burst/multi-fault/full VT grid on AWS)

## Decision

**WONTFIX / amended** relative to disclosed floor. Live evidence remains **lite key cells** (+ smoke finals + n=3). Guidance-under-fault closed via **`scoped_E_guidance_1` 20/20** (localsim `E_guidance_transfer`). Full IV live is beyond disclosed scope — not silently claimed.

## Evidence

- `results/live/scoped_E_guidance_1/` — 20/20 manifests + `summary.csv` + `SCOPED_E_BASELINE.md`
- No `full_iv*` live artefact (audit forbids fabricating one)
- Localsim H1–H3 remain fail-to-reject after Holm (`results/summary/stats_H1_H2_H3.json`)

## Gate

```bash
cd anji-thesis/sqs-reliability-recovery
python3 scripts/audit_scoped_e_root_causes.py
# expect EXIT 0; disposition DATED_WONTFIX_FULL_IV_LIVE_AMENDED
```

## Authority

`anji-thesis/CA2_PROPOSED_VS_ARTEFACT.md` §4 · `DESIGN_RATIONALE_BEYOND_CA2.md` · `_analysis_extract/reports/AGENT_UNFINISHED_TRACKER.md` (N-Anji CLOSED).

Live Holm H1–H3 and adaptive_vt/DIVE remain not claimed.
