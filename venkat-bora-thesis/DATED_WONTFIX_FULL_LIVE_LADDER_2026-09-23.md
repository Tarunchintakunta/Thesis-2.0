# DATED_WONTFIX — full live EC2 order ladder 200–2000 (Venkat)

**Date:** 2026-09-23  
**Item:** Full six-point live EC2 matmul sweep at orders **200–2000** (CA2 growing-order limb beyond Free-Tier subset).  
**Disposition:** **DATED_WONTFIX** — not remediable under disclosed Free-Tier scope.

## Why closed without re-run

- Live Free-Tier size ladder **100 / 250 / 500** executed (`results/live/size_ladder_ladder1/`; destroy confirmed).
- Local Dask suite already covers **200–2000** (`results/data/summary_statistics.json`).
- DESIGN amendment: `distributed-matrix-scaling/DESIGN_RATIONALE_BEYOND_CA2.md` (2026-09-22/23).
- Scripted audit: `scripts/audit_size_ladder_root_causes.py` treats full live 200–2000 as amended-out when DESIGN present and no fabricated full-ladder artefact.

## Honesty retained

Anti-crossover on live subset (scale-up ≪ multi at every order). Do **not** invent a crossover or claim full live 200–2000 EC2 coverage.
