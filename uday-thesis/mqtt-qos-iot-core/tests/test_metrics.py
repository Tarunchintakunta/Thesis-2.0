from analysis.stats_tests import holm, two_proportion_z
from analysis.cost import campaign_operations, estimate_usd, load_pricing
from matching.matcher import match_logs
from simulator.campaign import run_spec
from common.models import ExperimentSpec
from simulator.mock_broker import MockParams


def test_holm_monotone_and_capped():
    adj = holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adj["a"] <= adj["c"] <= adj["b"]
    assert all(0 <= v <= 1 for v in adj.values())


def test_ztest_detects_difference():
    z = two_proportion_z(50, 100, 5, 100, alternative="greater")
    assert z["p"] < 0.001
    z0 = two_proportion_z(0, 100, 0, 100, alternative="greater")
    assert z0["note"] == "degenerate_se0"


def test_latency_percentiles_present():
    params = MockParams(p_network_loss_connected=0.0)
    run = run_spec(
        ExperimentSpec(qos=1, disconnect_s=0, rate_mode="steady", n_devices=1, n_messages=30, seed=3),
        params=params,
    )
    m = match_logs(run.device_log, run.delivered)
    assert m.latency_mean_ms > 0
    assert m.latency_p95_ms >= m.latency_mean_ms
    assert m.latency_p99_ms >= m.latency_p95_ms


def test_cost_estimator_positive_and_priced():
    pricing = load_pricing()
    est = estimate_usd(
        {"publishes_attempted_connected": 1000, "pubacks": 1000, "rule_invocations": 1000, "ddb_puts": 1000},
        duration_s=5000,
        n_devices=5,
        pricing=pricing,
    )
    assert est["usd_raw"] > 0
    assert est["usd_with_safety"] == est["usd_raw"] * pricing["safety_factor"]


def test_formal_ops_exceed_free_tier_messages():
    ops = campaign_operations(5, 1000, 16 * 5, qos_share_1=0.5)
    ft = load_pricing()["free_tier_monthly"]["iot_messages"]
    assert ops["iot_messages_upper"] > ft
