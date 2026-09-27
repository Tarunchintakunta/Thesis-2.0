"""Jain's fairness index and latency aggregates."""
from __future__ import annotations

import math
from dataclasses import dataclass, field


def jain_index(shares: list[float]) -> float:
    """Jain's fairness index in [0, 1]. Equal shares → 1.0."""
    if not shares:
        return 1.0
    s = sum(shares)
    if s <= 0:
        return 1.0
    ss = sum(x * x for x in shares)
    n = len(shares)
    return (s * s) / (n * ss) if ss > 0 else 1.0


def percentile(vals: list[float], p: float) -> float:
    if not vals:
        return 0.0
    xs = sorted(vals)
    if p <= 0:
        return xs[0]
    if p >= 100:
        return xs[-1]
    k = (len(xs) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return xs[int(k)]
    return xs[f] * (c - k) + xs[c] * (k - f)


@dataclass
class EvalMetrics:
    mode: str = "local_sim"
    tenants: int = 0
    requests: int = 0
    cross_tenant_attempts: int = 0
    cross_tenant_blocked: int = 0
    cross_tenant_leaked: int = 0
    auth_latencies_ms: list[float] = field(default_factory=list)
    quota_latencies_ms: list[float] = field(default_factory=list)
    tenant_api_usage: dict[str, int] = field(default_factory=dict)
    hard_rejects: int = 0
    note: str = "LOCAL_SIM — not live AWS"

    def unauthorized_access_count(self) -> int:
        return self.cross_tenant_leaked

    def jain(self) -> float:
        return jain_index([float(v) for v in self.tenant_api_usage.values()])

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "note": self.note,
            "tenants": self.tenants,
            "requests": self.requests,
            "cross_tenant_attempts": self.cross_tenant_attempts,
            "cross_tenant_blocked": self.cross_tenant_blocked,
            "cross_tenant_leaked": self.cross_tenant_leaked,
            "zero_unauthorized_access": self.cross_tenant_leaked == 0,
            "jain_fairness_index": round(self.jain(), 6),
            "auth_latency_ms": {
                "p50": round(percentile(self.auth_latencies_ms, 50), 4),
                "p95": round(percentile(self.auth_latencies_ms, 95), 4),
                "p99": round(percentile(self.auth_latencies_ms, 99), 4),
                "n": len(self.auth_latencies_ms),
            },
            "quota_latency_ms": {
                "p50": round(percentile(self.quota_latencies_ms, 50), 4),
                "p95": round(percentile(self.quota_latencies_ms, 95), 4),
                "p99": round(percentile(self.quota_latencies_ms, 99), 4),
                "n": len(self.quota_latencies_ms),
            },
            "auth_budget_50ms_ok": percentile(self.auth_latencies_ms, 95) < 50.0 if self.auth_latencies_ms else True,
            "quota_budget_5ms_ok": percentile(self.quota_latencies_ms, 95) < 5.0 if self.quota_latencies_ms else True,
            "hard_rejects": self.hard_rejects,
            "tenant_api_usage": self.tenant_api_usage,
        }
