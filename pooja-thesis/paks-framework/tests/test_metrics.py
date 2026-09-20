"""Formal metric suite tagging."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.eval.metrics import (
    EVIDENCE_GLOSSARY,
    evaluate_policy,
    mae,
    rmse,
    sla_compliance,
)


def test_mae_rmse():
    y = np.array([1.0, 2.0, 3.0])
    p = np.array([1.0, 2.0, 5.0])
    assert abs(mae(y, p) - (2.0 / 3.0)) < 1e-12
    assert abs(rmse(y, p) - (4.0 / 3.0) ** 0.5) < 1e-9


def test_evaluate_policy_tags_simulated_loop():
    w = np.array([10.0, 20.0, 15.0, 12.0])
    pods = np.array([2.0, 2.0, 3.0, 2.0])
    row = evaluate_policy(
        w,
        pods,
        capacity=10.0,
        bin_seconds=300.0,
        y_true=w[1:],
        y_pred=w[:-1],
        policy="paks-adaptive",
        prediction_evidence="TRACE",
        loop_evidence="SIMULATED",
    )
    assert row["policy"] == "paks-adaptive"
    assert row["live_k8s"] is False
    assert row["live_cloudwatch"] is False
    assert row["evidence_loop"] == "SIMULATED"
    assert row["evidence_cost"] == "SIMULATED"
    assert row["evidence_prediction"] == "TRACE"
    for key in (
        "mae",
        "rmse",
        "cpu_util_mean",
        "response_time_ms_mean",
        "throughput_mean",
        "scaling_latency_s_mean",
        "cost_usd",
        "sla_compliance",
        "availability_sim",
    ):
        assert key in row
        assert np.isfinite(row[key])
    assert 0.0 <= sla_compliance(w, pods, 10.0) <= 1.0
    assert "TRACE" in EVIDENCE_GLOSSARY
    assert "SIMULATED" in EVIDENCE_GLOSSARY
    assert "LIVE" in EVIDENCE_GLOSSARY
