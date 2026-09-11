"""Shared fixtures: small runtime / db / fault configs."""
import random

import pytest


@pytest.fixture
def runtime_cfg():
    return {"memory_mb": 256, "timeout_s": 3.0, "reserved_concurrency": 10, "idle_reclaim_s": [300, 900],
            "max_env_lifetime_s": 7200, "cold_init_median_ms": 380, "cpu_median_ms": 4, "ws_mean_mb": 78,
            "ws_sd_mb": 8}


@pytest.fixture
def db_cfg():
    return {"latency_median_ms": 6, "latency_sigma": 0.35, "read_timeout_s": 2.0}


@pytest.fixture
def fault_cfg():
    return {"permission_denied": {"ops": ["PutItem"]}, "config_error": {},
            "dependency_timeout": {"latency_factor": 8, "p_timeout": 0.35, "p_hang": 0.10, "hang_s": 5.0},
            "resource_exhaustion": {"memory_mb": 128, "ws_mean_mb": 118, "ws_sd_mb": 10, "gc_factor": 1.8}}


@pytest.fixture
def emulator(runtime_cfg, db_cfg, fault_cfg):
    from logad.collect.runtime import LambdaEmulator

    return LambdaEmulator(runtime_cfg, db_cfg, fault_cfg, random.Random(3), start=1_780_272_000.0)


POST = {"routeKey": "POST /orders", "body": '{"order_id": "ord-000000000001", "items": 2, "amount_cents": 500}'}
GET_ONE = {"routeKey": "GET /orders/{id}", "pathParameters": {"id": "ord-000000000001"}}
HEALTH = {"routeKey": "GET /health"}
