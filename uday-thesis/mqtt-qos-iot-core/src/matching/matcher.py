"""Match device-side ID log against delivered DynamoDB (or mock) rows."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np


@dataclass
class MatchResult:
    n_published: int
    n_lost: int
    n_delivered_unique: int
    n_duplicate_ids: int
    n_delivery_copies: int
    n_extra_ids: int
    loss_rate: float
    duplicate_id_rate: float
    extra_copy_rate: float
    latency_mean_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    latencies_ms: list[float] = field(default_factory=list)
    lost_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("latencies_ms", None)
        d["n_latency_samples"] = len(self.latencies_ms)
        d.pop("lost_ids", None)
        return d


def _pct(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    return float(np.percentile(values, q))


def match_logs(device_log: list[dict[str, Any]], delivered: list[dict[str, Any]]) -> MatchResult:
    by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in delivered:
        by_id[str(row["msg_id"])].append(row)

    lost_ids: list[str] = []
    latencies: list[float] = []
    n_dup = 0
    n_copies = 0
    n_unique = 0

    published_ids = [str(r["msg_id"]) for r in device_log]
    log_ts = {str(r["msg_id"]): float(r.get("ts_log_ms", 0.0)) for r in device_log}

    for msg_id in published_ids:
        copies = by_id.get(msg_id, [])
        n_copies += len(copies)
        if not copies:
            lost_ids.append(msg_id)
            continue
        n_unique += 1
        if len(copies) > 1:
            n_dup += 1
        first = min(copies, key=lambda r: int(r.get("ts_ingest_ms", 0)))
        latencies.append(float(first.get("ts_ingest_ms", 0)) - float(log_ts.get(msg_id, 0.0)))

    delivered_ids = set(by_id)
    extra = len(delivered_ids - set(published_ids))
    n_pub = len(published_ids)
    n_lost = len(lost_ids)
    loss_rate = (n_lost / n_pub) if n_pub else float("nan")
    dup_rate = (n_dup / n_pub) if n_pub else float("nan")
    extra_copy_rate = ((n_copies - n_unique) / n_pub) if n_pub else float("nan")

    return MatchResult(
        n_published=n_pub,
        n_lost=n_lost,
        n_delivered_unique=n_unique,
        n_duplicate_ids=n_dup,
        n_delivery_copies=n_copies,
        n_extra_ids=extra,
        loss_rate=float(loss_rate),
        duplicate_id_rate=float(dup_rate),
        extra_copy_rate=float(extra_copy_rate),
        latency_mean_ms=float(np.mean(latencies)) if latencies else float("nan"),
        latency_p95_ms=_pct(latencies, 95),
        latency_p99_ms=_pct(latencies, 99),
        latencies_ms=latencies,
        lost_ids=lost_ids,
    )
