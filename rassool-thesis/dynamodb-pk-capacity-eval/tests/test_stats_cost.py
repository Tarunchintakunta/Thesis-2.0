"""Stats and cost model on small hand-made batch tables (test inputs, not results)."""
import numpy as np
import pandas as pd
import pytest

from analysis import stats
from analysis.cost_model import (
    add_costs,
    consumed_equivalent_cost,
    load_prices,
    on_demand_cost,
    per_10k,
    provisioned_cost,
)

PRICES = load_prices()


def cells(effect_key=0.0, effect_cap=0.0, interaction=0.0, n=30, noise=1.0, seed=0, skew=False):
    rng = np.random.default_rng(seed)
    rows = []
    for ki, k in enumerate(["K1", "K2", "K3"]):
        for ci, c in enumerate(["on_demand", "provisioned"]):
            base = 10 + effect_key * ki + effect_cap * ci + interaction * (ki == 2) * ci
            e = rng.lognormal(0, 0.6, n) if skew else rng.normal(0, noise, n)
            for v in base + e:
                rows.append({"key_design": k, "capacity_mode": c, "configuration": f"{k}-{c}", "y": v})
    return pd.DataFrame(rows)


def test_key_effect_found_capacity_not():
    r = stats.factorial(cells(effect_key=2.0, seed=1), "y")
    assert r["method"] == "anova2"
    assert r["terms"]["key"]["p"] < 1e-6 and r["terms"]["capacity"]["p"] > 0.01
    assert 0 < r["terms"]["key"]["partial_eta2"] < 1


def test_interaction_triggers_tukey_simple_effects():
    r = stats.factorial(cells(interaction=4.0, seed=2), "y")
    assert r["terms"]["interaction"]["p"] < 0.001
    se = r["simple_effects"]
    assert {x["capacity_mode"] for x in se} == {"on_demand", "provisioned"}
    assert any(x["reject"] for x in se if x["capacity_mode"] == "provisioned")


def test_skewed_data_goes_to_art():
    r = stats.factorial(cells(effect_cap=1.5, seed=3, skew=True), "y")
    assert r["method"] == "art"
    assert r["terms"]["capacity"]["p"] < 0.001 and "epsilon2" in r["terms"]["capacity"]


def test_art_alignment_keeps_only_its_effect():
    d = stats._aligned(cells(effect_key=5.0, seed=4), "y")
    # the capacity-aligned response has no key effect left in it
    assert d.groupby("key_design")["capacity"].mean().std() < 0.5


def test_no_variance_is_reported_not_crashed():
    df = cells(seed=5).assign(y=0.0)
    r = stats.factorial(df, "y")
    assert r["method"] == "no_variance" and r["terms"]["key"]["p"] == 1.0


def test_holm():
    adj = stats.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adj == pytest.approx({"a": 0.03, "b": 0.06, "c": 0.06})


def test_joint_divergence():
    df = cells(seed=6)
    df["lat"] = np.where(df["configuration"] == "K3-provisioned", 5.0, 10.0) + np.random.default_rng(1).normal(0, 0.2, len(df))
    df["cost"] = np.where(df["configuration"] == "K1-on_demand", 1.0, 2.0) + np.random.default_rng(2).normal(0, 0.05, len(df))
    r = stats.joint_divergence(df, "lat", "cost", n_boot=300)
    assert r["latency_optimal"] == "K3-provisioned" and r["cost_optimal"] == "K1-on_demand"
    assert r["p"] < 0.01 and not r["coincide_observed"]
    df["cost"] = np.where(df["configuration"] == "K3-provisioned", 1.0, 2.0)
    assert stats.joint_divergence(df, "lat", "cost", n_boot=300)["p"] > 0.95


def test_price_file_is_dated_and_regional():
    assert PRICES["region"] == "eu-west-1" and PRICES["publication_date"].startswith("2026")
    assert PRICES["on_demand"]["write_request_unit"] > PRICES["on_demand"]["read_request_unit"]


def test_cost_formulas_by_hand():
    # 1M WRU on demand = $0.705
    assert on_demand_cost(0, 1_000_000, PRICES) == pytest.approx(0.705)
    # 100 WCU for one hour = 100 x $0.000735
    assert provisioned_cost(0, 100, 3600, PRICES) == pytest.approx(0.0735)
    # consuming 100 WCU every second for an hour, priced as capacity-hours = the same
    assert consumed_equivalent_cost(0, 100 * 3600, PRICES) == pytest.approx(0.0735)
    assert per_10k(0.5, 20_000) == pytest.approx(0.25)
    assert np.isnan(per_10k(1.0, 0))


def test_add_costs_uses_the_right_formula_per_mode():
    b = pd.DataFrame([
        {"capacity_mode": "on_demand", "rcu": 9000.0, "wcu": 9000.0, "succeeded": 18000, "wall_s": 90,
         "prov_rcu_avg": np.nan, "prov_wcu_avg": np.nan},
        {"capacity_mode": "provisioned", "rcu": 9000.0, "wcu": 9000.0, "succeeded": 18000, "wall_s": 90,
         "prov_rcu_avg": 140.0, "prov_wcu_avg": 200.0},
    ])
    out = add_costs(b, PRICES)
    assert out.loc[0, "cost_usd"] == pytest.approx(9000 * 0.0000001415 + 9000 * 0.000000705)
    assert out.loc[1, "cost_usd"] == pytest.approx((140 * 0.000147 + 200 * 0.000735) * 90 / 3600)
    assert out.loc[1, "cost_consumed_eq_usd"] < out.loc[1, "cost_usd"]  # idle headroom costs money
    assert (out["cost_per_10k"] > 0).all()
