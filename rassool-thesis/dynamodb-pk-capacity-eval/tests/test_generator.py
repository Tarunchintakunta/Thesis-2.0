"""Zipf sampler, key designs and workload profiles."""
import numpy as np
import pytest

from workloads.generator import keys
from workloads.generator.profiles import PROFILES, duration_s, op_plan, planned_ops, send_times
from workloads.generator.zipf import Zipf, calibrate, top_share


def test_calibration_hits_ninety_ten():
    s = calibrate(20_000)
    assert top_share(20_000, s) == pytest.approx(0.90, abs=1e-3)


def test_sampled_share_matches_the_cdf():
    z = Zipf(20_000, calibrate(20_000))
    idx, rank = z.sample(np.random.default_rng(1), 200_000)
    hot = np.sort(z.perm[:2_000])  # the hottest 10% of order indexes
    share = np.isin(idx, hot).mean()
    assert share == pytest.approx(0.90, abs=0.01)
    assert rank.min() == 0 and idx.max() < 20_000


def test_hot_keys_are_scattered_not_the_first_orders():
    z = Zipf(20_000, 1.0)
    assert set(z.perm[:10]) != set(range(10))


def test_uniform_would_fail_the_skew_rule():
    assert top_share(20_000, 0.0) == pytest.approx(0.10)


def test_customer_mapping_gives_100_orders_each():
    counts = np.bincount([int(keys.customer_of(i)[1:]) for i in range(keys.N_ORDERS)], minlength=keys.N_CUSTOMERS)
    assert counts.min() == counts.max() == 100


def test_key_designs():
    assert keys.key_for("K1", 42) == {"orderId": "o0000042"}
    k2 = keys.key_for("K2", 42)
    assert set(k2) == {"customerId", "orderTs"} and k2["orderTs"].endswith("Z")
    assert keys.key_for("K3", 42, 7) == {"shardKey": "o0000042#7"}
    assert len(keys.all_shard_keys(42, 10)) == 10
    with pytest.raises(ValueError):
        keys.key_for("K9", 1)


@pytest.mark.parametrize("kb", [1, 8, 32])
@pytest.mark.parametrize("design", keys.DESIGNS)
def test_items_fit_their_write_unit_budget(design, kb):
    item = keys.make_item(design, 123456, kb, version=3, shard=4)
    size = keys.item_size(item)
    assert kb * 1024 - 64 <= size <= kb * 1024  # ceil(size / 1 KB) WCU == kb
    for attr in ("orderId", "customerId", "orderTs", "version", "payload"):
        assert attr in item


def test_profiles_match_the_master_prompt():
    assert PROFILES["W1"]["read_fraction"] == 0.95
    assert PROFILES["W2"]["read_fraction"] == 0.30
    assert PROFILES["W3"]["read_fraction"] == 0.50
    assert PROFILES["W4"]["cycle"] == [(200, 60), (1000, 30)]
    assert planned_ops(PROFILES["W1"]) == 18_000
    assert planned_ops(PROFILES["W4"]) == 2 * (12_000 + 30_000)
    assert duration_s(PROFILES["W4"]) == 180


def test_send_times_are_open_loop_and_monotonic():
    t = send_times(PROFILES["W4"])
    assert np.all(np.diff(t) > 0)
    assert t[0] == 0 and t[-1] < 180
    gaps = np.diff(t[:12_000])
    assert gaps == pytest.approx(np.full_like(gaps, 1 / 200))


def test_op_plan_is_reproducible_and_scaled():
    z = Zipf(20_000, 1.0)
    a = op_plan(PROFILES["W3"], z, seed=7, scale=0.1)
    b = op_plan(PROFILES["W3"], z, seed=7, scale=0.1)
    assert np.array_equal(a["order"], b["order"]) and len(a["t"]) == 1800
    assert a["read"].mean() == pytest.approx(0.5, abs=0.05)
