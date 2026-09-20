"""Train/evaluate MHSA-TDL artefact.

Default dataset = synthetic (artefact-as-built). Formal CA2 requires Google
Cluster Trace: pass `--dataset gct` only when DATA_GAPS files are present;
that path refuses to invent windows.
"""

from __future__ import annotations

import argparse
import json
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
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.data.telemetry_simulator import TelemetrySimulator, TelemetryDataset, METRIC_NAMES
from src.data.gct_loader import GCT_METRIC_NAMES, load_gct_bundle, require_gct
import src.data.gct_loader as gct_loader_mod
from src.models.mhsa_model import MHSAPerHead, MHSAFused
from src.models.baseline import ThresholdBaseline
from src.models.classical_baselines import run_classical_baselines
from src.models.aldomi_hybrid import run_aldomi_hybrid

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


def score_binary_failure(y_true, y_pred, y_score=None):
    """Cluster-unhealthy = any head class > 0 (EVICT or FAIL)."""
    yt = (y_true.max(axis=1) > 0).astype(np.int64)
    yp = (y_pred.max(axis=1) > 0).astype(np.int64)
    out = {
        "Fail-Accuracy": round(float(accuracy_score(yt, yp)), 4),
        "Fail-Precision": round(float(precision_score(yt, yp, zero_division=0)), 4),
        "Fail-Recall": round(float(recall_score(yt, yp, zero_division=0)), 4),
        "Fail-F1": round(float(f1_score(yt, yp, zero_division=0)), 4),
        "Fail-ROC-AUC": float("nan"),
    }
    if y_score is not None and len(np.unique(yt)) >= 2:
        p_unhealthy = 1.0 - y_score[:, :, 0].mean(axis=1)
        try:
            out["Fail-ROC-AUC"] = round(float(roc_auc_score(yt, p_unhealthy)), 4)
        except ValueError:
            pass
    return out


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

    out = {
        "Accuracy": round(float(np.mean(accs)), 4),
        "Precision": round(float(np.mean(precs)), 4),
        "Recall": round(float(np.mean(recs)), 4),
        "Macro-F1": round(float(np.mean(f1s)), 4),
        "ROC-AUC": round(float(np.mean(aucs)), 4) if aucs else float("nan"),
        "Transient Violation Recall": round(float(np.mean(transient_recalls)), 4) if transient_recalls else float("nan"),
        "Transient Underprediction Bias": round(float(np.mean(underprediction_bias)), 4) if underprediction_bias else float("nan"),
    }
    out.update(score_binary_failure(y_true, y_pred, y_score))
    return out


def class_weights_per_metric(y_train):
    weights = []
    for i in range(y_train.shape[1]):
        counts = np.bincount(y_train[:, i], minlength=3).astype(np.float32)
        counts[counts == 0] = 1.0
        w = counts.sum() / (3.0 * counts)
        weights.append(torch.tensor(w, dtype=torch.float32))
    return weights


def train_model(model_cls, X_train, y_train, X_test, seed, epochs, seq_length):
    torch.manual_seed(seed)
    model = model_cls(seq_length=seq_length).to(DEVICE)
    weights = [w.to(DEVICE) for w in class_weights_per_metric(y_train)]
    criteria = [nn.CrossEntropyLoss(weight=w) for w in weights]
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    train_ds = TelemetryDataset(X_train, y_train)
    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)

    model.train()
    for epoch in range(epochs):
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


def _split(X, y, is_transient, seed):
    idx = np.arange(len(X))
    strat = is_transient
    if len(np.unique(strat)) < 2 or np.bincount(strat.astype(np.int64)).min() < 2:
        strat = None
    idx_train, idx_test = train_test_split(idx, test_size=0.2, random_state=seed, stratify=strat)
    return (
        X[idx_train],
        y[idx_train],
        X[idx_test],
        y[idx_test],
        is_transient[idx_test],
        idx_train,
        idx_test,
    )


