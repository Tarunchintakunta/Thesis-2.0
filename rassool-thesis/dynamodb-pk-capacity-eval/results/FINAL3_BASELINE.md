# Rasool final-3 baseline (W3/W4 live key-cells)

**Date:** 2026-09-22  
**Packs:** `results/final_1|2|3/` (each 12 cells, seed 100k, destroy-after)  
**Prefixes:** `ddbpkf1` / `ddbpkf2` / `ddbpkf3`  
**Pooled stats:** `results/pooled_final3_anova.json` (n=3/cell across fleets)

## Batches
| Round | batches.csv lines | destroy |
|-------|------------------:|---------|
| final_1 | 13 (hdr+12) | yes |
| final_2 | 13 | yes |
| final_3 | 13 | yes |

## Pooled confirmatory ANOVA (latency_mean_ms)

| Workload | Key F (p) | Capacity F (p) | Interaction F (p) |
|----------|-----------|----------------|-------------------|
| W3 | **59.00 (1e-06)** | 1.27 (0.28) | 0.21 (0.81) |
| W4 | **17.01 (0.0003)** | 0.25 (0.63) | 3.08 (0.083) |

**Demonstrated:** key-design main effect on mean latency across three independent live fleets.  
**Not demonstrated here:** capacity main effect on W3 mean latency; formal n=30 power plan; full W1–W4 confirmatory ANOVA (W1/W2 = `results/w1w2_a/` n=1 exploratory — see SoT).

## Verdict
- **Positive:** three independent live W3/W4 key-cell rounds; destroy-after; pooled Key effect significant.
- **Soft retained:** W1/W2 exploratory n=1 (`w1w2_a`); capacity/interaction ns on W3 mean latency.

**Honest CA2 floor:** **~88%** — not 100%. See `../CA2_PROPOSED_VS_ARTEFACT.md` + `scripts/audit_soft_limbs_root_causes.py` EXIT 0.
