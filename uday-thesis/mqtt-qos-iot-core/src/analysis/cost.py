"""Cost surface from published unit prices × counted operations (not a bill)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_pricing(path: Path | None = None) -> dict[str, Any]:
    p = path or (ROOT / "configs" / "pricing.yaml")
    return yaml.safe_load(p.read_text())


def estimate_usd(
    counters: dict[str, float],
    duration_s: float,
    n_devices: int,
    pricing: dict[str, Any] | None = None,
) -> dict[str, float]:
    pricing = pricing or load_pricing()
    iot = pricing["iot_core"]
    lam = pricing["lambda"]
    ddb = pricing["dynamodb"]
    safety = float(pricing.get("safety_factor", 1.0))

    messages = float(counters.get("publishes_attempted_connected", 0)) + float(
        counters.get("pubacks", 0)
    )
    # Prefer explicit reached/rule counts when present.
    messages = float(counters.get("reached_broker", messages))
    minutes = (float(duration_s) / 60.0) * float(n_devices)
    rules = float(counters.get("rule_invocations", 0))
    actions = rules  # one DynamoDB action per successful rule
    lambda_req = rules
    gb_seconds = (
        lambda_req
        * (float(lam.get("assumed_memory_mb", 128)) / 1024.0)
        * (float(lam.get("assumed_duration_ms", 20)) / 1000.0)
    )
    wru = float(counters.get("ddb_puts", 0))

    usd_raw = (
        (messages / 1_000_000.0) * float(iot["usd_per_million_messages"])
        + (minutes / 1_000_000.0) * float(iot["usd_per_million_minutes"])
        + (rules / 1_000_000.0) * float(iot["usd_per_million_rules_triggered"])
        + (actions / 1_000_000.0) * float(iot["usd_per_million_rule_actions"])
        + (lambda_req / 1_000_000.0) * float(lam["usd_per_million_requests"])
        + gb_seconds * float(lam["usd_per_gb_second"])
        + (wru / 1_000_000.0) * float(ddb["usd_per_million_wru"])
    )
    return {
        "usd_raw": float(usd_raw),
        "usd_with_safety": float(usd_raw) * safety,
        "messages_counted": messages,
        "rules_counted": rules,
        "wru_counted": wru,
        "minutes_counted": minutes,
    }


def campaign_operations(
    n_devices: int,
    n_messages: int,
    n_cells: int,
    qos_share_1: float = 0.5,
) -> dict[str, float]:
    """Upper-bound ops if every intended publish hits the broker (live planning)."""
    publishes = float(n_devices * n_messages * n_cells)
    pubacks = publishes * float(qos_share_1)
    return {
        "publishes": publishes,
        "pubacks": pubacks,
        "iot_messages_upper": publishes + pubacks,
        "rules_upper": publishes,
        "lambda_upper": publishes,
        "ddb_puts_upper": publishes,
    }
