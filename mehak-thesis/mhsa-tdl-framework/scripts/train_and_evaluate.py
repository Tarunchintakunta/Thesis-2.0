"""Train/evaluate MHSA-TDL artefact.

Default dataset = synthetic (artefact-as-built). Formal CA2 requires Google
Cluster Trace: pass `--dataset gct` only when DATA_GAPS files are present;
that path refuses to invent windows.
"""

from __future__ import annotations

import argparse
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
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.data.telemetry_simulator import TelemetrySimulator, TelemetryDataset, METRIC_NAMES
from src.data.gct_loader import require_gct, load_gct_windows
from src.models.mhsa_model import MHSAPerHead, MHSAFused
from src.models.baseline import ThresholdBaseline
from src.models.classical_baselines import run_classical_baselines

SEEDS = [42, 43, 44, 45, 46]
SEQ_LENGTH = 10
EPOCHS = 30
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def per_metric_predictions(logits):
    return logits.argmax(axis=-1)


def _softmax(logits, axis=-1):
    z = logits - logits.max(axis=axis, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=axis, keepdims=True)


def score_model(y_true, y_pred, is_transient, y_score=None):
    """Artefact metrics + formal CA2 suite (Acc/Prec/Rec/F1/ROC-AUC).

    Formal metrics are macro-averaged over metrics then classes where applicable.
    ROC-AUC uses one-vs-rest on provided score tensor (N, metrics, 3). When
    scores are unavailable (e.g. hard threshold baseline), ROC-AUC is NaN.
    """
    accs, f1s, precs, recs, aucs = [], [], [], [], []
    for i in range(y_true.shape[1]):
        yt, yp = y_true[:, i], y_pred[:, i]
        accs.append(accuracy_score(yt, yp))
        f1s.append(f1_score(yt, yp, average="macro", zero_division=0))
        precs.append(precision_score(yt, yp, average="macro", zero_division=0))
        recs.append(recall_score(yt, yp, average="macro", zero_division=0))
        if y_score is not None:
            try:
                # Need ≥2 classes present in y_true for OVR AUC
                if len(np.unique(yt)) >= 2:
                    aucs.append(
                        roc_auc_score(yt, y_score[:, i, :], multi_class="ovr", average="macro")
                    )
            except ValueError:
                pass

    transient_recalls = []
    underprediction_bias = []
    for i in range(y_true.shape[1]):
        t_true = y_true[is_transient, i]
        t_pred = y_pred[is_transient, i]
        violation_mask = t_true > 0
        if violation_mask.sum() > 0:
            transient_recalls.append((t_pred[violation_mask] > 0).mean())
            underprediction_bias.append((t_true[violation_mask] - t_pred[violation_mask]).mean())

    return {
        "Accuracy": round(float(np.mean(accs)), 4),
        "Precision": round(float(np.mean(precs)), 4),
        "Recall": round(float(np.mean(recs)), 4),
        "Macro-F1": round(float(np.mean(f1s)), 4),
        "ROC-AUC": round(float(np.mean(aucs)), 4) if aucs else float("nan"),
        "Transient Violation Recall": round(float(np.mean(transient_recalls)), 4) if transient_recalls else float("nan"),
        "Transient Underprediction Bias": round(float(np.mean(underprediction_bias)), 4) if underprediction_bias else float("nan"),
    }


def class_weights_per_metric(y_train):
    weights = []
    for i in range(y_train.shape[1]):
        counts = np.bincount(y_train[:, i], minlength=3).astype(np.float32)
        counts[counts == 0] = 1.0
        w = counts.sum() / (3.0 * counts)
        weights.append(torch.tensor(w, dtype=torch.float32))
    return weights


def train_model(model_cls, X_train, y_train, X_test, seed):
    torch.manual_seed(seed)
    model = model_cls(seq_length=SEQ_LENGTH).to(DEVICE)
    weights = [w.to(DEVICE) for w in class_weights_per_metric(y_train)]
    criteria = [nn.CrossEntropyLoss(weight=w) for w in weights]
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    train_ds = TelemetryDataset(X_train, y_train)
    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)

    model.train()
    for epoch in range(EPOCHS):
        for X_batch, y_batch, _ in train_loader:
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
            optimizer.zero_grad()
            logits = model(X_batch)
            loss = sum(
                criteria[i](logits[:, i, :], y_batch[:, i]) for i in range(logits.shape[1])
            )
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        X_test_t = torch.FloatTensor(X_test).to(DEVICE)
        start = time.time()
        logits = model(X_test_t)
        latency_ms = (time.time() - start) * 1000 / len(X_test)
        logits_np = logits.cpu().numpy()
        preds = per_metric_predictions(logits_np)
        scores = _softmax(logits_np, axis=-1)

    return model, preds, scores, latency_ms


