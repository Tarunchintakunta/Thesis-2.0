"""SQS-style exponential backoff with full jitter (AWS recommended)."""
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class BackoffConfig:
    base_ms: float = 100.0
    max_ms: float = 30_000.0
    multiplier: float = 2.0
    jitter: str = "full"  # full | none


def delay_ms(attempt: int, cfg: BackoffConfig, rng: random.Random | None = None) -> float:
    """Return sleep milliseconds for 0-based attempt index after a failure."""
    if attempt < 0:
        attempt = 0
    raw = min(cfg.max_ms, cfg.base_ms * (cfg.multiplier ** attempt))
    if cfg.jitter == "none":
        return raw
    r = rng or random
    # Full jitter: U(0, cap) — AWS architecture blog pattern
    return r.uniform(0.0, raw)


def should_retry(receive_count: int, max_receive_count: int) -> bool:
    """True while receive_count is still below maxReceiveCount (SQS redrive)."""
    return receive_count < max_receive_count
