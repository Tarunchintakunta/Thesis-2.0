# DATED_WONTFIX — N-Pooja (2026-09-23)

**Thesis:** Pooja — `paks-framework`  
**Soft limb:** Formal CA2 includes infrastructure **cost**; **AWS Cost Explorer / billing-linked** validation was **not** run. Cost DV is closed via **LIST_PRICE** `$0.04`/pod-hour (`USD_PER_POD_HOUR`) tagged **SIMULATED**.

## Why WONTFIX (not remediable fabrication)

1. Live HPA vs PAKS method residual is on disk: `results/live/final_{1,2,3}/` + `final3_latency_summary.json` (destroy_confirmed).
2. Cost scalar is intentionally modeled: `src/eval/metrics.py` (`USD_PER_POD_HOUR = 0.04`); live packs set `evidence.cost=SIMULATED`.
3. Enabling Cost Explorer / GetCostAndUsage and waiting for settled bills is a **new** AWS billing campaign beyond disclosed Free-Tier floor; inventing CE-validated $/op would be fabrication.

## Script gate

```bash
cd pooja-thesis/paks-framework
python3 scripts/audit_cost_explorer_root_causes.py
# EXIT 0; remediable_total=0; disposition=DATED_WONTFIX_COST_EXPLORER
```

## Authority

`pooja-thesis/CA2_PROPOSED_VS_ARTEFACT.md` §4 · `DESIGN_RATIONALE_BEYOND_CA2.md` (billing-linked cost scoped out) · `_analysis_extract/reports/CA2_ALIGNMENT_SCOREBOARD.md` (~62).
