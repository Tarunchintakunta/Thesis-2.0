"""The mock must behave like the platform in the ways the pipeline depends on."""
import statistics

from coldstart.backends import FUNCTIONS, MockBackend
from coldstart.mock import MockLambda, VirtualClock, load_model
from coldstart.report_parser import parse_log_text

PAYLOAD = {"seed": "x", "iterations": 10, "items": [1, 2]}


def lam(seed=1):
    return MockLambda(FUNCTIONS, clock=VirtualClock(), seed=seed)


def report(res):
    return parse_log_text(res["log_tail"])[-1]


def test_first_call_cold_second_warm():
    m = lam()
    assert report(m.invoke("python-optimised", PAYLOAD)).cold
    m.clock.advance(1)
    assert not report(m.invoke("python-optimised", PAYLOAD)).cold


def test_force_cold_and_memory_change_give_new_environment():
    m = lam()
    m.invoke("java-default", PAYLOAD)
    m.clock.advance(1)
    m.force_cold("java-default")
    assert report(m.invoke("java-default", PAYLOAD)).cold
    m.clock.advance(1)
    m.set_memory("java-default", 512)
    r = report(m.invoke("java-default", PAYLOAD))
    assert r.cold and r.memory_mb == 512


def test_long_idle_gap_reclaims_environment():
    m = lam()
    m.invoke("nodejs-optimised", PAYLOAD)
    m.clock.advance(6 * 3600)  # far beyond any sampled idle lifetime
    assert report(m.invoke("nodejs-optimised", PAYLOAD)).cold


def test_concurrent_requests_need_their_own_environments():
    m = lam()
    m.invoke("python-optimised", PAYLOAD)
    m.clock.advance(1)
    burst = m.invoke_concurrent("python-optimised", PAYLOAD, 10)
    colds = [report(r).cold for r in burst]
    assert colds.count(False) == 1 and colds.count(True) == 9  # one warm env, nine new ones


def test_default_package_has_longer_init_than_optimised():
    m = lam(3)
    d = [m.init_ms("python", "default", 1024) for _ in range(300)]
    o = [m.init_ms("python", "optimised", 1024) for _ in range(300)]
    assert statistics.median(d) > statistics.median(o)


def test_more_memory_shortens_duration_until_one_vcpu():
    m = lam(4)
    small = statistics.median(m.duration_ms("python", 128, False) for _ in range(200))
    one = statistics.median(m.duration_ms("python", 1769, False) for _ in range(200))
    big = statistics.median(m.duration_ms("python", 3008, False) for _ in range(200))
    assert small > 5 * one
    assert abs(big - one) / one < 0.1


def test_warmer_keeps_environment_alive():
    b = MockBackend(seed=5)
    b.invoke("warm-target", PAYLOAD)
    b.invoke("warm-control", PAYLOAD)
    b.enable_warmer("warm-target", 300)
    b.sleep(3 * 3600)
    assert not report(b.invoke("warm-target", PAYLOAD)).cold
    assert report(b.invoke("warm-control", PAYLOAD)).cold


def test_logs_have_start_end_report_and_warm_pings():
    b = MockBackend(seed=6)
    b.enable_warmer("warm-target", 300)
    b.sleep(1800)
    msgs = [e["message"] for e in b.lam.logs]
    assert any(x.startswith("START") for x in msgs) and any(x.startswith("REPORT") for x in msgs)
    assert sum(x.startswith("REPORT") for x in msgs) >= 5  # about one ping every 5 minutes
    assert all(e["log_group"].endswith("warm-target") for e in b.lam.logs)


def test_same_seed_same_numbers():
    a, b = lam(9), lam(9)
    assert a.invoke("java-optimised", PAYLOAD)["rtt_ms"] == b.invoke("java-optimised", PAYLOAD)["rtt_ms"]


def test_model_file_is_labelled_synthetic():
    assert "SYNTHETIC" in load_model()["label"]
