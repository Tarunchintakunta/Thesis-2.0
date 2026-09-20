"""Dry-run Kubernetes client (default). Never deploys a cluster this pass.

If the official Python client and a kubeconfig are present, Scale patches can
be issued with dryRun=['All'] (no object mutation). Live apply requires
PAKS_K8S_APPLY=1, which this pass does not set.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from src.k8s.api_shapes import (
    DEFAULT_DEPLOYMENT,
    DEFAULT_NAMESPACE,
    ScaleIntent,
    scale_body,
    scale_patch_path,
)


class DryRunK8sClient:
    """Records apps/v1 Deployment /scale PATCH bodies."""

    def __init__(self, live_apply: Optional[bool] = None):
        env = os.environ.get("PAKS_K8S_APPLY", "").strip() in {"1", "true", "TRUE", "yes"}
        self.live_apply = bool(env if live_apply is None else live_apply)
        self.operations: List[ScaleIntent] = []
        self._api = None
        if self.live_apply:
            raise RuntimeError(
                "PAKS_K8S_APPLY is set, but this CA2 pass forbids live cluster "
                "mutation / AWS-K8s deploy. Unset the variable and use dry-run."
            )

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
        if not dry_run or self.live_apply:
            raise RuntimeError("Refusing non-dry-run Kubernetes mutate in this pass.")
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
