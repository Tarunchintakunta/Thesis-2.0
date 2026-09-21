"""K8s API-shaped PAKS engine vs HPA (dry-run only)."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.k8s.adaptive_engine import (
    AdaptiveScalingEngine,
    hpa_desired_from_current,
    replicas_for_load,
    run_paks_k8s,
    run_reactive_hpa_k8s,
)
from src.k8s.api_shapes import hpa_spec, scale_body, scale_patch_path
from src.k8s.dry_run_client import DryRunK8sClient


def test_hpa_spec_is_autoscaling_v2():
    spec = hpa_spec(name="demo")
    assert spec["apiVersion"] == "autoscaling/v2"
    assert spec["kind"] == "HorizontalPodAutoscaler"
    metric = spec["spec"]["metrics"][0]
    assert metric["type"] == "Resource"
    assert metric["resource"]["name"] == "cpu"
    assert metric["resource"]["target"]["averageUtilization"] == 70


def test_scale_patch_path_dry_run_query():
    path = scale_patch_path("paks-demo", "default", dry_run=True)
    assert path.startswith("/apis/apps/v1/namespaces/default/deployments/paks-demo/scale")
    assert "dryRun=All" in path


def test_scale_body_kind():
    body = scale_body("paks-demo", "default", replicas=4, current_replicas=3)
    assert body["apiVersion"] == "autoscaling/v1"
    assert body["kind"] == "Scale"
    assert body["spec"]["replicas"] == 4


def test_hpa_replica_formula():
    # 2 replicas at 140% of 70% target → ceil(2 * 140/70) = 4
    assert hpa_desired_from_current(2, 140, 70) == 4


def test_dry_run_records_patch_and_refuses_live():
    client = DryRunK8sClient()
    intent = client.patch_deployment_scale(replicas=5, step=1, observed_load=42.0)
    assert intent.dry_run is True
    assert intent.method == "PATCH"
    assert len(client.operations) == 1
    with pytest.raises(RuntimeError, match="dry-run"):
        client.patch_deployment_scale(replicas=5, dry_run=False)


def test_dry_run_client_refuses_live_flag():
    with pytest.raises(RuntimeError, match="cannot live-apply"):
        DryRunK8sClient(live_apply=True)


def test_live_client_requires_env(monkeypatch):
    monkeypatch.delenv("PAKS_K8S_APPLY", raising=False)
    from src.k8s.live_client import LiveKubectlClient

    with pytest.raises(RuntimeError, match="PAKS_K8S_APPLY"):
        LiveKubectlClient()


def test_hpa_and_paks_emit_equal_length_pods():
    workload = np.array([20.0, 25.0, 80.0, 90.0, 40.0, 30.0, 25.0] + [22.0] * 10)

    def pred(window):
        return float(window[-1] * 1.1)

    hpa_pods, hpa_snap, hpa_c = run_reactive_hpa_k8s(workload)
    paks_pods, paks_snap, paks_c = run_paks_k8s(workload, pred, lookback=3)
    assert len(hpa_pods) == len(workload)
    assert len(paks_pods) == len(workload)
    assert hpa_c.operations[0].source == "hpa"
    assert paks_c.operations[0].source == "paks"
    assert "hpa_status" in hpa_c.operations[0].extra
    assert hpa_snap[0]["evidence"] == "SIMULATED"


def test_engine_desired_uses_safety_buffer():
    eng = AdaptiveScalingEngine(safety_buffer=1.0)
    a = eng.desired_from_prediction(70.0)
    eng.safety_buffer = 2.0
    b = eng.desired_from_prediction(70.0)
    assert b >= a
    assert replicas_for_load(10.0) >= 1
