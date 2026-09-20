# Baseline paper — Vishvaksen (CA2-mapped)

**Student folder:** `vishvaksen-thesis`  
**Citation:** War et al. (2025) — *Detection of Security Smells in IaC… Semantics-Aware…*  
**Identifier:** arXiv:2509.18790 · `doi: 10.48550/arXiv.2509.18790` (preprint; venue risk)

## File
- `PRESENT: War_et_al_2025_IaC_misconfig_baseline.pdf`

## Problem → CA2 commitment
Semantics-aware ML (CodeBERT/LongFormer) loses **precision** when comments/NL context are stripped — over-flags safe IaC.

## Solution (paper)
Comment-aware transformer detectors for IaC security smells.

## Gap
Comment-ablation precision collapse. Commitments reproduce collapse on synthetic easy/hard benchmark and evaluate **hybrid rule+TF-IDF ML** (method simplification vs CodeBERT; intentional for reproducibility). Keep Rahman/GLITCH as published anchors.

## Metrics mapped to eval
| Paper | Ours (CSV) |
|-------|------------|
| Precision | Precision |
| Recall | Recall |
| F1 | F1 |

Evidence: `iac-security/results/results_summary.csv` + threshold sweep in evaluation.
