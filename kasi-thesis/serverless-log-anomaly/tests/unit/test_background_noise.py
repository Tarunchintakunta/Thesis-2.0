import random

import pandas as pd

from logad.collect.runtime import LambdaEmulator
from logad.inject.schedule import Injection
from logad.pipeline import certify_clean
from tests.conftest import POST

T0 = 1_780_272_000.0


def test_background_throttling_is_off_by_default(emulator):
    for i in range(300):
        emulator.invoke(T0 + i, POST)
    assert {m["status"] for m in emulator.metrics} == {201}


def test_background_throttling_returns_500s(runtime_cfg, db_cfg, fault_cfg):
    em = LambdaEmulator(runtime_cfg, {**db_cfg, "p_throttle": 0.2}, fault_cfg, random.Random(5), start=T0)
    for i in range(300):
        em.invoke(T0 + i, POST)
    statuses = [m["status"] for m in em.metrics]
    assert 30 < statuses.count(500) < 100
    assert any("ProvisionedThroughputExceededException" in line for _, line in em.lines)


def test_certification_ignores_background_throttles_but_not_faults():
    metrics = pd.DataFrame({"status": [201, 500, 201]})
    msgs = ['[ERROR] x {"error_type": "ProvisionedThroughputExceededException"}', "START RequestId: <RID>"]
    cert = certify_clean(msgs, metrics, [], a_end=100.0)
    assert cert["certified"] and cert["http_5xx_in_A"] == 1 and cert["background_throttle_lines_in_A"] == 1

    dirty = certify_clean(msgs + ["<TS> <RID> Task timed out after 3.00 seconds"], metrics, [], a_end=100.0)
    assert not dirty["certified"]
    overlap = certify_clean(msgs, metrics, [Injection(0, 0, "config_error", 50, 150)], a_end=100.0)
    assert not overlap["certified"]
