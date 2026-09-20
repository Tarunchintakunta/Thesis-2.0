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
        d.pop("lost_ids", None)
        d["n_latency_samples"] = len(self.latencies_ms)
        return d


def _pct(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    return float(np.percentile(values, q))


def match_logs(device_log: list[dict[str, Any]], delivered: list[dict[str, Any]]) -> MatchResult:
    intended = {row["msg_id"]: row for row in device_log}
    copies: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in delivered:
        copies[str(row["msg_id"])].append(row)

    lost_ids = [mid for mid in intended if mid not in copies]
    extra_ids = [mid for mid in copies if mid not in intended]
    dup_ids = [mid for mid, rows in copies.items() if mid in intended and len(rows) > 1]

    latencies: list[float] = []
    for mid, rows in copies.items():
        src = intended.get(mid)
        if src is None:
            continue
        first = min(rows, key=lambda r: int(r["ts_ingest_ms"]))
        latencies.append(float(int(first["ts_ingest_ms"]) - int(src["ts_log_ms"])))

    n = len(intended)
    n_copies = sum(len(v) for v in copies.values())
    unique = n - len(lost_ids)
    extra_copies = max(0, n_copies - unique)
    return MatchResult(
        n_published=n,
        n_lost=len(lost_ids),
        n_delivered_unique=unique,
        n_duplicate_ids=len(dup_ids),
        n_delivery_copies=n_copies,
        n_extra_ids=len(extra_ids),
        loss_rate=(len(lost_ids) / n) if n else 0.0,
        duplicate_id_rate=(len(dup_ids) / n) if n else 0.0,
        extra_copy_rate=(extra_copies / n) if n else 0.0,
        latency_mean_ms=float(np.mean(latencies)) if latencies else float("nan"),
        latency_p95_ms=_pct(latencies, 95),
        latency_p99_ms=_pct(latencies, 99),
        latencies_ms=latencies,
        lost_ids=lost_ids,
    )
