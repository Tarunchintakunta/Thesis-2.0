"""Lambda cost per 1,000 invocations (aligned with how Bluemke and Zdanowski report cost).

    compute cost = billed seconds x (memory MB / 1024) x price per GB-s (architecture)
    request cost = price per request

Prices live in configs/pricing.yaml together with the date they were copied
from the AWS pricing page; update both before a live campaign.

Init phase: ``bill_init_phase`` controls whether Init Duration is added to the
billed time when a REPORT line's Billed Duration does not already contain it
(the mock data and the local benchmark). For live REPORT lines the Billed
Duration printed by AWS is used as-is.
"""
from __future__ import annotations

import math
from pathlib import Path

import yaml

DEFAULT_PRICES = {
    "as_of": "unknown",
    "region": "eu-west-1",
    "per_gb_second": {"arm64": 0.0000133334, "x86_64": 0.0000166667},
    "per_request": 0.20 / 1_000_000,
    "bill_init_phase": True,
}


def load_prices(path: str | Path | None = None) -> dict:
    if path and Path(path).exists():
        with open(path, encoding="utf-8") as fh:
            return {**DEFAULT_PRICES, **(yaml.safe_load(fh) or {})}
    return dict(DEFAULT_PRICES)


def billed_ms(duration_ms: float, init_ms: float | None = None, bill_init: bool = True) -> int:
    """Lambda bills in 1 ms steps."""
    total = duration_ms + ((init_ms or 0.0) if bill_init else 0.0)
    return int(math.ceil(total))


def invocation_cost(billed: float, memory_mb: int, arch: str, prices: dict) -> float:
    gb_s = billed / 1000.0 * memory_mb / 1024.0
    return gb_s * prices["per_gb_second"][arch] + prices["per_request"]


def cost_per_1k(billed_values, memory_mb: int, arch: str, prices: dict) -> float:
    billed_values = list(billed_values)
    if not billed_values:
        return math.nan
    mean = sum(invocation_cost(b, memory_mb, arch, prices) for b in billed_values) / len(billed_values)
    return mean * 1000.0


def warming_cost_per_1k(pings_per_hour: float, ping_billed_ms: float, memory_mb: int, arch: str,
                        prices: dict, invocations_per_hour: float) -> float:
    """Extra cost of keep-warm pings, spread over 1,000 real invocations."""
    if invocations_per_hour <= 0:
        return math.inf
    ping_cost = invocation_cost(ping_billed_ms, memory_mb, arch, prices)
    return pings_per_hour * ping_cost / invocations_per_hour * 1000.0
