# Baseline paper — Mehak (CA2-mapped)

**Student folder:** `mehak-thesis`  
**Citation:** Thapliyal (2026) — *A Multi-Head Attention Approach for SLA Compliance Monitoring in Data Centers*  
**Identifier:** arXiv:2605.05354 · `doi: 10.48550/arXiv.2605.05354` (ICDCS 2026 acceptance claim; prefer VoR when available)

## File
- `PRESENT: Thapliyal_2026_MHSA_SLA_baseline.pdf`

## Problem → CA2 commitment
Colocation/SLA MHSA with **strict one-head-per-metric** underpredicts volatile metrics during correlated transients because heads do not share information.

## Solution (paper)
Per-entity multi-head transformer; one head per telemetry rule; proactive violation prediction.

## Gap (paper’s own / adapted)
Underprediction during high-load transients; no cross-head exchange. Commitments adapt colo SLA → **cluster telemetry** and test a **cross-head fusion** fix.

## Metrics mapped to eval
| Paper / commitment metric | Ours (CSV) |
|---------------------------|------------|
| Prediction accuracy | Accuracy |
| Class quality | Macro-F1 |
| Transient anticipation | Transient Violation Recall |
| Severity underprediction | Transient Underprediction Bias |

Evidence: `mhsa-tdl-framework/results/results_summary.csv` (seeds 42–46).
