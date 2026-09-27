"""Metric aggregation: delivery success, duplicate suppression, latency, DLQ recovery."""
from __future__ import annotations

import math
from dataclasses import dataclass, field


def percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    if p <= 0:
        return sorted_vals[0]
    if p >= 100:
        return sorted_vals[-1]
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)


@dataclass
class RunMetrics:
    attempted: int = 0
    unique_events: int = 0
    delivered_unique: int = 0
    duplicate_attempts: int = 0
    duplicates_suppressed: int = 0
    auth_rejected: int = 0
    transient_failures: int = 0
    permanent_failures: int = 0
    dlq_captured: int = 0
    dlq_replayed: int = 0
    dlq_recovered: int = 0
    latencies_ms: list[float] = field(default_factory=list)
    config: str = ""
    fault_rate: float = 0.0
    mode: str = "local_sim"

    def delivery_success_rate(self) -> float:
        if self.unique_events == 0:
            return 0.0
        return self.delivered_unique / self.unique_events

    def duplicate_suppression_ratio(self) -> float:
        if self.duplicate_attempts == 0:
            return 1.0  # vacuously perfect when no duplicates injected
        return self.duplicates_suppressed / self.duplicate_attempts

    def dlq_recovery_rate(self) -> float:
        if self.dlq_captured == 0:
            return 1.0
        return self.dlq_recovered / self.dlq_captured

    def latency_percentiles(self) -> dict[str, float]:
        vals = sorted(self.latencies_ms)
        return {
            "p50_ms": round(percentile(vals, 50), 3),
            "p95_ms": round(percentile(vals, 95), 3),
            "p99_ms": round(percentile(vals, 99), 3),
            "n": len(vals),
        }

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "config": self.config,
            "fault_rate": self.fault_rate,
            "attempted": self.attempted,
            "unique_events": self.unique_events,
            "delivered_unique": self.delivered_unique,
            "delivery_success_rate": round(self.delivery_success_rate(), 6),
            "duplicate_attempts": self.duplicate_attempts,
            "duplicates_suppressed": self.duplicates_suppressed,
            "duplicate_suppression_ratio": round(self.duplicate_suppression_ratio(), 6),
            "auth_rejected": self.auth_rejected,
            "transient_failures": self.transient_failures,
            "permanent_failures": self.permanent_failures,
            "dlq_captured": self.dlq_captured,
            "dlq_replayed": self.dlq_replayed,
            "dlq_recovered": self.dlq_recovered,
            "dlq_recovery_rate": round(self.dlq_recovery_rate(), 6),
            "latency": self.latency_percentiles(),
            "note": "LOCAL_SIM — not live AWS measurements",
        }
