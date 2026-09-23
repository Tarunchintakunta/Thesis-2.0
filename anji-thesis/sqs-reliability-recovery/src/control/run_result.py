"""Shared run-result shape for the live experiment backend."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RunResult:
    produced: dict[str, float]
    events: list[dict[str, Any]]
    dlq_order_ids: list[str]
    remaining_ids: list[str]
    samples: list[dict[str, float]]
    fault_window: tuple[float, float] | None
    counters: dict[str, float]
    end_time: float
    max_apply_count: int
