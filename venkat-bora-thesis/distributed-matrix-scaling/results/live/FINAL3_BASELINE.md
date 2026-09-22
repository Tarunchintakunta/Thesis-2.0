# Venkat final-3 baseline (matched Free-Tier EC2)

**Date:** 2026-09-21  
**Packs:** `results/live/final_1|2|3/` (+ `initial_eval_1/`)  
**Topology:** 1× t3.small vs 2× t3.micro; n=250; destroy-after each.

## Multi-instance da.matmul elapsed_s

| Round | status | elapsed_s |
|-------|--------|----------:|
| initial_eval_1 | ok | 0.2737 |
| final_1 | ok | 0.2480 |
| final_2 | ok | 0.2517 |
| final_3 | ok | 0.2484 |

## Verdict (pos + neg)
- **Positive:** multi-instance matmul **ok** on all three finals; destroy confirmed (0 running project instances).
- **Negative/soft:** single-shot n=250; not a full multi-order sweep; peak RSS not instrumented on EC2.

**CA2 floor:** still **100%** after final-3.