def _write_provenance(results_dir, dataset, extra_lines):
    os.makedirs(results_dir, exist_ok=True)
    body = [
        "# Results provenance\n",
        f"- Dataset flag used for this CSV: **{dataset}**\n",
        "- Formal CA2 requires **Google Cluster Trace** (`--dataset gct`).\n",
        "- If dataset is `synthetic`, these numbers are **artefact-as-built only** "
        "and do **not** close the GCT residual (see `../../DATA_GAPS.md`).\n",
        "- Formal metric suite columns present: Accuracy, Precision, Recall, "
        "Macro-F1, ROC-AUC, Latency (ms), plus Fail-* binary (EVICT∪FAIL vs healthy).\n",
        "- Classical RF/KNN/SVM rows are scaffold monitors on the same feature matrix.\n",
        "- Aldomi path is SelectKBest + GRU extractor + RF/KNN (paper family; not a hyperparameter clone).\n",
        "- 2011 `net` channel is sampled CPU, **not** network bytes (`CHANNEL_HONESTY.md`).\n",
    ]
    body.extend(extra_lines)
    path = os.path.join(results_dir, "RESULTS_PROVENANCE.md")
    with open(path, "w") as f:
        f.writelines(body)


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
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--max-windows", type=int, default=12000)
    parser.add_argument("--skip-aldomi", action="store_true")
    args = parser.parse_args()

    epochs = args.epochs if args.epochs is not None else (20 if args.dataset == "gct" else EPOCHS)

    gct_bundle = None
    if args.dataset == "gct":
        require_gct()
        print("Loading GCT windows (task_usage ↔ task_events join)...")
        gct_bundle = load_gct_bundle(
            seq_length=SEQ_LENGTH, horizon=5, max_windows=args.max_windows, seed=42
        )
        X_gct, y_gct, fail_gct = gct_bundle["X"], gct_bundle["y"], gct_bundle["is_transient"]
        print(
            f"GCT X={X_gct.shape} Xe={gct_bundle['X_expanded'].shape} "
            f"fail_rate={fail_gct.mean():.4f} "
            f"classes={np.bincount(y_gct[:, 0], minlength=3).tolist()} "
            f"net_is_bytes={gct_loader_mod.LAST_LOAD_META.get('net_channel_is_network_bytes')} "
            f"meta={gct_loader_mod.LAST_LOAD_META}"
        )

    print(f"Device: {DEVICE}")
    print(f"Dataset: {args.dataset}  (formal CA2 requires gct; synthetic is artefact-only)")
    all_runs = []
    fused_model_for_export = None
    fused_model_meta = None
    last_fused_cm = None
    last_aldomi_cm = None

    for seed in SEEDS:
        print(f"\n=== Seed {seed} ===")
        if args.dataset == "gct":
            X, y, is_transient = gct_bundle["X"], gct_bundle["y"], gct_bundle["is_transient"]
            X_exp = gct_bundle["X_expanded"]
        else:
            sim = TelemetrySimulator(
                num_samples=20000, seq_length=SEQ_LENGTH, transient_ratio=0.4, seed=seed
            )
            X, y, is_transient = sim.generate_data()
            X_exp = X

        X_train, y_train, X_test, y_test, transient_test, idx_train, idx_test = _split(
            X, y, is_transient, seed
        )
        X_train_exp, X_test_exp = X_exp[idx_train], X_exp[idx_test]

        def _record(name, preds, scores, latency):
            s = score_model(y_test, preds, transient_test, y_score=scores)
            s.update(
                {
                    "Model": name,
                    "Seed": seed,
                    "Latency (ms)": round(latency, 4),
                    "dataset": args.dataset,
                }
            )
            all_runs.append(s)
            print(
                f"  {name}: Acc={s['Accuracy']} F1={s['Macro-F1']} AUC={s['ROC-AUC']} "
                f"Fail-F1={s['Fail-F1']} Fail-AUC={s['Fail-ROC-AUC']}"
            )
            return s

        baseline = ThresholdBaseline()
        start = time.time()
        baseline_preds = baseline.predict(X_test)
        baseline_latency = (time.time() - start) * 1000 / len(X_test)
        _record("Threshold Baseline", baseline_preds, None, baseline_latency)

        if not args.skip_classical:
            print("Fitting classical RF/KNN/SVM monitors...")
            for name, (preds, scores, lat) in run_classical_baselines(X_train, y_train, X_test).items():
                _record(name, preds, scores, lat)

        print("Training MHSA-PerHead...")
        _, perhead_preds, perhead_score, perhead_latency = train_model(
            MHSAPerHead, X_train, y_train, X_test, seed, epochs, SEQ_LENGTH
        )
        _record("MHSA-PerHead", perhead_preds, perhead_score, perhead_latency)

        print("Training MHSA-Fused...")
        fused_model, fused_preds, fused_score, fused_latency = train_model(
            MHSAFused, X_train, y_train, X_test, seed, epochs, SEQ_LENGTH
        )
        _record("MHSA-Fused", fused_preds, fused_score, fused_latency)

        if not args.skip_aldomi:
            print("Training Aldomi SelectKBest+GRU+RF/KNN hybrid...")
            aldomi_epochs = min(epochs, 12)
            for name, (preds, scores, lat, info) in run_aldomi_hybrid(
                X_train_exp,
                y_train,
                X_test_exp,
                k=14,
                seed=seed,
                epochs=aldomi_epochs,
            ).items():
                print(f"    {name} selected_k={info.get('k_used')} idx={info.get('selected_channel_indices')}")
                _record(name, preds, scores, lat)
                if name == "Aldomi GRU-RF":
                    last_aldomi_cm = confusion_matrix(
                        (y_test.max(axis=1) > 0).astype(int),
                        (preds.max(axis=1) > 0).astype(int),
                        labels=[0, 1],
                    )

        fused_model_for_export = fused_model
        metric_names = list(GCT_METRIC_NAMES) if args.dataset == "gct" else list(METRIC_NAMES)
        fused_model_meta = {"seq_length": SEQ_LENGTH, "metrics": metric_names, "dataset": args.dataset}
        last_fused_cm = confusion_matrix(
            (y_test.max(axis=1) > 0).astype(int),
            (fused_preds.max(axis=1) > 0).astype(int),
            labels=[0, 1],
        )

    results_df = pd.DataFrame(all_runs)
    print("\nPer-seed results:")
    print(results_df.to_string(index=False))

    metric_cols = [
        "Accuracy",
        "Precision",
        "Recall",
        "Macro-F1",
        "ROC-AUC",
        "Fail-Accuracy",
        "Fail-Precision",
        "Fail-Recall",
        "Fail-F1",
        "Fail-ROC-AUC",
        "Transient Violation Recall",
        "Transient Underprediction Bias",
        "Latency (ms)",
    ]
    summary = results_df.groupby("Model")[metric_cols].agg(["mean", "std"]).round(4)
    print("\nSummary across seeds (mean +/- std):")
    with pd.option_context("display.max_columns", None, "display.width", 220):
        print(summary)

    if args.dataset == "gct":
        results_dir = os.path.join(parent_dir, "results", "gct")
    else:
        results_dir = os.path.join(parent_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    results_df.to_csv(os.path.join(results_dir, "results_per_seed.csv"), index=False)
    summary.to_csv(os.path.join(results_dir, "results_summary.csv"))

    extra = []
    if args.dataset == "gct":
        extra.append(f"- GCT load meta: `{json.dumps(gct_loader_mod.LAST_LOAD_META, default=str)}`\n")
        extra.append("- GCT CSVs live under `results/gct/` so synthetic CSVs are not overwritten.\n")
        extra.append("- 2011 channel 3 (`net`) is sampled CPU — ClusterData 2011 has no network-byte column.\n")
        extra.append("- `net_channel_is_network_bytes=false` (see `data/gct/CHANNEL_HONESTY.md`).\n")
        extra.append("- Aldomi uses expanded usage columns + history-only SCHEDULE/UPDATE counts.\n")
        extra.append(
            "- Subset: landed 2011 parts listed in load meta; not the full 29-day / 2019 Borg cells.\n"
        )
    _write_provenance(results_dir, args.dataset, extra)

    if args.dataset == "gct":
        if last_fused_cm is not None:
            cm_path = os.path.join(results_dir, "confusion_mhsa_fused_last_seed.csv")
            pd.DataFrame(last_fused_cm, index=["true_healthy", "true_unhealthy"], columns=["pred_healthy", "pred_unhealthy"]).to_csv(
                cm_path
            )
        if last_aldomi_cm is not None:
            cm_a = os.path.join(results_dir, "confusion_aldomi_gru_rf_last_seed.csv")
            pd.DataFrame(last_aldomi_cm, index=["true_healthy", "true_unhealthy"], columns=["pred_healthy", "pred_unhealthy"]).to_csv(
                cm_a
            )
        with open(os.path.join(results_dir, "gct_load_meta.json"), "w") as f:
            json.dump(gct_loader_mod.LAST_LOAD_META, f, indent=2, default=str)
        # Pointer in the synthetic results folder without wiping those CSVs.
        pointer = os.path.join(parent_dir, "results", "RESULTS_PROVENANCE.md")
        with open(pointer, "w") as f:
            f.write(
                "# Results provenance\n\n"
                "## Synthetic (artefact-as-built, not formal CA2)\n\n"
                "- Files: `results_per_seed.csv`, `results_summary.csv` from `--dataset synthetic`.\n"
                "- These rows are **not** Google Cluster Trace evidence.\n\n"
                "## Google Cluster Trace (formal CA2)\n\n"
                "- Files: `gct/results_per_seed.csv`, `gct/results_summary.csv`, "
                "`gct/RESULTS_PROVENANCE.md` from `--dataset gct`.\n"
                f"- Load meta: `{json.dumps(gct_loader_mod.LAST_LOAD_META, default=str)}`\n"
                "- Dataset flag in those CSVs: **gct**.\n"
            )

    print(f"\nResults saved to {results_dir}/")

    if fused_model_for_export is not None and args.dataset == "synthetic":
        model_dir = os.path.join(parent_dir, "src", "lambda_handler", "model")
        os.makedirs(model_dir, exist_ok=True)
        torch.save(fused_model_for_export.state_dict(), os.path.join(model_dir, "mhsa_fused.pt"))
        with open(os.path.join(model_dir, "metadata.json"), "w") as f:
            json.dump(fused_model_meta, f, indent=2)
        print(f"Deployable model saved to {model_dir}/mhsa_fused.pt")


if __name__ == "__main__":
    main()
