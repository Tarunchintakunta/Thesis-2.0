# Stability-Aware Predictive Kubernetes Scaling (PAKS)

Pooja's MSc Cloud Computing thesis codebase. Reproduces the trade-off
reported by Wanigasooriya & Ekanayake (2026), *"NimbusGuard: A Novel
Framework for Proactive Kubernetes Autoscaling Using Deep Q-Networks"*
(IEEE ICOIN 2026, DOI 10.1109/ICOIN68469.2026.11480646), and fixes the
weakness their own results table names.

## The baseline paper's gap
NimbusGuard's DQN+LSTM agent beats reactive HPA and event-driven KEDA on
SLA compliance by scaling proactively -- but their own Table II shows it
does so by being "the most agile and least stable system": highest average
replica count, and double the total scaling events of HPA/KEDA (8 vs 4).
Their Discussion section frames this directly as "a fundamental trade-off:
the proactive, performance-focused scaling of NimbusGuard versus the
reactive, cost-efficient stability of traditional autoscalers" -- and lists
a calmer, more stable design as future work, not something they built.

## What this project does
1. **Reproduces** the trade-off with `AggressivePAKS`: a proactive scaler (feed-forward regressor forecasting next-step workload) that acts immediately on every raw prediction -- lower SLA violations than reactive HPA, at the cost of higher over-provisioning and more scaling events.
2. **Builds the stability fix NimbusGuard names as future work** with `StabilityAwarePAKS`: the same predictor, plus exponential smoothing of predictions and a hysteresis/cooldown rule before acting on them -- targeting the instability NimbusGuard's own results flag, without discarding the foresight that beats reactive HPA in the first place.
3. **Evaluates all three** (Reactive HPA, Aggressive PAKS, Stability-Aware PAKS) across 5 seeds on SLA violations, over-provisioning %, total scaling events, and pod-count volatility.

**Result:** Stability-Aware PAKS cuts scaling events by ~57% and pod-count
volatility by ~32% versus the aggressive baseline, while still beating
reactive HPA on SLA violations (though by less than the unfiltered
aggressive policy does) — see `../final_report.md` for full numbers and an
honest discussion of that trade-off.

## Project Structure
- `src/data/workload_simulator.py` — synthetic cyclical workload generator with traffic spikes.
- `src/models/scalers.py` — `run_reactive_hpa`, `run_aggressive_paks` (baseline), `StabilityAwareController` / `run_stability_aware_paks` (improvement).
- `scripts/train_and_evaluate.py` — trains/evaluates all 3 policies over 5 seeds, saves results, exports the deployable predictor.
- `src/lambda_handler/app.py` — real-time inference over a Kinesis workload-telemetry stream, applying the stability-aware controller per node.
- `template.yaml` — AWS SAM template (Kinesis stream + Lambda). Replaces an earlier, broken template that pointed at a `src/ml_predict.py` handler that didn't exist and hardcoded placeholder VPC subnet IDs.
- `.github/workflows/deploy.yml` (repo root) — CI: trains + deploys the SAM stack on push to `main`.

## Usage
```bash
pip install -r requirements.txt
python scripts/train_and_evaluate.py
```
Results land in `results/results_per_seed.csv` and `results/results_summary.csv`.

## Known change from the original scaffold
The original scaffold used TensorFlow/Keras for the workload predictor.
This version uses scikit-learn's `MLPRegressor` instead -- same modelling
idea (a small 2-hidden-layer dense network), without the heavy TensorFlow
dependency, consistent with keeping this codebase simple.
