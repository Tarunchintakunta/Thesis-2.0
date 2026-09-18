import os
import sys
import time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.data.telemetry_simulator import TelemetrySimulator, TelemetryDataset, METRIC_NAMES
from src.models.mhsa_model import MHSAPerHead, MHSAFused
from src.models.baseline import ThresholdBaseline

SEEDS = [42, 43, 44, 45, 46]
SEQ_LENGTH = 10
EPOCHS = 30
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def per_metric_predictions(logits):
    # logits: (N, num_metrics, 3) -> (N, num_metrics) predicted class
    return logits.argmax(axis=-1)


def score_model(y_true, y_pred, is_transient):
    """Per-metric macro accuracy/F1 (averaged across metrics), plus recall
    on the specific failure mode the baseline paper reports: whether a
    real violation (L1/L2) inside a high-load transient window gets
    detected at all."""
    accs, f1s = [], []
    for i in range(y_true.shape[1]):
        accs.append(accuracy_score(y_true[:, i], y_pred[:, i]))
        f1s.append(f1_score(y_true[:, i], y_pred[:, i], average="macro", zero_division=0))

    transient_recalls = []
    underprediction_bias = []
    for i in range(y_true.shape[1]):
        t_true = y_true[is_transient, i]
        t_pred = y_pred[is_transient, i]
        violation_mask = t_true > 0
        if violation_mask.sum() > 0:
            transient_recalls.append((t_pred[violation_mask] > 0).mean())
            # Positive = model predicts a lower severity than what actually
            # happens (systematic underprediction, the paper's own framing).
            underprediction_bias.append((t_true[violation_mask] - t_pred[violation_mask]).mean())

    return {
        "Accuracy": round(float(np.mean(accs)), 4),
        "Macro-F1": round(float(np.mean(f1s)), 4),
        "Transient Violation Recall": round(float(np.mean(transient_recalls)), 4) if transient_recalls else float("nan"),
        "Transient Underprediction Bias": round(float(np.mean(underprediction_bias)), 4) if underprediction_bias else float("nan"),
    }


def class_weights_per_metric(y_train):
    # Inverse-frequency weights so rare L1/L2 classes aren't drowned out by
    # the dominant "none" class.
    weights = []
    for i in range(y_train.shape[1]):
        counts = np.bincount(y_train[:, i], minlength=3).astype(np.float32)
        counts[counts == 0] = 1.0
        w = counts.sum() / (3.0 * counts)
        weights.append(torch.tensor(w, dtype=torch.float32))
    return weights


def train_model(model_cls, X_train, y_train, X_test, seed):
    # Seed torch's own RNG (weight init + DataLoader shuffling) so results
    # are actually reproducible per seed -- numpy's RNG alone (used for data
    # generation) does not control any of this.
    torch.manual_seed(seed)
    model = model_cls(seq_length=SEQ_LENGTH).to(DEVICE)
    weights = [w.to(DEVICE) for w in class_weights_per_metric(y_train)]
    criteria = [nn.CrossEntropyLoss(weight=w) for w in weights]
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    train_ds = TelemetryDataset(X_train, y_train)
    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)

    model.train()
    for epoch in range(EPOCHS):
        total_loss = 0.0
        for X_batch, y_batch, _ in train_loader:
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
            optimizer.zero_grad()
            logits = model(X_batch)  # (batch, num_metrics, 3)
            loss = sum(
                criteria[i](logits[:, i, :], y_batch[:, i]) for i in range(logits.shape[1])
            )
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

    model.eval()
    with torch.no_grad():
        X_test_t = torch.FloatTensor(X_test).to(DEVICE)
        start = time.time()
        logits = model(X_test_t)
        latency_ms = (time.time() - start) * 1000 / len(X_test)
        preds = per_metric_predictions(logits.cpu().numpy())

    return model, preds, latency_ms


def main():
    print(f"Device: {DEVICE}")
    all_runs = []
    fused_model_for_export = None
    fused_model_meta = None

    for seed in SEEDS:
        print(f"\n=== Seed {seed} ===")
        sim = TelemetrySimulator(num_samples=20000, seq_length=SEQ_LENGTH, transient_ratio=0.4, seed=seed)
        X, y, is_transient = sim.generate_data()

        idx = np.arange(len(X))
        idx_train, idx_test = train_test_split(idx, test_size=0.2, random_state=seed, stratify=is_transient)
        X_train, y_train = X[idx_train], y[idx_train]
        X_test, y_test = X[idx_test], y[idx_test]
        transient_test = is_transient[idx_test]

        # Traditional reactive threshold monitoring
        baseline = ThresholdBaseline()
        start = time.time()
        baseline_preds = baseline.predict(X_test)
        baseline_latency = (time.time() - start) * 1000 / len(X_test)
        baseline_scores = score_model(y_test, baseline_preds, transient_test)
        baseline_scores.update({"Model": "Threshold Baseline", "Seed": seed, "Latency (ms)": round(baseline_latency, 4)})
        all_runs.append(baseline_scores)

        # Baseline reproduction: strict 1-head-per-metric (Thapliyal 2026)
        print("Training MHSA-PerHead (baseline reproduction)...")
        _, perhead_preds, perhead_latency = train_model(MHSAPerHead, X_train, y_train, X_test, seed)
        perhead_scores = score_model(y_test, perhead_preds, transient_test)
        perhead_scores.update({"Model": "MHSA-PerHead (baseline)", "Seed": seed, "Latency (ms)": round(perhead_latency, 4)})
        all_runs.append(perhead_scores)

        # Improvement: cross-head fusion
        print("Training MHSA-Fused (improved)...")
        fused_model, fused_preds, fused_latency = train_model(MHSAFused, X_train, y_train, X_test, seed)
        fused_scores = score_model(y_test, fused_preds, transient_test)
        fused_scores.update({"Model": "MHSA-Fused (improved)", "Seed": seed, "Latency (ms)": round(fused_latency, 4)})
        all_runs.append(fused_scores)

        fused_model_for_export = fused_model
        fused_model_meta = {"seq_length": SEQ_LENGTH, "metrics": METRIC_NAMES}

    results_df = pd.DataFrame(all_runs)
    print("\nPer-seed results:")
    print(results_df.to_string(index=False))

    metric_cols = ["Accuracy", "Macro-F1", "Transient Violation Recall", "Transient Underprediction Bias", "Latency (ms)"]
    summary = results_df.groupby("Model")[metric_cols].agg(["mean", "std"]).round(4)
    print("\nSummary across seeds (mean +/- std):")
    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(summary)

    results_dir = os.path.join(parent_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    results_df.to_csv(os.path.join(results_dir, "results_per_seed.csv"), index=False)
    summary.to_csv(os.path.join(results_dir, "results_summary.csv"))
    print(f"\nResults saved to {results_dir}/")

    if fused_model_for_export is not None:
        # Saved inside the lambda_handler dir so the SAM CodeUri packages the
        # weights alongside the handler code -- no separate model bucket/layer needed.
        model_dir = os.path.join(parent_dir, "src", "lambda_handler", "model")
        os.makedirs(model_dir, exist_ok=True)
        torch.save(fused_model_for_export.state_dict(), os.path.join(model_dir, "mhsa_fused.pt"))
        import json
        with open(os.path.join(model_dir, "metadata.json"), "w") as f:
            json.dump(fused_model_meta, f, indent=2)
        print(f"Deployable model saved to {model_dir}/mhsa_fused.pt")


if __name__ == "__main__":
    main()
