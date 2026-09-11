import math

import pytest

from coldstart.cost_model import (
    billed_ms,
    cost_per_1k,
    effective_billed_ms,
    invocation_cost,
    load_prices,
    warming_cost_per_1k,
)

PRICES = load_prices(None)


def test_billed_rounds_up_to_ms():
    assert billed_ms(12.01) == 13
    assert billed_ms(12.0) == 12


def test_billed_adds_init_only_when_asked():
    assert billed_ms(10.2, init_ms=200.3, bill_init=True) == 211
    assert billed_ms(10.2, init_ms=200.3, bill_init=False) == 11
    assert billed_ms(10.2, init_ms=None, bill_init=True) == 11


def test_one_gb_second_on_arm():
    # 1000 ms at 1024 MB = 1 GB-s
    c = invocation_cost(1000, 1024, "arm64", PRICES)
    assert c == pytest.approx(PRICES["per_gb_second"]["arm64"] + PRICES["per_request"])


def test_arm_is_cheaper_than_x86_for_same_billed_time():
    assert invocation_cost(100, 512, "arm64", PRICES) < invocation_cost(100, 512, "x86_64", PRICES)


def test_cost_per_1k_is_mean_times_1000():
    vals = [10, 20, 30]
    expect = sum(invocation_cost(v, 256, "arm64", PRICES) for v in vals) / 3 * 1000
    assert cost_per_1k(vals, 256, "arm64", PRICES) == pytest.approx(expect)
    assert math.isnan(cost_per_1k([], 256, "arm64", PRICES))


def test_request_charge_floor():
    # even a 1 ms invocation pays the request charge: $0.20 per million = $0.0002 per 1k
    assert cost_per_1k([1], 128, "arm64", PRICES) > 0.0002


def test_warming_cost_scales_with_ping_rate():
    a = warming_cost_per_1k(6, 2, 512, "arm64", PRICES, invocations_per_hour=60)
    b = warming_cost_per_1k(12, 2, 512, "arm64", PRICES, invocations_per_hour=60)
    assert b == pytest.approx(2 * a)
    assert warming_cost_per_1k(6, 2, 512, "arm64", PRICES, invocations_per_hour=0) == math.inf


def test_effective_billed_adds_init_only_when_missing():
    # old REPORT format: billed covers only the handler -> add the init time
    assert effective_billed_ms(13, 12.3, 245.6, True) == 13 + 246
    # INIT already inside Billed Duration (new billing) -> keep as is
    assert effective_billed_ms(258, 12.3, 245.6, True) == 258
    # warm call or init billing switched off
    assert effective_billed_ms(13, 12.3, None, True) == 13
    assert effective_billed_ms(13, 12.3, float("nan"), True) == 13
    assert effective_billed_ms(13, 12.3, 245.6, False) == 13


def test_pricing_yaml_loads(tmp_path):
    p = tmp_path / "p.yaml"
    p.write_text("as_of: test\nper_request: 0.000001\n")
    prices = load_prices(p)
    assert prices["as_of"] == "test" and prices["per_request"] == 0.000001
    assert "arm64" in prices["per_gb_second"]
