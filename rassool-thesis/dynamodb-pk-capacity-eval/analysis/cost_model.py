"""Cost per 10,000 successful operations from published unit prices (config/prices.yaml).

on-demand      consumed RRU x price per RRU + consumed WRU x price per WRU
provisioned    (mean provisioned RCU x RCU-hour price + mean provisioned WCU x WCU-hour price)
               x batch hours - what the table costs while the batch runs, used or not (primary)
provisioned,   consumed units priced at the hourly rate as if capacity were sized perfectly
consumed-eq.   (sensitivity only - shows how much of C2's cost is idle headroom)

Storage, backups and data transfer are left out on purpose (master prompt 2.3).
Every figure can be recomputed by hand from prices.yaml and results/batches.csv:

    cost_per_10k = batch_cost / succeeded * 10,000
"""
from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_prices(path: str | Path = ROOT / "config/prices.yaml") -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def on_demand_cost(rcu: float, wcu: float, prices: dict) -> float:
    od = prices["on_demand"]
    return rcu * od["read_request_unit"] + wcu * od["write_request_unit"]


def provisioned_cost(prov_rcu: float, prov_wcu: float, seconds: float, prices: dict) -> float:
    p = prices["provisioned"]
    return (prov_rcu * p["rcu_hour"] + prov_wcu * p["wcu_hour"]) * seconds / 3600.0


def consumed_equivalent_cost(rcu: float, wcu: float, prices: dict) -> float:
    """Consumed capacity-seconds priced per hour: a perfectly sized provisioned table."""
    p = prices["provisioned"]
    return (rcu * p["rcu_hour"] + wcu * p["wcu_hour"]) / 3600.0


def per_10k(cost: float, succeeded: float) -> float:
    return cost / succeeded * 10_000 if succeeded and succeeded > 0 else math.nan


def add_costs(batches: pd.DataFrame, prices: dict) -> pd.DataFrame:
    """Needs: capacity_mode, rcu, wcu, succeeded, wall_s, prov_rcu_avg, prov_wcu_avg."""
    b = batches.copy()
    od = b["capacity_mode"] == "on_demand"
    b["cost_usd"] = [
        on_demand_cost(r, w, prices) if is_od else provisioned_cost(pr, pw, s, prices)
        for is_od, r, w, pr, pw, s in zip(od, b["rcu"], b["wcu"], b["prov_rcu_avg"], b["prov_wcu_avg"],
                                          b["wall_s"], strict=True)
    ]
    b["cost_consumed_eq_usd"] = [
        on_demand_cost(r, w, prices) if is_od else consumed_equivalent_cost(r, w, prices)
        for is_od, r, w in zip(od, b["rcu"], b["wcu"], strict=True)
    ]
    b["cost_per_10k"] = [per_10k(c, s) for c, s in zip(b["cost_usd"], b["succeeded"], strict=True)]
    b["cost_per_10k_consumed_eq"] = [per_10k(c, s) for c, s in zip(b["cost_consumed_eq_usd"], b["succeeded"], strict=True)]
    return b
