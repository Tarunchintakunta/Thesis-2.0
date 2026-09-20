# CA2 Commitments (proxy) — Mehak

**Status:** Formal CA2 file **NOT FOUND** in-repo. This document is the **binding research contract** until a real CA2 is added.  
**AWS deploy:** **Not required** for research alignment (local synthetic campaign is the experiment). Lambda/SAM is packaging only — **do not deploy AWS** for this thesis under the alignment-only policy.

## Research question
Does allowing per-metric attention heads to exchange information via a cross-head fusion layer reduce systematic underprediction during high-load transients, without degrading overall prediction accuracy?

## Objectives (must evidence)
1. Reproduce Thapliyal’s strict one-head-per-metric MHSA as baseline, adapted to cluster telemetry (CPU, memory, disk, network).
2. Synthetic telemetry with genuine forecasting task + cross-metric burst precursors.
3. Confirm underprediction pattern on that benchmark.
4. Evaluate cross-head fusion across multiple seeds; report targeted metrics honestly (including non-wins).

## Baseline
Thapliyal (2026), arXiv:2605.05354 (ICDCS 2026 acceptance claim). DOI note: `doi: 10.48550/arXiv.2605.05354`. PDF under `baseline_papers/`.

## Variables / metrics (eval↔CSV)
| Metric | Artefact |
|--------|----------|
| Accuracy, Macro-F1 | `mhsa-tdl-framework/results/results_summary.csv` |
| Transient Violation Recall | same |
| Transient Underprediction Bias | same |
| Seeds | 42–46 (`results_per_seed.csv`) |

## Non-goals (honest)
- Live AWS / Kinesis / Lambda inference campaign
- Real Borg/IBM cluster traces
- Claiming statistical significance when Δ < 1σ across seeds
