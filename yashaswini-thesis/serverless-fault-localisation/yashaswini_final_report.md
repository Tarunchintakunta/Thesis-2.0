# Lightweight Fault Detection and Localisation in AWS Serverless Microservices

**Author:** Yashaswini Penumarthi (24262404)  
**Evidence lock:** 2026-09-20 — numbers match `results/rcaeval/{summary.md,localisation.csv,detection.json}` only.

## Abstract
Untrained rule-based detection + optional Isolation Forest hybrid localiser (LGGT) for cost-constrained serverless. Three-leg protocol: (1) Xing F1=0.938 citation ceiling only; (2) RCAEval vs BARO/CIRCA/TraceRCA ($n{=}90$; CausalRCA quarantined $n{=}4$, fixed-order); (3) overhead — **Leg 3 live AWS not executed**.

Committed: rule F1 **0.469**, AC@3 **0.611** vs BARO/CIRCA AC@3 **0.878**. **Not** competitive under CA2 decision rule. Hybrid underperforms rules on Top-3. Overhead estimator-only.

## Results (evidence-locked)

| Method | $n$ | AC@1 | AC@3 | Mean rank |
|--------|----:|-----:|-----:|----------:|
| Rules | 90 | 0.289 | **0.611** | 2.98 |
| BARO | 90 | 0.144 | 0.878 | 2.32 |
| CIRCA | 90 | 0.589 | 0.878 | 2.08 |
| TraceRCA | 90 | 0.111 | 0.644 | 2.92 |
| Hybrid | 90 | 0.256 | 0.478 | 3.63 |
| CausalRCA | **4** | 0.000 | 1.000 | 3.00 |

Detection F1=0.469 (TP=90, FP=204, FN=0). CausalRCA fixed-order share=1.0 — quarantined, not peer. Sole hard residual: **live Leg 3 AWS**.

## References
See `bib/references.bib` / `latex_report/refs.bib` (DOI `note={doi:…}`).
