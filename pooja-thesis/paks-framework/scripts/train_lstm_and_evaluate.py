#!/usr/bin/env python3
"""Formal PAKS driver: LSTM on GCT/Alibaba-derived series + dry-run K8s scaler vs HPA.

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

from src.data.trace_loader import (
    alibaba_derived_ready,
    gct2010_ready,
    gct2011_derived_ready,
    load_alibaba_cluster,
    load_gct2010_jobs,
    load_gct2011_jobs,
    load_scaling_workload,
    require_dataset,
)
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


def _job_frame_for(dataset: str):
    if dataset == "gct2011":
        return load_gct2011_jobs(), "gct2011"
    if dataset == "gct2010":
        return load_gct2010_jobs(), "gct2010"
    return None, None


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--dataset",
        default="gct",
        help="gct | gct2010 | gct2011 | gct2019 | alibaba | synthetic "
        "(default gct prefers 2011 sample when derived series exist)",
    )
    p.add_argument("--backend", default="numpy-lstm", choices=["numpy-lstm", "tensorflow"])
    p.add_argument("--epochs", type=int, default=8)
    p.add_argument("--max-train-windows", type=int, default=3000)
    p.add_argument("--hidden", type=int, default=16)
    p.add_argument("--lookback", type=int, default=LOOKBACK)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--max-scale-steps",
        type=int,
        default=400,
        help="Cap scaling-loop length (Alibaba sample can be >2k bins).",
    )
    p.add_argument(
        "--also-alibaba",
        action="store_true",
        default=True,
        help="Also train/eval Alibaba cluster LSTM when sample is present (default on).",
    )
    p.add_argument("--no-also-alibaba", action="store_false", dest="also_alibaba")
    args = p.parse_args()

    print("PAKS formal driver — LSTM + K8s dry-run vs HPA. No live AWS/K8s apply.")
    if args.dataset == "synthetic":
        print("WARNING: --dataset synthetic is PROXY, not trace evidence.")

    if args.backend == "tensorflow":
        require_tensorflow()

    require_dataset(args.dataset)
    workload, meta = load_scaling_workload(
        args.dataset, seed=args.seed, max_steps=args.max_scale_steps
    )
    # Single GCT 2011 shard yields few 300s cluster bins; use a longer TRACE series
    # for the HPA/PAKS loop when needed (jobs LSTM still uses 2011 when present).
    scale_meta = dict(meta)
    demand_scale = 1.0
    min_scale = max(40, args.lookback * 3)
    if len(workload) < min_scale and not meta.get("proxy"):
        if alibaba_derived_ready():
            workload, scale_meta = load_scaling_workload(
                "alibaba", seed=args.seed, max_steps=args.max_scale_steps
            )
            # Keep LSTM metrics in native CPU%; scale demand only for replica math.
            demand_scale = 10.0
            scale_meta = dict(scale_meta)
            scale_meta["scaled_from_pct"] = True
            scale_meta["demand_scale"] = demand_scale
            scale_meta["note"] = (
                (scale_meta.get("note") or "")
                + " Scaling loop uses Alibaba RANGE sample (CPU%×10 demand units) "
                "because primary GCT cluster bins were too few."
            )
        elif gct2010_ready():
            workload, scale_meta = load_scaling_workload(
                "gct2010", seed=args.seed, max_steps=args.max_scale_steps
            )
            scale_meta = dict(scale_meta)
            scale_meta["note"] = (
                (scale_meta.get("note") or "")
                + " Scaling loop fell back to GCT 2010 (primary cluster series too short)."
            )
    print(f"pred_dataset={meta.get('dataset')} scale_dataset={scale_meta.get('dataset')} "
          f"proxy={meta.get('proxy')} n_steps={len(workload)}")
    print(f"note={scale_meta.get('note')}")

    results_dir = FRAMEWORK_ROOT / "results"
    results_dir.mkdir(exist_ok=True)

    pred_rows = []
    jobs_df, jobs_ds = _job_frame_for(meta.get("dataset", ""))
    if jobs_df is None and gct2011_derived_ready():
        jobs_df, jobs_ds = load_gct2011_jobs(), "gct2011"
    if jobs_df is None and gct2010_ready():
        jobs_df, jobs_ds = load_gct2010_jobs(), "gct2010"

    if jobs_df is not None and not meta.get("proxy"):
        _job_model, job_metrics = train_lstm_on_jobs(
            jobs_df,
            lookback=args.lookback,
            hidden_size=args.hidden,
            seed=args.seed,
            max_train_windows=args.max_train_windows,
            epochs=args.epochs,
            backend=args.backend,
        )
        job_metrics["policy"] = "lstm-job-windows"
        job_metrics["dataset"] = jobs_ds
        pred_rows.append(job_metrics)
        print(
            "job-split LSTM  MAE_test={mae_test:.4f} RMSE_test={rmse_test:.4f} "
            "persistence_MAE={mae_persistence_test:.4f} backend={backend} dataset={dataset}".format(
                **job_metrics
            )
        )

    Xc, yc = series_windows(workload, lookback=args.lookback)
    cut = max(args.lookback, int(0.7 * len(Xc)))
    cluster_model = NumpyLSTMRegressor(hidden_size=args.hidden, seed=args.seed)
    cluster_model.fit(Xc[:cut], yc[:cut], epochs=max(6, args.epochs // 2))
    yhat = cluster_model.predict(Xc[cut:])
    mae_c, rmse_c = mae_rmse(yc[cut:], yhat)
    mae_p, rmse_p = mae_rmse(yc[cut:], Xc[cut:, -1])
    cluster_pred = {
        "policy": "lstm-cluster-series",
        "dataset": scale_meta.get("dataset"),
        "n_train_windows": int(cut),
        "n_test_windows": int(len(yc) - cut),
        "lookback": args.lookback,
        "hidden_size": args.hidden,
        "backend": cluster_model.backend,
        "mae_test": mae_c,
        "rmse_test": rmse_c,
        "mae_persistence_test": mae_p,
        "rmse_persistence_test": rmse_p,
        "evidence": "TRACE" if not scale_meta.get("proxy") else "SIMULATED",
        "split": "last 30% of cluster bins",
        "note": scale_meta.get("note", ""),
        "units": "cpu_pct_mean" if scale_meta.get("dataset") == "alibaba" else "cpu_cores_sum",
    }
    pred_rows.append(cluster_pred)
    print(f"cluster LSTM  MAE_test={mae_c:.4f} RMSE_test={rmse_c:.4f} persistence_MAE={mae_p:.4f}")

    # Avoid duplicate Alibaba row when the scaling series already is Alibaba.
    if (
        args.also_alibaba
        and alibaba_derived_ready()
        and scale_meta.get("dataset") != "alibaba"
        and meta.get("dataset") != "alibaba"
    ):
        ali_df = load_alibaba_cluster()
        ali_series = ali_df["cpu_cores_sum"].to_numpy(dtype=float)
        if args.max_scale_steps:
            ali_series = ali_series[: args.max_scale_steps]
        Xa, ya = series_windows(ali_series, lookback=args.lookback)
        cut_a = max(args.lookback, int(0.7 * len(Xa)))
        ali_model = NumpyLSTMRegressor(hidden_size=args.hidden, seed=args.seed)
        ali_model.fit(Xa[:cut_a], ya[:cut_a], epochs=max(6, args.epochs // 2))
        yhat_a = ali_model.predict(Xa[cut_a:])
        mae_a, rmse_a = mae_rmse(ya[cut_a:], yhat_a)
        mae_ap, rmse_ap = mae_rmse(ya[cut_a:], Xa[cut_a:, -1])
        pred_rows.append(
            {
                "policy": "lstm-cluster-series",
                "dataset": "alibaba",
                "n_train_windows": int(cut_a),
                "n_test_windows": int(len(ya) - cut_a),
                "lookback": args.lookback,
                "hidden_size": args.hidden,
                "backend": ali_model.backend,
                "mae_test": mae_a,
                "rmse_test": rmse_a,
                "mae_persistence_test": mae_ap,
                "rmse_persistence_test": rmse_ap,
                "evidence": "TRACE",
                "split": "last 30% of cluster bins",
                "note": "Alibaba v2018 machine_usage HTTP RANGE 64MiB sample; not full 1.7GiB dump.",
                "units": "cpu_pct_mean",
            }
        )
        print(f"alibaba LSTM  MAE_test={mae_a:.4f} RMSE_test={rmse_a:.4f} persistence_MAE={mae_ap:.4f}")

    scale_workload = np.asarray(workload, dtype=float) * float(demand_scale)

    def predict_fn(window: np.ndarray) -> float:
        # window is in scaled demand units when demand_scale != 1
        raw = window / float(demand_scale)
        return float(cluster_model.predict_next(raw) * demand_scale)

    hpa_pods, hpa_snap, hpa_client = run_reactive_hpa_k8s(scale_workload)
    paks_pods, paks_snap, paks_client = run_paks_k8s(
        scale_workload, predict_fn, lookback=args.lookback
    )

    y_true_loop = scale_workload[args.lookback :]
    y_pred_loop = np.array(
        [
            predict_fn(scale_workload[t - args.lookback : t])
            for t in range(args.lookback, len(scale_workload))
        ]
    )
    pred_ev = "TRACE" if not scale_meta.get("proxy") else "SIMULATED"
    bin_seconds = float(scale_meta.get("bin_seconds") or 300.0)
    mem = scale_meta.get("mem_series")
    if mem is not None:
        mem = np.asarray(mem, dtype=float)[: len(scale_workload)] * float(demand_scale)
    mem_cap = float(np.nanmean(mem) / 0.7) if mem is not None and np.nanmean(mem) > 0 else 8.0

    scale_rows = [
        evaluate_policy(
            scale_workload,
            hpa_pods,
            POD_CAPACITY_CORES,
            bin_seconds=bin_seconds,
            mem=mem,
            mem_capacity=mem_cap,
            y_true=y_true_loop,
            y_pred=y_pred_loop,
            policy="reactive-hpa",
            prediction_evidence="n/a",
            loop_evidence="SIMULATED",
        ),
        evaluate_policy(
            scale_workload,
            paks_pods,
            POD_CAPACITY_CORES,
            bin_seconds=bin_seconds,
            mem=mem,
            mem_capacity=mem_cap,
            y_true=y_true_loop,
            y_pred=y_pred_loop,
            policy="paks-adaptive",
            prediction_evidence=pred_ev,
            loop_evidence="SIMULATED",
        ),
    ]
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
        for k, v in {**meta, **{f"scale_{kk}": vv for kk, vv in scale_meta.items()}}.items()
        if k != "mem_series" and not str(k).endswith("mem_series")
    }
    meta_public["pred_dataset"] = meta.get("dataset")
    meta_public["scale_dataset"] = scale_meta.get("dataset")
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
                "  - Job-split LSTM MAE/RMSE is **TRACE** when GCT 2010/2011 job series are used.",
                "  - Alibaba cluster LSTM (if present) is **TRACE** on a **64 MiB HTTP RANGE**",
                "    sample of `machine_usage.tar.gz` (not the full 1.7 GiB dump).",
                "  - GCT 2011 evidence here is **one** public `task_usage` shard",
                "    (`part-00000-of-00500`), SHA256-verified — not the full 29-day cell.",
                f"- Scaling CSV: `{scale_path.name}` — util / response / throughput / cost / SLA /",
                "  scaling latency are **SIMULATED** (capacity mapping, M/M/1-style queue proxy,",
                "  assumed $0.04/pod-hour). `live_k8s=false`, `live_cloudwatch=false`.",
                "- K8s: dry-run `PATCH .../scale?dryRun=All` recorded in `formal_k8s_dry_run.json`.",
                "- Local kind/minikube: see `results/K8S_LOCAL_PROBE.md` (Docker daemon / kind absent",
                "  on this host → live apply still unmet).",
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
    cols = [c for c in ["policy", "mae", "rmse", "cpu_util_mean", "mem_util_mean", "sla_compliance", "cost_usd", "scaling_events"] if c in scale_df.columns]
    print(scale_df[cols].to_string(index=False))
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
