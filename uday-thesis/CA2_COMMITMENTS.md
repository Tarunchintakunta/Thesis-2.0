# CA2 Commitments (proxy) — Uday

**Status:** Formal CA2 file **NOT FOUND** in-repo. This document is the **binding research contract** until a real CA2 is added.  
**AWS deploy:** **Not required** for research alignment (local synthetic multi-site QoS campaign). Lambda/SAM is packaging only — **do not deploy AWS**.

## Research question
Can a federated learning alternative — training one model per IoT site on local data only and combining without pooling raw telemetry — recover most of the accuracy of the centralized RF baseline?

## Objectives (must evidence)
1. Reproduce centralized Random Forest + SMOTE-style class handling on synthetic non-IID sites.
2. Build federated ensemble alternative (paper’s named future work).
3. Quantify single-site local-only lower bound.
4. Evaluate all three arms on the same held-out pooled test set across seeds.

## Baseline
Et-Tousy, Zyane & Sharif (2026), JNSM. DOI `10.1007/s10922-026-10071-4`. Disk PDF may be Research Square preprint of VoR — keep DOI; prefer publisher PDF when available.

## Variables / metrics (eval↔CSV)
| Metric | Artefact |
|--------|----------|
| Accuracy, Macro-F1 | `iot-reliability/results/results_summary.csv` |
| Critical Recall (class 2) | same |
| Seeds | 42–46 (`results_per_seed.csv`) |

## Non-goals (honest)
- Live OneM2M / Azure IoT telemetry
- Live AWS SAM deploy
- Cryptographic secure aggregation / DP
- Absolute accuracy matching paper’s Azure numbers (synthetic labelling is easier)
