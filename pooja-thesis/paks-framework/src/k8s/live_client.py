"""Live Kubernetes scale client via kubectl (used on the k3s node).

Dry-run remains the default path (`DryRunK8sClient`). This module is only for
the Free-Tier AWS single-node k3s eval (`PAKS_K8S_APPLY=1` on the instance).
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from typing import Any, Dict, List, Optional

from src.k8s.api_shapes import (
    DEFAULT_DEPLOYMENT,
    DEFAULT_NAMESPACE,
    ScaleIntent,
    scale_body,
    scale_patch_path,
)


class LiveKubectlClient:
    """Applies Deployment /scale via kubectl; records TRACE apply latency."""

    def __init__(
        self,
        kubeconfig: Optional[str] = None,
        kubectl_bin: str = "kubectl",
        ready_timeout_s: float = 90.0,
    ):
        if os.environ.get("PAKS_K8S_APPLY", "").strip() not in {"1", "true", "TRUE", "yes"}:
            raise RuntimeError(
                "LiveKubectlClient requires PAKS_K8S_APPLY=1. "
                "Use DryRunK8sClient for local dry-run."
            )
        self.kubectl_bin = kubectl_bin
        self.kubeconfig = kubeconfig or os.environ.get(
            "KUBECONFIG", "/etc/rancher/k3s/k3s.yaml"
        )
        self.ready_timeout_s = float(ready_timeout_s)
        self.operations: List[ScaleIntent] = []
        self.apply_latencies_s: List[float] = []
        self.live_apply = True

    def _env(self) -> Dict[str, str]:
        env = dict(os.environ)
        env["KUBECONFIG"] = self.kubeconfig
        return env

    def _run(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        cmd = [self.kubectl_bin, *args]
        return subprocess.run(
            cmd,
            env=self._env(),
            capture_output=True,
            text=True,
            check=check,
        )

    def get_replicas(self, name: str = DEFAULT_DEPLOYMENT, namespace: str = DEFAULT_NAMESPACE) -> int:
        out = self._run(
            [
                "get",
                "deployment",
                name,
                "-n",
                namespace,
                "-o",
                "jsonpath={.status.readyReplicas}",
            ]
        )
        raw = (out.stdout or "").strip()
        if not raw:
            return 0
        return int(raw)

    def wait_ready(
        self,
        desired: int,
        name: str = DEFAULT_DEPLOYMENT,
        namespace: str = DEFAULT_NAMESPACE,
    ) -> float:
        """Block until readyReplicas == desired; return elapsed seconds (TRACE)."""
        t0 = time.perf_counter()
        deadline = t0 + self.ready_timeout_s
        while time.perf_counter() < deadline:
            ready = self.get_replicas(name=name, namespace=namespace)
            if ready == desired:
                return time.perf_counter() - t0
            time.sleep(0.5)
        # Timeout: still record wall time; caller tags incomplete.
        return time.perf_counter() - t0

    def patch_deployment_scale(
        self,
        replicas: int,
        name: str = DEFAULT_DEPLOYMENT,
        namespace: str = DEFAULT_NAMESPACE,
        current_replicas: Optional[int] = None,
        dry_run: bool = False,
        source: str = "paks",
        step: int = 0,
        predicted_load: Optional[float] = None,
        observed_load: Optional[float] = None,
        extra: Optional[Dict[str, Any]] = None,
        wait: bool = True,
    ) -> ScaleIntent:
        replicas = int(replicas)
        if dry_run:
            # Still allow local schema recording if requested.
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

        # Live mutate: kubectl scale (apps/v1 Deployment scale subresource).
        t_patch = time.perf_counter()
        self._run(
            [
                "scale",
                f"deployment/{name}",
                f"--replicas={replicas}",
                "-n",
                namespace,
            ]
        )
        apply_s = 0.0
        ready_ok = True
        if wait:
            apply_s = self.wait_ready(replicas, name=name, namespace=namespace)
            ready_ok = self.get_replicas(name=name, namespace=namespace) == replicas
        else:
            apply_s = time.perf_counter() - t_patch
        self.apply_latencies_s.append(apply_s)

        meta = dict(extra or {})
        meta.update(
            {
                "apply_latency_s": apply_s,
                "ready_ok": ready_ok,
                "evidence": "LIVE",
            }
        )
        intent = ScaleIntent(
            method="PATCH",
            path=scale_patch_path(name, namespace, dry_run=False),
            body=scale_body(name, namespace, replicas, current_replicas),
            dry_run=False,
            source=source,
            step=step,
            predicted_load=predicted_load,
            observed_load=observed_load,
            extra=meta,
        )
        self.operations.append(intent)
        return intent

    def as_json(self) -> List[Dict[str, Any]]:
        return [op.as_dict() for op in self.operations]

    def latency_summary(self) -> Dict[str, Any]:
        xs = self.apply_latencies_s
        if not xs:
            return {"n": 0, "mean_s": 0.0, "p50_s": 0.0, "max_s": 0.0, "evidence": "LIVE"}
        xs_sorted = sorted(xs)
        mid = xs_sorted[len(xs_sorted) // 2]
        return {
            "n": len(xs),
            "mean_s": float(sum(xs) / len(xs)),
            "p50_s": float(mid),
            "max_s": float(max(xs)),
            "evidence": "LIVE",
        }
