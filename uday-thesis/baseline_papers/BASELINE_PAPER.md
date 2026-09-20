# Baseline paper — Uday (CA2-mapped)

**Student folder:** `uday-thesis`  
**Citation:** Et-Tousy, Zyane & Sharif (2026) — *Adaptive QoS Management in OneM2M…* — JNSM  
**Identifier:** `doi: 10.1007/s10922-026-10071-4` (disk PDF may be Research Square preprint of VoR)

## File
- `PRESENT: EtTousy_et_al_2026_Federated_QoS_baseline.pdf`

## Problem → CA2 commitment
Centralized RF on pooled QoS telemetry achieves high offload-decision accuracy but **may not scale / guarantee privacy** in distributed IoT; FL named as future work.

## Solution (paper)
Centralized RF (+ ensembles/DL variants) on Azure IoT telemetry; MAPE-K loop; Keep-Local / Partial / Full offload.

## Gap
No federated alternative in the paper. Commitments build per-site RF ensemble without pooling raw telemetry + local-only lower bound.

## Metrics mapped to eval
| Paper / commitment | Ours (CSV) |
|--------------------|------------|
| Offload-class accuracy | Accuracy |
| Multi-class quality | Macro-F1 |
| Minority / critical class | Critical Recall (class 2) |

Evidence: `iot-reliability/results/results_summary.csv`. Absolute % will differ from Azure VoR (synthetic labels).
