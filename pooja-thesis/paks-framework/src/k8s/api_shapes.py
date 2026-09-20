"""Kubernetes API object shapes used by PAKS vs HPA (no live cluster required).

Shapes follow autoscaling/v2 HorizontalPodAutoscaler and the apps/v1
Deployment scale subresource closely enough to emit dry-run PATCH bodies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


DEFAULT_NAMESPACE = "default"
DEFAULT_DEPLOYMENT = "paks-demo"
HPA_API = "autoscaling/v2"
SCALE_API = "autoscaling/v1"
APPS_API = "apps/v1"
TARGET_CPU_UTILIZATION = 70  # HPA spec.metrics[].resource.target.averageUtilization


def hpa_spec(
    name: str = DEFAULT_DEPLOYMENT,
    namespace: str = DEFAULT_NAMESPACE,
    min_replicas: int = 1,
    max_replicas: int = 100,
    target_cpu_utilization: int = TARGET_CPU_UTILIZATION,
) -> Dict[str, Any]:
    return {
        "apiVersion": HPA_API,
        "kind": "HorizontalPodAutoscaler",
        "metadata": {"name": f"{name}-hpa", "namespace": namespace},
        "spec": {
            "scaleTargetRef": {
                "apiVersion": APPS_API,
                "kind": "Deployment",
                "name": name,
            },
            "minReplicas": int(min_replicas),
            "maxReplicas": int(max_replicas),
            "metrics": [
                {
                    "type": "Resource",
                    "resource": {
                        "name": "cpu",
                        "target": {
                            "type": "Utilization",
                            "averageUtilization": int(target_cpu_utilization),
                        },
                    },
                }
            ],
        },
    }


def hpa_status(
    current_replicas: int,
    desired_replicas: int,
    current_cpu_utilization: Optional[int],
) -> Dict[str, Any]:
    current_metrics: List[Dict[str, Any]] = []
    if current_cpu_utilization is not None:
        current_metrics.append(
            {
                "type": "Resource",
                "resource": {
                    "name": "cpu",
                    "current": {"averageUtilization": int(current_cpu_utilization)},
                },
            }
        )
    return {
        "currentReplicas": int(current_replicas),
        "desiredReplicas": int(desired_replicas),
        "currentMetrics": current_metrics,
    }


def scale_body(
    name: str,
    namespace: str,
    replicas: int,
    current_replicas: Optional[int] = None,
) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "apiVersion": SCALE_API,
        "kind": "Scale",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {"replicas": int(replicas)},
    }
    if current_replicas is not None:
        body["status"] = {
            "replicas": int(current_replicas),
            "selector": f"app={name}",
        }
    return body


def scale_patch_path(name: str, namespace: str, dry_run: bool = True) -> str:
    q = "?dryRun=All" if dry_run else ""
    return f"/apis/{APPS_API}/namespaces/{namespace}/deployments/{name}/scale{q}"


@dataclass
class ScaleIntent:
    """One intended Kubernetes scale mutation (dry-run unless explicitly applied)."""

    method: str
    path: str
    body: Dict[str, Any]
    dry_run: bool = True
    source: str = "paks"
    step: int = 0
    predicted_load: Optional[float] = None
    observed_load: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "method": self.method,
            "path": self.path,
            "body": self.body,
            "dry_run": self.dry_run,
            "source": self.source,
            "step": self.step,
            "predicted_load": self.predicted_load,
            "observed_load": self.observed_load,
            "extra": self.extra,
        }