def load_dataset(dataset: str, seed: int):
    if dataset == "gct":
        require_gct()
        # Will raise NotImplementedError until join is reviewed — intentional.
        return load_gct_windows(seq_length=SEQ_LENGTH)
    if dataset != "synthetic":
        raise ValueError(f"Unknown dataset {dataset!r}; use 'synthetic' or 'gct'")
    sim = TelemetrySimulator(num_samples=20000, seq_length=SEQ_LENGTH, transient_ratio=0.4, seed=seed)
    return sim.generate_data()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        choices=["synthetic", "gct"],
        default="synthetic",
        help="synthetic = artefact-as-built; gct = formal CA2 (requires DATA_GAPS files)",
    )
    parser.add_argument(
        "--skip-classical",
        action="store_true",
        help="Skip RF/KNN/SVM classical monitors",
    )
    args = parser.parse_args()

    if args.dataset == "gct":
        # Fail fast with checklist — do not invent GCT results.
        require_gct()

    print(f"Device: {DEVICE}")
    print(f"Dataset: {args.dataset}  (formal CA2 requires gct; synthetic is artefact-only)")
    all_runs = []
    fused_model_for_export = None
    fused_model_meta = None

    for seed in SEEDS:
        print(f"\n=== Seed {seed} ===")
        X, y, is_transient = load_dataset(args.dataset, seed)

        idx = np.arange(len(X))
        idx_train, idx_test = train_test_split(idx, test_size=0.2, random_state=seed, stratify=is_transient)
        X_train, y_train = X[idx_train], y[idx_train]
        X_test, y_test = X[idx_test], y[idx_test]
        transient_test = is_transient[idx_test]

        baseline = ThresholdBaseline()
        start = time.time()
        baseline_preds = baseline.predict(X_test)
        baseline_latency = (time.time() - start) * 1000 / len(X_test)
        baseline_scores = score_model(y_test, baseline_preds, transient_test, y_score=None)
        baseline_scores.update({"Model": "Threshold Baseline", "Seed": seed, "Latency (ms)": round(baseline_latency, 4)})
        all_runs.append(baseline_scores)

        if not args.skip_classical:
            print("Fitting classical RF/KNN/SVM monitors...")
            for name, (preds, scores, lat) in run_classical_baselines(X_train, y_train, X_test).items():
                s = score_model(y_test, preds, transient_test, y_score=scores)
                s.update({"Model": name, "Seed": seed, "Latency (ms)": round(lat, 4)})
                all_runs.append(s)
                print(f"  {name}: Acc={s['Accuracy']} F1={s['Macro-F1']} AUC={s['ROC-AUC']}")

        print("Training MHSA-PerHead (artefact baseline)...")
        _, perhead_preds, perhead_score, perhead_latency = train_model(MHSAPerHead, X_train, y_train, X_test, seed)
        perhead_scores = score_model(y_test, perhead_preds, transient_test, y_score=perhead_score)
        perhead_scores.update({"Model": "MHSA-PerHead (baseline)", "Seed": seed, "Latency (ms)": round(perhead_latency, 4)})
        all_runs.append(perhead_scores)

        print("Training MHSA-Fused (improved)...")
        fused_model, fused_preds, fused_score, fused_latency = train_model(MHSAFused, X_train, y_train, X_test, seed)
        fused_scores = score_model(y_test, fused_preds, transient_test, y_score=fused_score)
        fused_scores.update({"Model": "MHSA-Fused (improved)", "Seed": seed, "Latency (ms)": round(fused_latency, 4)})
        all_runs.append(fused_scores)

        fused_model_for_export = fused_model
        fused_model_meta = {"seq_length": SEQ_LENGTH, "metrics": METRIC_NAMES, "dataset": args.dataset}

    results_df = pd.DataFrame(all_runs)
    print("\nPer-seed results:")
    print(results_df.to_string(index=False))

    metric_cols = [
        "Accuracy", "Precision", "Recall", "Macro-F1", "ROC-AUC",
        "Transient Violation Recall", "Transient Underprediction Bias", "Latency (ms)",
    ]
    summary = results_df.groupby("Model")[metric_cols].agg(["mean", "std"]).round(4)
    print("\nSummary across seeds (mean +/- std):")
    with pd.option_context("display.max_columns", None, "display.width", 220):
        print(summary)

    results_dir = os.path.join(parent_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    # Keep prior proxy CSVs; write formal-suite columns to new + updated summary
    results_df.to_csv(os.path.join(results_dir, "results_per_seed.csv"), index=False)
    summary.to_csv(os.path.join(results_dir, "results_summary.csv"))
    # Honest provenance note for formal alignment readers
    with open(os.path.join(results_dir, "RESULTS_PROVENANCE.md"), "w") as f:
        f.write(
            "# Results provenance\n\n"
            f"- Dataset flag used for this CSV: **{args.dataset}**\n"
            "- Formal CA2 requires **Google Cluster Trace** (`--dataset gct`).\n"
            "- If dataset is `synthetic`, these numbers are **artefact-as-built only** "
            "and do **not** close the GCT residual (see `../../DATA_GAPS.md`).\n"
            "- Formal metric suite columns present: Accuracy, Precision, Recall, "
            "Macro-F1, ROC-AUC, Latency (ms).\n"
            "- Classical RF/KNN/SVM rows are scaffold monitors on the same feature "
            "matrix; Aldomi hybrid reproduction still needs GCT feature schemas.\n"
        )
    print(f"\nResults saved to {results_dir}/")

    if fused_model_for_export is not None and args.dataset == "synthetic":
        model_dir = os.path.join(parent_dir, "src", "lambda_handler", "model")
        os.makedirs(model_dir, exist_ok=True)
        torch.save(fused_model_for_export.state_dict(), os.path.join(model_dir, "mhsa_fused.pt"))
        import json
        with open(os.path.join(model_dir, "metadata.json"), "w") as f:
            json.dump(fused_model_meta, f, indent=2)
        print(f"Deployable model saved to {model_dir}/mhsa_fused.pt")


if __name__ == "__main__":
    main()
