# Final Report: Cross-Head Fusion for Multi-Head Attention Cluster Telemetry Monitoring

## Abstract
Cluster health monitoring traditionally relies on reactive threshold rules that only flag a problem after a metric has already crossed its limit. Thapliyal (2026), "A Multi-Head Attention Approach for SLA Compliance Monitoring in Data Centers" (arXiv:2605.05354, IEEE ICDCS 2026), proposes a proactive alternative for data-center SLA monitoring: a per-entity transformer with one attention head dedicated to each telemetry metric, predicting violations ahead of time. That paper reports a specific weakness: its most volatile metric's head systematically underpredicts severity during high-load transients, because heads never exchange information with one another. This project reproduces that strict one-head-per-metric architecture as a baseline for cluster telemetry (CPU, memory, disk, network), confirms the same underprediction pattern on synthetic telemetry with injected cross-metric burst precursors, and evaluates a cross-head fusion layer as a fix. Across 5 properly-seeded training runs, fusion gives a small, directionally consistent improvement on the targeted gap (transient recall 86.4%→88.4%, underprediction bias 0.290→0.273) at a marginal accuracy cost (87.3%→86.3%), none of which exceed one standard deviation — a real but modest result.

## 1. Introduction
See `latex_report/text/introduction.tex` for the full introduction, research question, and objectives.

Research question: does a cross-head fusion layer reduce the systematic underprediction Thapliyal (2026) reports for strictly independent per-metric attention heads during high-load transients, without degrading overall accuracy?

## 2. Literature Review Summary
(Refers to `/latex_report/text/relatedwork.tex`.) Baseline paper: Thapliyal, O. (2026). *A Multi-Head Attention Approach for SLA Compliance Monitoring in Data Centers.* arXiv:2605.05354, accepted at the 46th IEEE ICDCS. Per-customer transformer with one attention head per SLA rule (power/temperature/humidity), predicting None/L1/L2 violations 30 minutes ahead. Reports systematic underprediction on the power head during high-load transients, attributed to heads never sharing information.

## 3. Methodology
Synthetic multivariate telemetry generator (`src/data/telemetry_simulator.py`): 10-step history window (model input) + 5-step future window (label only, never shown to the model) — a genuine forecasting task. 40% of samples contain a correlated burst: a primary metric spikes mostly in the future window, with a "rider" metric leading it by 3-6 steps inside the visible history — so predicting some future violations requires reading a *different* metric's precursor. Two models share a temporal backbone (linear embed + positional encoding + self-attention + FFN); `MHSAPerHead` splits into 4 independent per-metric heads/classifiers (baseline reproduction); `MHSAFused` adds a cross-head self-attention layer between the heads and their classifiers (the improvement). Trained with Adam, 30 epochs, inverse-frequency class weighting, 5 seeds (42-46), both data generation and model training (weight init + batch shuffling) fully seeded for reproducibility.

## 4. Experimental Results
| Model | Accuracy | Macro-F1 | Transient Recall | Underprediction Bias |
|---|---|---|---|---|
| Threshold Baseline (reactive) | 0.847 ± 0.002 | 0.313 ± 0.002 | 0.025 ± 0.002 | 1.715 ± 0.011 |
| MHSA-PerHead (baseline reproduction) | 0.873 ± 0.011 | 0.565 ± 0.008 | 0.864 ± 0.022 | 0.290 ± 0.076 |
| MHSA-Fused (improved) | 0.863 ± 0.014 | 0.560 ± 0.010 | 0.884 ± 0.021 | 0.273 ± 0.050 |

Raw per-seed and summary CSVs: `mhsa-tdl-framework/results/results_per_seed.csv`, `results_summary.csv`. Reproduce with `python scripts/train_and_evaluate.py` inside `mhsa-tdl-framework/`.

An earlier, unseeded version of this experiment showed a ~20% bias reduction from fusion; that did not replicate once torch's RNG was properly seeded per run, and is called out explicitly in `latex_report/text/evaluation.tex` as an artefact rather than a real effect.

## 5. Conclusion
Both attention models strongly beat reactive threshold monitoring at anticipating violations ahead of time (86-88% vs. 2.5% recall), confirming the baseline paper's core premise transfers to cluster telemetry. Cross-head fusion produces a real but modest, statistically inconclusive-at-n=5 improvement on the specific gap the baseline paper reports, at a small accuracy cost. Future work: real cluster trace data, an asymmetric loss penalising underprediction directly, and a richer burst-pattern vocabulary. See `latex_report/text/conclusion.tex`.

## Bibliography
See `latex_report/refs.bib` (`Thapliyal26` entry).
