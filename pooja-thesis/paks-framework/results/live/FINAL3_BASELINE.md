# Pooja final-3 baseline compare (live k3s HPA vs PAKS)

**Date:** 2026-09-22  
**Packs:** `results/live/final_1|final_2|final_3/`  
**Protocol:** 1× t3.micro + k3s + S3 + CW (`project=paks-k8s-live`); steps=16; seeds 41/42/43; destroy-after each round.  
**Destroy:** confirmed each round (`aws_destroy_verify.json`); EC2 leftover = none after final_3.

## Scaling latency mean (s) — LIVE kubectl Scale

| Round | HPA mean | PAKS mean | HPA p50 | PAKS p50 | n_steps |
|-------|---------:|----------:|--------:|---------:|--------:|
| final_1 | 0.334 | 0.279 | 0.141 | 0.142 | 16 |
| final_2 | 0.296 | 0.319 | 0.141 | 0.137 | 16 |
| final_3 | 0.395 | 0.312 | 0.143 | 0.145 | 16 |

Source: `results/live/final3_latency_summary.json`.

## Verdict (pos + neg)

- **Positive:** all three rounds live-apply + destroy_confirmed; p50 scale latency stable ≈0.14 s both policies; stack clean after each round.
- **Negative/mixed:** mean HPA↔PAKS ordering not monotone across rounds (PAKS faster on f1/f3, HPA on f2) — lite n=16 single-node; cost/SLA fields remain partly SIMULATED (trace/util model); not a confirmatory superiority claim.
- Finals are method-scale smoke stability, not new Holm tests on prediction MAE.

**CA2 floor:** still **100%** after final-3. Soft residuals (full dumps / multi-node) remain beyond-CA2.
