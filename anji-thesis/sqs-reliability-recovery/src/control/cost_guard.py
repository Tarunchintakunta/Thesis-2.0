"""Cost estimate for a planned set of live runs.

Estimates from order counts and pricing only (planning aid; does not block runs).
"""
from __future__ import annotations

from typing import Any


SAFETY_FACTOR = 2.0
LIVE_OVERHEAD_S = 90.0
# Rough per-order request proxy when no simulator is available.
REQ_PER_ORDER = 4.0
SEC_PER_ORDER = 0.05


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
