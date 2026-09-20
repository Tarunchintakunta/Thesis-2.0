from common.models import ExperimentSpec
from matching.matcher import match_logs
from simulator.campaign import run_spec
from simulator.mock_broker import MockParams


def _spec(**kwargs) -> ExperimentSpec:
    base = dict(qos=0, disconnect_s=0, rate_mode="steady", n_devices=2, n_messages=20, replication=1, seed=7)
    base.update(kwargs)
    return ExperimentSpec(**base)


def test_qos0_disconnect_loses_messages():
    params = MockParams(p_network_loss_connected=0.0, p_rule_fail=0.0)
    lost = run_spec(_spec(qos=0, disconnect_s=60), params=params)
    m = match_logs(lost.device_log, lost.delivered)
    assert m.n_published == 40
    assert m.n_lost > 0
    assert m.n_duplicate_ids == 0


def test_qos1_disconnect_recovers_more_than_qos0():
    params = MockParams(p_network_loss_connected=0.0, p_rule_fail=0.0, p_inflight_already_acked=1.0)
    s0 = run_spec(_spec(qos=0, disconnect_s=60, seed=11), params=params)
    s1 = run_spec(_spec(qos=1, disconnect_s=60, seed=11), params=params)
    m0 = match_logs(s0.device_log, s0.delivered)
    m1 = match_logs(s1.device_log, s1.delivered)
    assert m0.loss_rate > m1.loss_rate
    assert m1.n_lost == 0 or m1.loss_rate < 0.05


def test_qos0_no_disconnect_near_zero_loss():
    params = MockParams(p_network_loss_connected=0.0, p_rule_fail=0.0)
    run = run_spec(_spec(qos=0, disconnect_s=0), params=params)
    m = match_logs(run.device_log, run.delivered)
    assert m.n_lost == 0
    assert run.manifest.backend == "mock"
    assert "not an AWS" in run.manifest.measurement_kind


def test_device_log_written_for_every_intended_message():
    run = run_spec(_spec(qos=1, disconnect_s=15, n_messages=12, n_devices=3))
    assert len(run.device_log) == 36
    ids = [r["msg_id"] for r in run.device_log]
    assert len(ids) == len(set(ids))
    assert all(r["ts_log_ms"] == r["ts_intended_publish_ms"] for r in run.device_log)


def test_live_backend_blocked():
    spec = _spec(backend="live")
    try:
        run_spec(spec)
        raise AssertionError("should have blocked live")
    except RuntimeError as exc:
        assert "blocked" in str(exc).lower()


def test_qos1_connected_network_loss_is_retried():
    params = MockParams(p_network_loss_connected=0.3, p_rule_fail=0.0, p_inflight_already_acked=1.0)
    run = run_spec(_spec(qos=1, disconnect_s=0, n_messages=40, n_devices=1, seed=99), params=params)
    m = match_logs(run.device_log, run.delivered)
    assert m.n_lost == 0


def test_qos1_disconnect_can_duplicate_inflight():
    params = MockParams(p_network_loss_connected=0.0, p_rule_fail=0.0, p_inflight_already_acked=0.0)
    run = run_spec(_spec(qos=1, disconnect_s=60, n_devices=3, n_messages=24, seed=5), params=params)
    m = match_logs(run.device_log, run.delivered)
    assert m.n_duplicate_ids >= 1
