"""Multi-dimensional quotas with atomic in-memory counters (Redis stand-in)."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Literal

Dimension = Literal["api", "storage", "compute"]


@dataclass
class QuotaLimit:
    hard: int
    soft: int


@dataclass
class QuotaDecision:
    allowed: bool
    dimension: Dimension
    used: int
    soft_exceeded: bool
    hard_exceeded: bool
    latency_ms: float


@dataclass
class InMemoryQuotaEngine:
    """Atomic multi-dim counters. Mirrors Redis INCR / WATCH+MULTI semantics locally."""

    limits: dict[str, dict[Dimension, QuotaLimit]] = field(default_factory=dict)
    _usage: dict[tuple[str, Dimension], int] = field(default_factory=dict)

    def set_limits(self, tenant_id: str, *, api: QuotaLimit, storage: QuotaLimit, compute: QuotaLimit) -> None:
        self.limits[tenant_id] = {"api": api, "storage": storage, "compute": compute}

    def check_and_consume(self, tenant_id: str, dimension: Dimension, amount: int = 1) -> QuotaDecision:
        t0 = time.perf_counter()
        lims = self.limits.get(tenant_id)
        if lims is None:
            # default small limits
            lims = {
                "api": QuotaLimit(hard=1000, soft=800),
                "storage": QuotaLimit(hard=10_000, soft=8_000),
                "compute": QuotaLimit(hard=500, soft=400),
            }
            self.limits[tenant_id] = lims
        key = (tenant_id, dimension)
        used = self._usage.get(key, 0) + amount
        hard = lims[dimension].hard
        soft = lims[dimension].soft
        hard_ex = used > hard
        soft_ex = used > soft
        if not hard_ex:
            self._usage[key] = used
        else:
            used = self._usage.get(key, 0)
        lat = (time.perf_counter() - t0) * 1000
        return QuotaDecision(
            allowed=not hard_ex,
            dimension=dimension,
            used=used,
            soft_exceeded=soft_ex and not hard_ex,
            hard_exceeded=hard_ex,
            latency_ms=lat,
        )

    def usage(self, tenant_id: str, dimension: Dimension) -> int:
        return self._usage.get((tenant_id, dimension), 0)

    def snapshot(self) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = {}
        for (tid, dim), val in self._usage.items():
            out.setdefault(tid, {})[dim] = val
        return out
