"""Controlled fault injection for webhook processing experiments."""
from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum


class FaultKind(str, Enum):
    NONE = "none"
    TRANSIENT = "transient"       # network / downstream timeout — retryable
    PERMANENT = "permanent"       # poison / schema — should land in DLQ
    DUPLICATE = "duplicate"       # synthetic redelivery of same event_id


@dataclass
class FaultPlan:
    """Probabilities in [0, 1]. Permanent is applied only if transient did not fire."""

    transient_rate: float = 0.0
    permanent_rate: float = 0.0
    duplicate_rate: float = 0.0


def decide(plan: FaultPlan, rng: random.Random) -> FaultKind:
    if rng.random() < plan.transient_rate:
        return FaultKind.TRANSIENT
    if rng.random() < plan.permanent_rate:
        return FaultKind.PERMANENT
    return FaultKind.NONE


def should_inject_duplicate(plan: FaultPlan, rng: random.Random) -> bool:
    return rng.random() < plan.duplicate_rate
