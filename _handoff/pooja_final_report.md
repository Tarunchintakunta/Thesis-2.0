# Final Report: Stability-Aware Predictive Kubernetes Scaling

## Abstract
Wanigasooriya & Ekanayake (2026), "NimbusGuard: A Novel Framework for Proactive Kubernetes Autoscaling Using Deep Q-Networks" (IEEE ICOIN 2026, DOI 10.1109/ICOIN68469.2026.11480646), show a DQN+LSTM proactive autoscaler beating reactive HPA/KEDA on SLA compliance, but their own results table names the cost: NimbusGuard was "the most agile and least stable system" — highest average replica count, double the scaling events. This project reproduces that trade-off with a simpler feed-forward predictor (`AggressivePAKS`: acts immediately on every raw forecast) and builds the stability fix the paper names as future work but doesn't build (`StabilityAwarePAKS`: exponential smoothing + hysteresis/cooldown on the same predictor). Across 5 seeds: Aggressive PAKS roughly halves SLA violations vs. reactive HPA (11.0 vs. 20.0) at higher over-provisioning (45.8% vs. 40.9%); Stability-Aware PAKS cuts scaling events by 57% (384.4→165.8) and volatility by 32% (2.86→1.95) vs. Aggressive, while still beating HPA on SLA violations (18.0 vs. 20.0) — though by less than the unfiltered policy does. A genuine trade-off, reported honestly rather than as a clean win.

## 1. Introduction
See `latex_report/text/introduction.tex` for the full introduction, research question, and objectives.

## 2. Literature Review Summary
(Refers to `/latex_report/text/relatedwork.tex`.) Baseline paper: Wanigasooriya, C., Ekanayake, I. (2026). *NimbusGuard: A Novel Framework for Proactive Kubernetes Autoscaling Using Deep Q-Networks.* IEEE ICOIN 2026. DOI: 10.1109/ICOIN68469.2026.11480646 (preprint: arXiv:2604.11017). DQN+LSTM proactive autoscaler vs. reactive HPA/KEDA; names instability/over-provisioning as an explicit, unresolved trade-off.

## 3. Methodology
Synthetic cyclical workload generator (`src/data/workload_simulator.py`, 500 steps, sine-wave base + periodic spikes + noise). A scikit-learn `MLPRegressor` (replacing the original scaffold's TensorFlow model — same 2-hidden-layer design, no heavy DL dependency) forecasts next-step workload from a 10-step lookback window. `run_reactive_hpa` (baseline reactive), `run_aggressive_paks` (baseline reproduction, unfiltered proactive), `StabilityAwareController`/`run_stability_aware_paks` (improvement: EMA smoothing + hysteresis/cooldown). 5 seeds (42-46), fresh workload + predictor per seed, all 3 policies evaluated on the identical workload per seed.

## 4. Experimental Results
| Model | SLA Violations | Over-provisioning % | Scaling Events | Pod Count Volatility |
|---|---|---|---|---|
| Reactive HPA | 20.0 ± 2.7 | 40.92 ± 0.19 | 407.4 ± 4.9 | 3.32 ± 0.25 |
| Aggressive PAKS (baseline reproduction) | 11.0 ± 2.2 | 45.80 ± 2.23 | 384.4 ± 9.1 | 2.86 ± 0.36 |
| Stability-Aware PAKS (improved) | 18.0 ± 2.7 | 46.52 ± 2.16 | 165.8 ± 5.3 | 1.95 ± 0.17 |

Raw per-seed and summary CSVs: `paks-framework/results/results_per_seed.csv`, `results_summary.csv`. Reproduce with `python scripts/train_and_evaluate.py` inside `paks-framework/`.

## 5. Conclusion
The stability-aware controller substantially recovers the specific weakness NimbusGuard's own results name (agility/instability), at a partial, disclosed cost to the SLA-violation benefit that motivated proactive scaling in the first place. See `latex_report/text/conclusion.tex` for full discussion and future work (parameter sweeps, real testbed evaluation, learned cooldown policy).

## Bibliography
See `latex_report/refs.bib` (`Wanigasooriya26` entry).
