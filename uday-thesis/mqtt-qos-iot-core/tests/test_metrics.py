from analysis.cost import campaign_operations, estimate_usd, load_pricing
from analysis.stats_tests import holm, two_proportion_z
from common.models import ExperimentSpec
from matching.matcher import match_logs
from simulator.campaign import run_spec
from simulator.mock_broker import MockParams


def test_holm_monotone_and_capped():
    adj = holm({"a": 0.04, "b": 0.01, "c": 0.03})
    vals = list(adj.values())
    assert all(0.0 <= v <= 1.0 for v in vals)
    assert vals == sorted(vals)


def test_ztest_detects_difference():
    z = two_proportion_z(80, 100, 20, 100, alternative="greater")
    assert z["p"] < 0.01
    z0 = two_proportion_z(50, 100, 50, 100, alternative="greater")
    assert z0["p"] > 0.4


def test_latency_percentiles_present():
    params = MockParams(p_network_loss_connected=0.0)
    run = run_spec(
        ExperimentSpec(
            qos=0,
            disconnect_s=0,
            rate_mode="steady",
            n_devices=1,
            n_messages=20,
            seed=1,
        ),
        params=params,
    )
    m = match_logs(run.device_log, run.delivered)
    assert m.latency_mean_ms == m.latency_mean_ms  # not NaN
    assert m.latency_p95_ms >= m.latency_mean_ms or m.latency_p95_ms == m.latency_mean_ms
    assert m.latency_p99_ms >= m.latency_p95_ms or m.latency_p99_ms == m.latency_p95_ms


def test_cost_estimator_positive_and_priced():
    pricing = load_pricing()
    est = estimate_usd(
        {
            "publishes_attempted_connected": 1000,
            "pubacks": 500,
            "reached_broker": 1000,
            "rule_invocations": 1000,
            "ddb_puts": 1000,
        },
        duration_s=1000.0,
        n_devices=5,
        pricing=pricing,
    )
    assert est["usd_raw"] > 0
    assert est["usd_with_safety"] >= est["usd_raw"]


def test_formal_ops_exceed_free_tier_messages():
    ops = campaign_operations(n_devices=5, n_messages=1000, n_cells=80, qos_share_1=0.5)
    ft = load_pricing()["free_tier_monthly"]
    assert ops["iot_messages_upper"] > ft["iot_messages"]
