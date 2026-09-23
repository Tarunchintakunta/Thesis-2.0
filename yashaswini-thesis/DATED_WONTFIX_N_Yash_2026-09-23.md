# DATED_WONTFIX — N-Yash (2026-09-23)

**Thesis:** Yashaswini — `serverless-fault-localisation`  
**Soft limbs:** (1) original Leg3 `reduction_policy_vs_full` ≥ **0.50** **fails** on final_1–3; (2) detection F1 gap to Xing retained; (3) CausalRCA full-90 peer quarantined.

## Why WONTFIX (not remediable fabrication)

1. Measured finals: **0.383 / 0.422 / 0.472** — all **< 0.50**; mean ≈ 0.426. Inventing a 0.50 pass is fabrication.
2. **Amended 2026-09-22** reporting floor ≥ **0.35** for lite Leg3 (see `DESIGN_RATIONALE_BEYOND_CA2.md`); aspirational 0.50 remains beyond-floor.
3. Detection F1 = **0.469** vs Xing **0.938** (≈46.9 pp) — retained limitation; not within 10 pp.
4. CausalRCA n=4 + `fixed_order.json` share=1.0 — quarantined non-peer; full 90-case rerun is beyond-CA2.

## Script gate

```bash
cd yashaswini-thesis/serverless-fault-localisation
python3 scripts/audit_leg3_reduction_root_causes.py
# EXIT 0; remediable_total=0; disposition=DATED_WONTFIX_REDUCTION_050_FAIL_AMENDED_035
```

## Authority

`yashaswini-thesis/CA2_PROPOSED_VS_ARTEFACT.md` §2/§4 · `DESIGN_RATIONALE_BEYOND_CA2.md` · `_analysis_extract/reports/CA2_ALIGNMENT_SCOREBOARD.md` (~72).
