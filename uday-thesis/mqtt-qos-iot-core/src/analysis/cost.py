"""Cost surface from published unit prices × counted operations (not a bill)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_pricing(path: Path | None = None) -> dict[str, Any]:
    path = path or (ROOT / "configs" / "pricing.yaml")
    return yaml.safe_load(path.read_text())


def estimate_usd(counters: dict[str, float], duration_s: float, n_devices: int, pricing: dict[str, Any] | None = None) -> dict[str, float]:
    pricing = pricing or load_pricing()
    iot = pricing["iot_core"]
    lam = pricing["lambda"]
    ddb = pricing["dynamodb"]
    safety = float(pricing.get("safety_factor", 1.0))

    messages = float(counters.get("publishes_attempted_connected", 0) + counters.get("pubacks", 0))
    minutes = n_devices * (duration_s / 60.0)
    rules = float(counters.get("rule_invocations", 0))
    actions = rules
    lambda_req = rules
    gb_seconds = lambda_req * (lam["assumed_memory_mb"] / 1024.0) * (lam["assumed_duration_ms"] / 1000.0)
    wru = float(counters.get("ddb_puts", 0))

    usd = {
        "iot_messages": messages / 1e6 * iot["usd_per_million_messages"],
        "iot_minutes": minutes / 1e6 * iot["usd_per_million_minutes"],
        "iot_rules": rules / 1e6 * iot["usd_per_million_rules_triggered"],
        "iot_actions": actions / 1e6 * iot["usd_per_million_rule_actions"],
        "lambda_requests": lambda_req / 1e6 * lam["usd_per_million_requests"],
        "lambda_compute": gb_seconds * lam["usd_per_gb_second"],
        "dynamodb_wru": wru / 1e6 * ddb["usd_per_million_wru"],
    }
    raw = sum(usd.values())
    usd["usd_raw"] = raw
    usd["usd_with_safety"] = raw * safety
    usd["messages_counted"] = messages
    usd["rules_counted"] = rules
    usd["wru_counted"] = wru
    usd["minutes_counted"] = minutes
    usd["safety_factor"] = safety
    return usd


def campaign_operations(n_devices: int, n_messages: int, n_cells: int, qos_share_1: float = 0.5) -> dict[str, float]:
    """Upper-bound ops if every intended publish hits the broker (live planning)."""
    publishes = n_devices * n_messages * n_cells
    pubacks = publishes * qos_share_1
    return {
        "publishes": publishes,
        "pubacks": pubacks,
        "iot_messages_upper": publishes + pubacks,
        "rules_upper": publishes,
        "lambda_upper": publishes,
        "ddb_puts_upper": publishes,
    }
