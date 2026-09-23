# Design rationale — beyond CA2 (Venkat)

**Updated:** 2026-09-23  
**Authority:** `CA2_ALIGNMENT_SCOREBOARD.md` (~85 honest). Do **not** market ALIGNMENT=100.

## Floor (met)

- Matched Free-Tier scale-up vs scale-out (1× t3.small vs 2× t3.micro).  
- Live time finals + RSS/CPU packs + size ladder lite (100/250/500).  
- Anti-crossover retained (honest): scale-out not automatically faster at small n.

## Dated scope note (2026-09-22/23)

Live six-point order set **200–2000** is **not** required once Free-Tier subset + local full ladder are disclosed. Soft: Holm polish / DOI notes.  
**DATED_WONTFIX:** `../DATED_WONTFIX_FULL_LIVE_LADDER_2026-09-23.md`. Audit: `scripts/audit_size_ladder_root_causes.py`.

## Negatives retained

Single-shot n and historical timeouts on larger n — do not invent crossover wins.
