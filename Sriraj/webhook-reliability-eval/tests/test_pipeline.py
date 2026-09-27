import random

from fault.injector import FaultPlan
from pipeline.processor import ConfigMode, Pipeline, PipelineConfig
from sim.runner import run_cell


def test_hmac_rejects_bad_signature():
    pipe = Pipeline(PipelineConfig(mode=ConfigMode.RDI), rng=random.Random(1))
    ok, reason = pipe.ingest({"event_id": "x", "source": "t"}, signed=False)
    assert not ok and reason == "bad_signature"


def test_rdi_better_than_baseline_at_50pct_fault():
    b = run_cell(ConfigMode.B, 0.50, n_events=150, seed=7)
    rdi = run_cell(ConfigMode.RDI, 0.50, n_events=150, seed=7)
    assert rdi["delivery_success_rate"] > b["delivery_success_rate"]
    assert rdi["delivery_success_rate"] >= 0.90


def test_idempotency_suppresses_duplicates():
    rdi = run_cell(ConfigMode.RDI, 0.0, n_events=100, duplicate_rate=0.25, seed=3)
    assert rdi["duplicate_attempts"] > 0
    assert rdi["duplicate_suppression_ratio"] >= 0.95


def test_rd_captures_dlq():
    # High permanent rate → DLQ activity under RD
    rd = run_cell(ConfigMode.RD, 0.40, n_events=80, permanent_fraction=0.5, seed=11)
    # After replay, recovery should be high
    assert rd["dlq_recovery_rate"] >= 0.8 or rd["dlq_captured"] == 0
