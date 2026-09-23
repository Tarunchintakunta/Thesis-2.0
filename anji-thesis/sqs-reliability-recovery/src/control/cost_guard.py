"""Cost estimate for a planned set of live runs, and the budget check.

Estimates from order counts and pricing only (no local simulator).
"""
from __future__ import annotations

import os
from typing import Any

SAFETY_FACTOR = 2.0
LIVE_OVERHEAD_S = 90.0
# Rough per-order request proxy when no simulator is available.
REQ_PER_ORDER = 4.0
SEC_PER_ORDER = 0.05


class CostGuardError(RuntimeError):
    pass


def estimate_plan(specs: list, pricing: dict[str, float]) -> dict[str, Any]:
    sqs = float(pricing.get("sqs_per_request", pricing.get("sqs_request_usd", 0.0)) or 0.0)
    lam = float(pricing.get("lambda_per_request", pricing.get("lambda_request_usd", 0.0)) or 0.0)
    unit = max(sqs + lam, 1e-9)
    total = 0.0
    worst = 0.0
    wall_s = 0.0
    for spec in specs:
        orders = float(getattr(spec, "order_count", 0) or 0)
        usd = orders * REQ_PER_ORDER * unit * SAFETY_FACTOR
        total += usd
        worst = max(worst, usd)
        wall_s += orders * SEC_PER_ORDER + LIVE_OVERHEAD_S
    return {
        "runs": len(specs),
        "usd_total": total,
        "usd_worst_run": worst,
        "safety_factor": SAFETY_FACTOR,
        "est_wall_hours": wall_s / 3600.0,
    }


def guard_settings() -> tuple[bool, float]:
    enabled = os.environ.get("ENABLE_COST_GUARD", "1") != "0"
    limit = float(os.environ.get("MAX_ESTIMATED_USD", "5.00"))
    return enabled, limit


def check_plan(specs: list, pricing: dict[str, float], max_usd: float | None = None) -> dict[str, Any]:
    enabled, limit = guard_settings()
    if max_usd is not None:
        limit = max_usd
    estimate = estimate_plan(specs, pricing)
    estimate["limit_usd"] = limit
    if not enabled:
        print("[warn] ENABLE_COST_GUARD=0, not enforcing the budget")
        return estimate
    if estimate["usd_total"] > limit:
        raise CostGuardError(
            f"estimated ${estimate['usd_total']:.2f} for {estimate['runs']} runs is above "
            f"MAX_ESTIMATED_USD=${limit:.2f}. Cut orders/repeats or raise the limit on purpose."
        )
    return estimate
