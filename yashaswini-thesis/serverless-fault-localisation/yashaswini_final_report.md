# Lightweight Fault Detection and Localisation in AWS Serverless Microservices

**Author:** Yashaswini Penumarthi (24262404)  
**Evidence lock:** 2026-09-20 — Leg 2 from `results/rcaeval/*`; Leg 3 lite from `results/live/overhead.json`.

## Abstract
Untrained rule-based detection + optional Isolation Forest hybrid localiser (LGGT) for cost-constrained serverless. Three-leg protocol: (1) Xing F1=0.938 citation ceiling only; (2) RCAEval vs BARO/CIRCA/TraceRCA ($n{=}90$; CausalRCA quarantined $n{=}4$, fixed-order); (3) overhead — **lite Leg 3 live AWS executed** (`results/live/overhead.json`; destroyed after).

Committed: rule F1 **0.469**, AC@3 **0.611** vs BARO/CIRCA AC@3 **0.878**. Lite policy vs full volume reduction **0.803**. **Not** competitive under joint CA2 rule (accuracy limb fails). Hybrid underperforms rules on Top-3.

## Results (evidence-locked)

| Method | $n$ | AC@1 | AC@3 | Mean rank |
|--------|----:|-----:|-----:|----------:|
| Rules | 90 | 0.289 | **0.611** | 2.98 |
| BARO | 90 | 0.144 | 0.878 | 2.32 |
| CIRCA | 90 | 0.589 | 0.878 | 2.08 |
| TraceRCA | 90 | 0.111 | 0.644 | 2.92 |
| Hybrid | 90 | 0.256 | 0.478 | 3.63 |
| CausalRCA | **4** | 0.000 | 1.000 | 3.00 |

Detection F1=0.469 (TP=90, FP=204, FN=0). CausalRCA fixed-order share=1.0 — quarantined, not peer.

### Leg 3 lite (measured)

| Condition | req | bytes/1000 | traces | median ms |
|-----------|----:|-----------:|-------:|----------:|
| full | 300 | 19 000 061 | 511 | 916.24 |
| policy | 300 | 3 739 927 | 51 | 875.63 |
| off | 300 | 1 251 573 | 0 | 917.98 |

Reduction policy vs full = **0.803**. Cost/M list-price: full ≈\$10.93; policy ≈\$2.25. Sole AWS residual **closed**.

## References
See `bib/references.bib` / `latex_report/refs.bib` (DOI `note={doi:…}`).
