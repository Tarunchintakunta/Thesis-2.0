#!/usr/bin/env python3
"""Formal PAKS driver: LSTM on GCT-derived series + dry-run K8s scaler vs HPA.

Does not deploy AWS or a live cluster. Proxy MLP/synthetic path is a separate
script (train_and_evaluate.py) and is not invoked here.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FRAMEWORK_ROOT))

from src.data.trace_loader import load_gct2010_jobs, load_scaling_workload, require_dataset
from src.eval.metrics import evaluate_policy
from src.k8s.adaptive_engine import (
    POD_CAPACITY_CORES,
    run_paks_k8s,
    run_reactive_hpa_k8s,
)
from src.models.lstm_predictor import (
    LOOKBACK,
    NumpyLSTMRegressor,
    mae_rmse,
    require_tensorflow,
    series_windows,
    train_lstm_on_jobs,
)


def _write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset", default="gct2010", help="gct2010 | gct | gct2011 | gct2019 | alibaba | synthetic")
    p.add_argument("--backend", default="numpy-lstm", choices=["numpy-lstm", "tensorflow"])
    p.add_argument("--epochs", type=int, default=8)
    p.add_argument("--max-train-windows", type=int, default=3000)
    p.add_argument("--hidden", type=int, default=16)
    p.add_argument("--lookback", type=int, default=LOOKBACK)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    print("PAKS formal driver — LSTM + K8s dry-run vs HPA. No live AWS/K8s apply.")
    if args.dataset == "synthetic":
        print("WARNING: --dataset synthetic is PROXY, not formal CA2 evidence.")

    if args.backend == "tensorflow":
        require_tensorflow()

    require_dataset(args.dataset)
    workload, meta = load_scaling_workload(args.dataset, seed=args.seed)
    print(f"dataset={meta.get('dataset')} proxy={meta.get('proxy')} n_steps={len(workload)}")
    print(f"note={meta.get('note')}")

    results_dir = FRAMEWORK_ROOT / "results"
    results_dir.mkdir(exist_ok=True)

    pred_rows = []
    cluster_model = None
    if not meta.get("proxy") and meta.get("dataset") == "gct2010":
        jobs = load_gct2010_jobs()
        job_model, job_metrics = train_lstm_on_jobs(
            jobs,
            lookback=args.lookback,
            hidden_size=args.hidden,
            seed=args.seed,
            max_train_windows=args.max_train_windows,
            epochs=args.epochs,
            backend=args.backend,
        )
        job_metrics["policy"] = "lstm-job-windows"
        job_metrics["dataset"] = meta["dataset"]
        pred_rows.append(job_metrics)
        print(
            "job-split LSTM  MAE_test={mae_test:.4f} RMSE_test={rmse_test:.4f} "
            "persistence_MAE={mae_persistence_test:.4f} backend={backend}".format(**job_metrics)
        )
        cluster_model = job_model
    else:
        cluster_model = NumpyLSTMRegressor(hidden_size=args.hidden, seed=args.seed)

    Xc, yc = series_windows(workload, lookback=args.lookback)
    cut = max(args.lookback, int(0.7 * len(Xc)))
    cluster_model.fit(Xc[:cut], yc[:cut], epochs=max(6, args.epochs // 2))
    yhat = cluster_model.predict(Xc[cut:])
    mae_c, rmse_c = mae_rmse(yc[cut:], yhat)
    mae_p, rmse_p = mae_rmse(yc[cut:], Xc[cut:, -1])
    cluster_pred = {
        "policy": "lstm-cluster-series",
        "dataset": meta.get("dataset"),
        "n_train_windows": int(cut),
        "n_test_windows": int(len(yc) - cut),
        "lookback": args.lookback,
        "hidden_size": args.hidden,
        "backend": cluster_model.backend,
        "mae_test": mae_c,
        "rmse_test": rmse_c,
        "mae_persistence_test": mae_p,
        "rmse_persistence_test": rmse_p,
        "evidence": "TRACE" if not meta.get("proxy") else "SIMULATED",
        "split": "last 30% of cluster bins",
        "note": "Cluster series is short (GCT v1 ~7h / 5min). Job-split MAE/RMSE is the primary prediction evidence.",
    }
    pred_rows.append(cluster_pred)
    print(f"cluster LSTM  MAE_test={mae_c:.4f} RMSE_test={rmse_c:.4f} persistence_MAE={mae_p:.4f}")

    def predict_fn(window: np.ndarray) -> float:
        return cluster_model.predict_next(window)

    hpa_pods, hpa_snap, hpa_client = run_reactive_hpa_k8s(workload)
    paks_pods, paks_snap, paks_client = run_paks_k8s(workload, predict_fn, lookback=args.lookback)

    # Walk-forward predictions aligned to workload[t] for t>=lookback (prediction of current from past).
    y_true_loop = workload[args.lookback :]
    y_pred_loop = np.array(
        [cluster_model.predict_next(workload[t - args.lookback : t]) for t in range(args.lookback, len(workload))]
    )
    pred_ev = "TRACE" if not meta.get("proxy") else "SIMULATED"
    bin_seconds = float(meta.get("bin_seconds") or 300.0)

    scale_rows = [
        evaluate_policy(
            workload,
            hpa_pods,
            POD_CAPACITY_CORES,
            bin_seconds=bin_seconds,
            y_true=y_true_loop,
            y_pred=y_pred_loop,
            policy="reactive-hpa",
            prediction_evidence="n/a",
            loop_evidence="SIMULATED",
        ),
        evaluate_policy(
            workload,
            paks_pods,
            POD_CAPACITY_CORES,
            bin_seconds=bin_seconds,
            y_true=y_true_loop,
            y_pred=y_pred_loop,
            policy="paks-adaptive",
            prediction_evidence=pred_ev,
            loop_evidence="SIMULATED",
        ),
    ]
    # HPA does not use the LSTM; blank its prediction columns for honesty.
    scale_rows[0]["mae"] = np.nan
    scale_rows[0]["rmse"] = np.nan
    scale_rows[0]["evidence_prediction"] = "n/a"

    pred_df = pd.DataFrame(pred_rows)
    scale_df = pd.DataFrame(scale_rows)
    pred_path = results_dir / "formal_prediction_metrics.csv"
    scale_path = results_dir / "formal_scaling_metrics.csv"
    pred_df.to_csv(pred_path, index=False)
    scale_df.to_csv(scale_path, index=False)

    meta_public = {
        k: (str(Path(v).name) if k.endswith("_csv") else v)
        for k, v in meta.items()
    }
    _write_json(
        results_dir / "formal_k8s_dry_run.json",
        {
            "live_apply": False,
            "aws_deployed": False,
            "hpa_ops": len(hpa_client.operations),
            "paks_ops": len(paks_client.operations),
            "sample_hpa": hpa_client.as_json()[:3],
            "sample_paks": paks_client.as_json()[:3],
            "hpa_snapshot_tail": hpa_snap[-2:],
            "paks_snapshot_tail": paks_snap[-2:],
            "dataset_meta": meta_public,
        },
    )

    provenance = results_dir / "RESULTS_PROVENANCE.md"
    provenance.write_text(
        "\n".join(
            [
                "# Results provenance — Pooja PAKS",
                "",
                "**Status:** NOT COMPLETE. No live Kubernetes. No AWS EC2/S3/CloudWatch deploy.",
                "",
                "## Formal (this driver)",
                f"- Dataset meta: `{meta_public}`",
                f"- Prediction CSV: `{pred_path.name}`",
                "  - Job-split LSTM MAE/RMSE is **TRACE** (GCT v1, held-out jobs).",
                "  - Honesty: last-value **persistence MAE is lower** than LSTM on job windows",
                "    (many jobs are near-constant). Cluster-aggregate LSTM vs persistence is the",
                "    scaling-relevant series but **n_test is small** (~19 bins). Neither result",
                "    is GCT 2011/2019 or Alibaba.",
                f"- Scaling CSV: `{scale_path.name}` — util / response / throughput / cost / SLA /",
                "  scaling latency are **SIMULATED** (capacity mapping, M/M/1-style queue proxy,",
                "  assumed $0.04/pod-hour). `live_k8s=false`, `live_cloudwatch=false`.",
                "- K8s: dry-run `PATCH .../scale?dryRun=All` recorded in `formal_k8s_dry_run.json`.",
                "",
                "## Proxy (do not mix)",
                "- `results_summary.csv` / `results_per_seed.csv` = NimbusGuard-framed MLP on synthetic sine/spikes.",
                "- See `PROXY_NIMBUSGUARD.md` and `src/proxy/README.md`.",
                "",
            ]
        )
        + "\n"
    )

    print(f"wrote {pred_path}")
    print(f"wrote {scale_path}")
    print("HPA vs PAKS (simulated loop):")
    print(scale_df[["policy", "mae", "rmse", "cpu_util_mean", "sla_compliance", "cost_usd", "scaling_events"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(2)
    except ImportError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(3)
