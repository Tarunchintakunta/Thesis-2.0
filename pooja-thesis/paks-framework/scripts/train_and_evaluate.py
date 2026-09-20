"""PROXY driver (synthetic MLP / NimbusGuard-framed policies).

Formal PAKS: ``scripts/train_lstm_and_evaluate.py``. Do not treat this CSV
as MAE/RMSE, cost, or live Kubernetes evidence.
"""
import os
import sys
import numpy as np
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.data.workload_simulator import generate_workload, calculate_desired_pods, POD_CAPACITY
from src.models.scalers import train_predictor, run_reactive_hpa, run_aggressive_paks, run_stability_aware_paks

SEEDS = [42, 43, 44, 45, 46]
SIMULATION_STEPS = 500


def evaluate(workload, pods):
    absolute_min_required = np.ceil(workload / POD_CAPACITY)
    sla_violations = int(np.sum(pods < absolute_min_required))

    target_pods = calculate_desired_pods(workload, 1.0)
    overprovisioning_pct = float(np.sum(pods - target_pods) / np.sum(target_pods) * 100)

    diffs = np.diff(pods)
    scaling_events = int(np.sum(diffs != 0))
    pod_volatility = float(np.std(diffs))

    return {
        "SLA Violations": sla_violations,
        "Over-provisioning %": round(overprovisioning_pct, 2),
        "Scaling Events": scaling_events,
        "Pod Count Volatility (std)": round(pod_volatility, 4),
    }


def main():
    print("PROXY mode: synthetic MLP vs HPA (NimbusGuard-framed). Not formal CA2.")
    all_runs = []
    exported_model = None

    for seed in SEEDS:
        print(f"\n=== Seed {seed} ===")
        workload = generate_workload(SIMULATION_STEPS, seed=seed)

        print("Training workload predictor...")
        predictor = train_predictor(workload, seed=seed)

        hpa_pods = run_reactive_hpa(workload)
        hpa_scores = evaluate(workload, hpa_pods)
        hpa_scores.update({"Model": "Reactive HPA", "Seed": seed})
        all_runs.append(hpa_scores)

        aggressive_pods = run_aggressive_paks(workload, predictor)
        aggressive_scores = evaluate(workload, aggressive_pods)
        aggressive_scores.update({"Model": "Aggressive PAKS (baseline)", "Seed": seed})
        all_runs.append(aggressive_scores)

        stable_pods = run_stability_aware_paks(workload, predictor)
        stable_scores = evaluate(workload, stable_pods)
        stable_scores.update({"Model": "Stability-Aware PAKS (improved)", "Seed": seed})
        all_runs.append(stable_scores)

        exported_model = predictor

    results_df = pd.DataFrame(all_runs)
    print("\nPer-seed results:")
    print(results_df.to_string(index=False))

    metric_cols = ["SLA Violations", "Over-provisioning %", "Scaling Events", "Pod Count Volatility (std)"]
    summary = results_df.groupby("Model")[metric_cols].agg(["mean", "std"]).round(4)
    print("\nSummary across seeds (mean +/- std):")
    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(summary)

    results_dir = os.path.join(parent_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    results_df.to_csv(os.path.join(results_dir, "results_per_seed.csv"), index=False)
    summary.to_csv(os.path.join(results_dir, "results_summary.csv"))
    print(f"\nResults saved to {results_dir}/")

    if exported_model is not None:
        import joblib
        model_dir = os.path.join(parent_dir, "src", "lambda_handler", "model")
        os.makedirs(model_dir, exist_ok=True)
        joblib.dump(exported_model, os.path.join(model_dir, "workload_predictor.joblib"))
        print(f"Deployable predictor saved to {model_dir}/workload_predictor.joblib")


if __name__ == "__main__":
    main()
