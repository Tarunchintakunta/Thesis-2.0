# Design rationale — beyond CA2 (Vikas)

**Updated:** 2026-09-23  
**Honest floor ≈ 88%.** Do **not** market ALIGNMENT=100. Authority: `CA2_ALIGNMENT_SCOREBOARD.md`.

## Floor (met)

- Live campaign P1/P2/P3 × multiplicity {1,2,5}, N=1000, Streams ground truth, destroy-after.  
- E1–E3 supported on campaign analysis.  
- Primary final-scale pack = campaign (see `results/live/FINAL3_NOTE.md`).

## Explicitly out of floor

- **P4 / TransactWriteItems** — quarantined (ASSUMPTIONS A12; not in binding experiment.yaml).  
  Dated WONTFIX: `../DATED_WONTFIX_N_Vikas_P4_2026-09-23.md`.  
- Separate lite final_1/2/3 repeats — optional beyond-floor.

## Negatives retained

P1 duplicate-risk control expected; moto ≠ AWS latency/capacity.

## Move gate

- SoT: `../CA2_PROPOSED_VS_ARTEFACT.md`  
- Audit: `scripts/audit_campaign_root_causes.py` → EXIT 0 / remediable_total=0 (2026-09-23).  
- **MOVE ALLOWED** under disclosed P1–P3 scope.
