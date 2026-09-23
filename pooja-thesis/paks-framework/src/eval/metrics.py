
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

import numpy as np

# Assumed unit economics / service times — SIMULATED, not CloudWatch / billing.
USD_PER_POD_HOUR = 0.04
BASE_SERVICE_MS = 50.0
# Default control interval for GCT v1 bins; overridden by meta["bin_seconds"].
DEFAULT_BIN_SECONDS = 300.0


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    err = np.asarray(y_true, dtype=float) - np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean(err ** 2)))


def mean_cpu_util(workload: np.ndarray, pods: np.ndarray, capacity: float) -> float:
    return float(np.mean(workload / (np.maximum(pods, 1.0) * capacity)))


def mean_mem_util(mem: Optional[np.ndarray], pods: np.ndarray, mem_capacity: float) -> Optional[float]:
    if mem is None:
        return None
    return float(np.mean(np.asarray(mem) / (np.maximum(pods, 1.0) * mem_capacity)))


def throughput(workload: np.ndarray, pods: np.ndarray, capacity: float) -> np.ndarray:
    return np.minimum(workload, pods * capacity)


def response_time_ms(workload: np.ndarray, pods: np.ndarray, capacity: float, base_ms: float = BASE_SERVICE_MS) -> np.ndarray:
    """M/M/1-style proxy: base / (1 - util), capped. NOT live request traces."""
    util = workload / (np.maximum(pods, 1.0) * capacity)
    util = np.clip(util, 0.0, 0.99)
    return base_ms / (1.0 - util)


def sla_violations(workload: np.ndarray, pods: np.ndarray, capacity: float) -> int:
    needed = np.ceil(workload / capacity)
    return int(np.sum(pods < needed))


def sla_compliance(workload: np.ndarray, pods: np.ndarray, capacity: float) -> float:
    n = max(1, len(workload))
    return 1.0 - sla_violations(workload, pods, capacity) / n


def scaling_events(pods: np.ndarray) -> int:
    if len(pods) < 2:
        return 0
    return int(np.sum(np.diff(pods) != 0))


def simulated_cost_usd(pods: np.ndarray, bin_seconds: float, usd_per_pod_hour: float = USD_PER_POD_HOUR) -> float:
    pod_hours = float(np.sum(pods) * (bin_seconds / 3600.0))
    return pod_hours * usd_per_pod_hour


def simulated_scaling_latency_s(pods: np.ndarray, bin_seconds: float) -> Dict[str, float]:
    """Each replica change is assumed to take one control interval to apply.

    Live Kubernetes would measure time from Scale PATCH to Ready replicas
    (kubelet). That number is not available in this dry-run.
    """
    events = scaling_events(pods)
    return {
        "assumed_interval_s": float(bin_seconds),
        "n_scaling_events": float(events),
        "mean_scale_apply_s": float(bin_seconds) if events else float("nan"),
        "evidence": "SIMULATED_ASSUMED_INTERVAL",
    }


def evaluate_policy(
    workload: np.ndarray,
    pods: np.ndarray,
    capacity: float,
    bin_seconds: float = DEFAULT_BIN_SECONDS,
    mem: Optional[np.ndarray] = None,
    mem_capacity: float = 8.0,
    y_true: Optional[np.ndarray] = None,
    y_pred: Optional[np.ndarray] = None,
    policy: str = "",
    prediction_evidence: str = "TRACE",
    loop_evidence: str = "SIMULATED",
) -> Dict[str, Any]:
    workload = np.asarray(workload, dtype=float)
    pods = np.asarray(pods, dtype=float)
    tp = throughput(workload, pods, capacity)
    rt = response_time_ms(workload, pods, capacity)
    row: Dict[str, Any] = {
        "policy": policy,
        "n_steps": int(workload.size),
        "mae": mae(y_true, y_pred) if y_true is not None and y_pred is not None else np.nan,
        "rmse": rmse(y_true, y_pred) if y_true is not None and y_pred is not None else np.nan,
        "cpu_util_mean": mean_cpu_util(workload, pods, capacity),
        "mem_util_mean": mean_mem_util(mem, pods, mem_capacity),
        "response_time_ms_mean": float(np.mean(rt)),
        "throughput_mean": float(np.mean(tp)),
        "throughput_sum": float(np.sum(tp)),
        "scaling_latency_s_mean": float(bin_seconds) if scaling_events(pods) else float("nan"),
        "cost_usd": simulated_cost_usd(pods, bin_seconds),
        "sla_violations": sla_violations(workload, pods, capacity),
        "sla_compliance": sla_compliance(workload, pods, capacity),
        "availability_sim": sla_compliance(workload, pods, capacity),
        "scaling_events": scaling_events(pods),
        "mean_replicas": float(np.mean(pods)),
        "bin_seconds": float(bin_seconds),
        "usd_per_pod_hour_assumed": USD_PER_POD_HOUR,
        "evidence_prediction": prediction_evidence if y_true is not None else "n/a",
        "evidence_loop": loop_evidence,
        "evidence_cost": "SIMULATED",
        "evidence_latency": "SIMULATED",
        "evidence_response_throughput": "SIMULATED",
        "live_k8s": False,
        "live_cloudwatch": False,
    }
    return row


EVIDENCE_GLOSSARY: Mapping[str, str] = {
    "TRACE": "Computed from public cluster-trace-derived series (see PROVENANCE.md).",
    "SIMULATED": "Discrete-time model (capacity mapping / queue proxy / unit price). Not kubelet, not billing, not CloudWatch.",
    "LIVE": "Collected from a running Kubernetes cluster and/or CloudWatch (see formal_k8s_live_aws.json).",
}
