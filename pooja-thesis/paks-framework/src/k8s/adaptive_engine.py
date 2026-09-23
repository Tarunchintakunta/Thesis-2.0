"""Adaptive PAKS scaling engine vs reactive HPA, both emitting K8s API shapes.

HPA uses the autoscaling/v2 CPU-utilization replica formula on *observed* load.
PAKS uses LSTM (or any predictor) next-step load, then PATCHes the Deployment
scale subresource (dry-run). Replica counts in the loop are SIMULATED: the
dry-run client does not wait for kubelet.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from src.k8s.api_shapes import (
    DEFAULT_DEPLOYMENT,
    DEFAULT_NAMESPACE,
    TARGET_CPU_UTILIZATION,
    hpa_spec,
    hpa_status,
)
from src.k8s.dry_run_client import DryRunK8sClient
from src.models.lstm_predictor import LOOKBACK, NumpyLSTMRegressor

# Simulated pod capacity in the same units as the workload series (normalized cores).
POD_CAPACITY_CORES = 10.0
MIN_REPLICAS = 1
MAX_REPLICAS = 100
TARGET_UTIL = TARGET_CPU_UTILIZATION / 100.0


def clip_replicas(n: float) -> int:
    return int(np.clip(int(np.ceil(n)), MIN_REPLICAS, MAX_REPLICAS))


def replicas_for_load(load: float, capacity: float = POD_CAPACITY_CORES, target_util: float = TARGET_UTIL) -> int:
    return clip_replicas(load / (capacity * target_util))


def cpu_utilization_percent(load: float, replicas: int, capacity: float = POD_CAPACITY_CORES) -> int:
    if replicas <= 0:
        return 100
    util = load / (replicas * capacity)
    return int(np.clip(round(100.0 * util), 0, 10_000))


def hpa_desired_from_current(
    current_replicas: int,
    current_cpu_utilization: int,
    target_cpu_utilization: int = TARGET_CPU_UTILIZATION,
) -> int:
    """Kubernetes HPA v2 ratio formula (no tolerance / stabilization here)."""
    if target_cpu_utilization <= 0:
        raise ValueError("target CPU utilization must be positive")
    raw = current_replicas * (current_cpu_utilization / float(target_cpu_utilization))
    return clip_replicas(raw)


class AdaptiveScalingEngine:
    """Prediction-driven scaler that talks K8s Scale JSON (dry-run client)."""

    def __init__(
        self,
        client: Optional[DryRunK8sClient] = None,
        predictor: Optional[NumpyLSTMRegressor] = None,
        lookback: int = LOOKBACK,
        name: str = DEFAULT_DEPLOYMENT,
        namespace: str = DEFAULT_NAMESPACE,
        safety_buffer: float = 1.05,
    ):
        self.client = client or DryRunK8sClient()
        self.predictor = predictor
        self.lookback = int(lookback)
        self.name = name
        self.namespace = namespace
        self.safety_buffer = float(safety_buffer)

    def desired_from_prediction(self, predicted_load: float) -> int:
        return replicas_for_load(predicted_load * self.safety_buffer)

    def emit_scale(
        self,
        desired: int,
        current: int,
        step: int,
        predicted_load: Optional[float],
        observed_load: Optional[float],
        source: str = "paks",
        extra: Optional[Dict[str, Any]] = None,
        dry_run: bool = True,
    ):
        return self.client.patch_deployment_scale(
            replicas=desired,
            name=self.name,
            namespace=self.namespace,
            current_replicas=current,
            dry_run=dry_run,
            source=source,
            step=step,
            predicted_load=predicted_load,
            observed_load=observed_load,
            extra=extra,
        )


def run_reactive_hpa_k8s(
    workload: Sequence[float],
    client: Optional[Any] = None,
    name: str = DEFAULT_DEPLOYMENT,
    namespace: str = DEFAULT_NAMESPACE,
    capacity: float = POD_CAPACITY_CORES,
    dry_run: bool = True,
    max_replicas_live: int = 8,
) -> Tuple[np.ndarray, List[Dict[str, Any]], Any]:
    """Reactive HPA: act on *already observed* utilization, one-step delay."""
    client = client or DryRunK8sClient()
    w = np.asarray(workload, dtype=np.float64)
    spec = hpa_spec(name=name, namespace=namespace)
    pods: List[int] = []
    snapshots: List[Dict[str, Any]] = []
    current = replicas_for_load(w[0], capacity=capacity)
    if not dry_run:
        current = min(current, max_replicas_live)
    for t in range(len(w)):
        pods.append(current)
        util = cpu_utilization_percent(w[t], current, capacity=capacity)
        desired = hpa_desired_from_current(current, util)
        if not dry_run:
            desired = min(desired, max_replicas_live)
        intent = client.patch_deployment_scale(
            replicas=desired,
            name=name,
            namespace=namespace,
            current_replicas=current,
            dry_run=dry_run,
            source="hpa",
            step=t,
            observed_load=float(w[t]),
            extra={"hpa_spec": spec, "hpa_status": hpa_status(current, desired, util)},
        )
        evidence = "LIVE" if not dry_run else "SIMULATED"
        apply_s = (intent.extra or {}).get("apply_latency_s")
        snapshots.append(
            {
                "step": t,
                "policy": "reactive-hpa",
                "observed_load": float(w[t]),
                "current_replicas": current,
                "desired_replicas": desired,
                "cpu_utilization_pct": util,
                "k8s_path": intent.path,
                "apply_latency_s": apply_s,
                "evidence": evidence,
            }
        )
        current = desired
    return np.asarray(pods, dtype=float), snapshots, client


def run_paks_k8s(
    workload: Sequence[float],
    predict_fn: Callable[[np.ndarray], float],
    client: Optional[Any] = None,
    lookback: int = LOOKBACK,
    name: str = DEFAULT_DEPLOYMENT,
    namespace: str = DEFAULT_NAMESPACE,
    capacity: float = POD_CAPACITY_CORES,
    safety_buffer: float = 1.05,
    dry_run: bool = True,
    max_replicas_live: int = 8,
) -> Tuple[np.ndarray, List[Dict[str, Any]], Any]:
    """PAKS: scale from predicted next load via Scale PATCH (dry-run or live).

    The replica vector is the count *in service* at each step. A scale decision
    takes effect on the next step (simulated scaling latency = 1 control interval
    when dry_run; live path records kubelet Ready latency in intent.extra).
    """
    engine = AdaptiveScalingEngine(
        client=client or DryRunK8sClient(),
        lookback=lookback,
        name=name,
        namespace=namespace,
        safety_buffer=safety_buffer,
    )
    w = np.asarray(workload, dtype=np.float64)
    pods: List[int] = []
    snapshots: List[Dict[str, Any]] = []
    current = replicas_for_load(w[0], capacity=capacity)
    if not dry_run:
        current = min(current, max_replicas_live)
    for t in range(len(w)):
        pods.append(current)
        if t < lookback:
            predicted = float(w[t])
            pred_source = "warmup-observed"
        else:
            predicted = float(predict_fn(w[t - lookback : t]))
            pred_source = "lstm"
        desired = engine.desired_from_prediction(predicted)
        if not dry_run:
            desired = min(desired, max_replicas_live)
        util = cpu_utilization_percent(w[t], current, capacity=capacity)
        intent = engine.emit_scale(
            desired=desired,
            current=current,
            step=t,
            predicted_load=predicted,
            observed_load=float(w[t]),
            source="paks",
            extra={"pred_source": pred_source, "cpu_utilization_pct": util},
            dry_run=dry_run,
        )
        evidence = "LIVE" if not dry_run else "SIMULATED"
        apply_s = (intent.extra or {}).get("apply_latency_s")
        snapshots.append(
            {
                "step": t,
                "policy": "paks-adaptive",
                "observed_load": float(w[t]),
                "predicted_load": predicted,
                "current_replicas": current,
                "desired_replicas": desired,
                "cpu_utilization_pct": util,
                "k8s_path": intent.path,
                "pred_source": pred_source,
                "apply_latency_s": apply_s,
                "evidence": evidence,
            }
        )
        current = desired
    return np.asarray(pods, dtype=float), snapshots, engine.client
