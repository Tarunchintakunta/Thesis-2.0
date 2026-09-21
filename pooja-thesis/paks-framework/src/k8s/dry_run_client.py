"""Dry-run Kubernetes client (default). Records Scale PATCH bodies only.

Live mutation belongs in `LiveKubectlClient` (AWS k3s / PAKS_K8S_APPLY=1).
This class always refuses non-dry-run patches so local drivers stay safe.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.k8s.api_shapes import (
    DEFAULT_DEPLOYMENT,
    DEFAULT_NAMESPACE,
    ScaleIntent,
    scale_body,
    scale_patch_path,
)


class DryRunK8sClient:
    """Records apps/v1 Deployment /scale PATCH bodies (dry-run only)."""

    def __init__(self, live_apply: Optional[bool] = None):
        # live_apply retained for API compatibility; DryRunK8sClient never mutates.
        self.live_apply = False
        if live_apply:
            raise RuntimeError(
                "DryRunK8sClient cannot live-apply. Use LiveKubectlClient with "
                "PAKS_K8S_APPLY=1 on the k3s node (see scripts/run_live_aws_k8s.py)."
            )
        self.operations: List[ScaleIntent] = []

    def patch_deployment_scale(
        self,
        replicas: int,
        name: str = DEFAULT_DEPLOYMENT,
        namespace: str = DEFAULT_NAMESPACE,
        current_replicas: Optional[int] = None,
        dry_run: bool = True,
        source: str = "paks",
        step: int = 0,
        predicted_load: Optional[float] = None,
        observed_load: Optional[float] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> ScaleIntent:
        if not dry_run:
            raise RuntimeError(
                "Refusing non-dry-run Kubernetes mutate on DryRunK8sClient. "
                "Use LiveKubectlClient for live apply."
            )
        intent = ScaleIntent(
            method="PATCH",
            path=scale_patch_path(name, namespace, dry_run=True),
            body=scale_body(name, namespace, replicas, current_replicas),
            dry_run=True,
            source=source,
            step=step,
            predicted_load=predicted_load,
            observed_load=observed_load,
            extra=extra or {},
        )
        self.operations.append(intent)
        return intent

    def as_json(self) -> List[Dict[str, Any]]:
        return [op.as_dict() for op in self.operations]
