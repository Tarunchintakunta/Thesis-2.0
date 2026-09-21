#!/usr/bin/env python3
"""On-node live PAKS vs HPA scale loop against local k3s.

Invoked on the EC2 k3s host via SSM (see run_live_aws_k8s.py). Requires:
  PAKS_K8S_APPLY=1, kubectl, /etc/rancher/k3s/k3s.yaml, deployment/paks-demo.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

# When copied to /opt/paks on the instance, FRAMEWORK may be absent — embed minimal path.
HERE = Path(__file__).resolve().parent
CANDIDATES = [
    HERE.parent,  # scripts/ → framework root
    Path("/opt/paks/paks-framework"),
    Path("/opt/paks"),
]
for root in CANDIDATES:
    if (root / "src" / "k8s" / "live_client.py").exists():
        sys.path.insert(0, str(root))
        FRAMEWORK_ROOT = root
        break
else:
    FRAMEWORK_ROOT = HERE.parent
    sys.path.insert(0, str(FRAMEWORK_ROOT))

from src.k8s.adaptive_engine import (  # noqa: E402
    POD_CAPACITY_CORES,
    run_paks_k8s,
    run_reactive_hpa_k8s,
)
from src.k8s.live_client import LiveKubectlClient  # noqa: E402
from src.eval.metrics import evaluate_policy  # noqa: E402
from src.models.lstm_predictor import LOOKBACK, NumpyLSTMRegressor, series_windows  # noqa: E402


def _synthetic_burst_workload(n: int = 24, seed: int = 42) -> np.ndarray:
    """Tiny TRACE-shaped series for live apply (keeps t3.micro short).

    Prefer Alibaba-derived bins when a CSV is present under /opt/paks.
    """
    csv_candidates = [
        FRAMEWORK_ROOT / "data" / "traces" / "alibaba_v2018_machine_usage_sample_cluster_cpu.csv",
        Path("/opt/paks/alibaba_sample_cluster_cpu.csv"),
    ]
    for p in csv_candidates:
        if p.exists():
            # cpu_cores_sum or cpu_pct_mean column
            import csv as _csv

            rows = []
            with p.open() as f:
                reader = _csv.DictReader(f)
                for row in reader:
                    val = row.get("cpu_cores_sum") or row.get("cpu_pct_mean") or row.get("cpu")
                    if val is None:
                        continue
                    rows.append(float(val))
                    if len(rows) >= n:
                        break
            if len(rows) >= max(LOOKBACK + 2, 8):
                arr = np.asarray(rows[:n], dtype=float)
                # Scale % into demand units similar to formal driver
                if arr.max() <= 100.0:
                    arr = arr * 10.0
                return arr
    rng = np.random.default_rng(seed)
    base = 30.0 + 10.0 * np.sin(np.linspace(0, 4 * np.pi, n))
    spikes = np.zeros(n)
    spikes[n // 3 : n // 3 + 3] = 80.0
    spikes[2 * n // 3 : 2 * n // 3 + 2] = 120.0
    noise = rng.normal(0, 3.0, size=n)
    return np.clip(base + spikes + noise, 5.0, None)


def main() -> int:
    os.environ["PAKS_K8S_APPLY"] = "1"
    out_path = Path(os.environ.get("PAKS_LIVE_OUT", "/opt/paks/formal_k8s_live_aws.json"))
    n_steps = int(os.environ.get("PAKS_LIVE_STEPS", "20"))
    max_replicas = int(os.environ.get("PAKS_LIVE_MAX_REPLICAS", "4"))
    seed = int(os.environ.get("PAKS_LIVE_SEED", "42"))

    workload = _synthetic_burst_workload(n=n_steps, seed=seed)
    lookback = min(LOOKBACK, max(3, n_steps // 4))

    X, y = series_windows(workload, lookback=lookback)
    cut = max(lookback, int(0.7 * len(X))) if len(X) else 0
    model = NumpyLSTMRegressor(hidden_size=8, seed=seed)
    if len(X) >= lookback + 2:
        model.fit(X[: max(cut, 1)], y[: max(cut, 1)], epochs=6)
    else:
        # Degenerate: persistence-only predictor
        pass

    def predict_fn(window: np.ndarray) -> float:
        try:
            return float(model.predict_next(window))
        except Exception:
            return float(window[-1])

    client_hpa = LiveKubectlClient(ready_timeout_s=60.0)
    client_paks = LiveKubectlClient(ready_timeout_s=60.0)

    # Reset deployment to 1 before each policy
    client_hpa.patch_deployment_scale(replicas=1, source="reset", step=-1, wait=True)

    t0 = time.time()
    hpa_pods, hpa_snap, hpa_c = run_reactive_hpa_k8s(
        workload,
        client=client_hpa,
        dry_run=False,
        max_replicas_live=max_replicas,
        capacity=POD_CAPACITY_CORES,
    )
    client_paks.patch_deployment_scale(replicas=1, source="reset", step=-1, wait=True)
    paks_pods, paks_snap, paks_c = run_paks_k8s(
        workload,
        predict_fn,
        client=client_paks,
        lookback=lookback,
        dry_run=False,
        max_replicas_live=max_replicas,
        capacity=POD_CAPACITY_CORES,
    )
    elapsed = time.time() - t0

    y_true = workload[lookback:]
    y_pred = np.array(
        [predict_fn(workload[t - lookback : t]) for t in range(lookback, len(workload))]
    )

    hpa_row = evaluate_policy(
        workload,
        hpa_pods,
        POD_CAPACITY_CORES,
        bin_seconds=5.0,
        y_true=y_true,
        y_pred=y_pred,
        policy="reactive-hpa",
        prediction_evidence="n/a",
        loop_evidence="LIVE",
    )
    paks_row = evaluate_policy(
        workload,
        paks_pods,
        POD_CAPACITY_CORES,
        bin_seconds=5.0,
        y_true=y_true,
        y_pred=y_pred,
        policy="paks-adaptive",
        prediction_evidence="TRACE",
        loop_evidence="LIVE",
    )
    for row, client in ((hpa_row, hpa_c), (paks_row, paks_c)):
        lat = client.latency_summary()
        row["live_k8s"] = True
        row["live_cloudwatch"] = False  # filled by orchestrator after PutMetricData
        row["scaling_latency_s_mean"] = lat["mean_s"]
        row["scaling_latency_s_p50"] = lat["p50_s"]
        row["scaling_latency_s_max"] = lat["max_s"]
        row["evidence_latency"] = "LIVE"
        row["evidence_loop"] = "LIVE"

    payload = {
        "live_apply": True,
        "aws_deployed": True,
        "cluster": "k3s-single-node",
        "instance_role": "k3s-single",
        "project_tag": "paks-k8s-live",
        "n_steps": int(n_steps),
        "max_replicas_live": max_replicas,
        "lookback": lookback,
        "elapsed_wall_s": elapsed,
        "workload_head": workload[:5].tolist(),
        "hpa_metrics": hpa_row,
        "paks_metrics": paks_row,
        "hpa_latency": hpa_c.latency_summary(),
        "paks_latency": paks_c.latency_summary(),
        "hpa_ops": len(hpa_c.operations),
        "paks_ops": len(paks_c.operations),
        "sample_hpa": hpa_c.as_json()[:3],
        "sample_paks": paks_c.as_json()[:3],
        "hpa_snapshot_tail": hpa_snap[-2:],
        "paks_snapshot_tail": paks_snap[-2:],
        "evidence": {
            "k8s_scale": "LIVE",
            "lstm_series": "TRACE-or-synthetic-fallback",
            "cost": "SIMULATED",
            "cloudwatch": "pending-orchestrator",
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, default=str) + "\n")
    print(json.dumps({"wrote": str(out_path), "hpa_mean_lat": hpa_row["scaling_latency_s_mean"],
                      "paks_mean_lat": paks_row["scaling_latency_s_mean"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
