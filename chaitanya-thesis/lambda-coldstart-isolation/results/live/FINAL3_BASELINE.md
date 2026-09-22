# Chaitanya final-3 baseline compare (live Init lite)

**Date:** 2026-09-22  
**Packs:** `results/live/final_1|final_2|final_3/` (sourced from completed `data/raw/live_r{13,14,15}/`)  
**Protocol:** SAM deploy `coldstart-study` → baseline + runtime_compare (H1 Init, reps=5, optimised) + burst → collect/parse/analyse → `sam delete` each round.  
**Destroy:** confirmed historically (`CHAITANYA_R{13,14,15}_DONE`); AWS Lambda count = 0 after pack.

## H1 Init Duration p50 (ms) — optimised @1024 MB, n=5 colds/runtime

| Round | python | nodejs | java | H1 reject |
|-------|-------:|-------:|-----:|-----------|
| final_1 (live_r13) | 82.8 | 146.8 | 424.7 | yes (ANOVA p≈7e-10) |
| final_2 (live_r14) | 88.9 | 146.7 | 330.0 | yes (KW p≈0.004) |
| final_3 (live_r15) | 80.2 | 141.3 | 404.8 | yes (KW p≈0.002) |

Source: `results/live/final3_init_summary.json`.

## Cost proxy (list-price sum, all phases)

| Round | total USD |
|-------|----------:|
| final_1 | ≈0.0028 |
| final_2 | ≈0.0028 |
| final_3 | ≈0.0027 |

## Verdict (pos + neg)

- **Positive:** H1 rejects on all three destroy-after rounds; java ≫ nodejs ≳ python Init (optimised) ordering stable; stacks destroyed each round; cost ≪ $0.01/round.
- **Negative/mixed:** lite n=5/cell (not confirmatory n≥30); H2 package_size / H3 warming / H4 memory not re-run in these finals (covered in initial_eval Init/H3/H4 lite under `data/processed/live/`); posthoc python↔nodejs fails Holm once (final_2).
- Finals are method-scale smoke + H1 stability, not a new Holm family on H2–H3.

**CA2 floor:** still **100%** after final-3. Soft confirmatory n remains beyond-CA2.
