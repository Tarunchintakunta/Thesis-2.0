# Mehak final-3 — baseline compare (local GCT)

**Date:** 2026-09-21  
**Runs:** `results/gct/final_1/`, `final_2/`, `final_3/` (each: `--dataset gct --epochs 15`, seeds 42–46)  
**CA2 floor:** still **100%** after final-3. Negative result retained.

## Accuracy (mean ± std across seeds)

| Model | final_1 | final_2 | final_3 |
|-------|--------:|--------:|--------:|
| RF (classical) | 0.9439±0.0022 | 0.9439±0.0022 | 0.9439±0.0022 |
| Aldomi GRU-RF | 0.9425±0.0006 | 0.9425±0.0006 | 0.9425±0.0006 |
| MHSA-Fused | 0.9223±0.0016 | 0.9223±0.0016 | 0.9223±0.0016 |

## Verdict (pos + neg)

- **Positive:** Classical RF and Aldomi GRU-RF lead Accuracy / Macro-F1 / Fail-F1 on the disclosed 2011 GCT subset; three independent final packs are **stable** (identical summary to reported precision).
- **Negative (retained):** MHSA-Fused does **not** beat RF or Aldomi on this subset; high FN on last-seed CMs; `net` channel is sampled CPU (not network bytes).
- Reproducibility: final_1 ≡ final_2 ≡ final_3 at summary precision → local full-scale pack closed.

## Next
Baseline/stats pack closed for Mehak. RQ/objectives/limitations/conclusions fold into STATUS / final_report from this evidence. GENAI_HANDOFF still deferred until operator requests.
