"""Redis-like idempotency store (in-memory for local/moto; Redis client stub for AWS)."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Protocol


def idempotency_key(source: str, event_id: str, payload: bytes | str = b"") -> str:
    """SHA-256 key from source + event_id (+ optional payload bytes)."""
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    h = hashlib.sha256()
    h.update(source.encode("utf-8"))
    h.update(b"|")
    h.update(event_id.encode("utf-8"))
    if payload:
        h.update(b"|")
        h.update(payload)
    return h.hexdigest()


@dataclass
class ClaimResult:
    is_new: bool
    key: str
    prior_status: str | None = None


class IdempotencyStore(Protocol):
    def claim(self, key: str, *, ttl_s: int = 86400) -> ClaimResult: ...
    def complete(self, key: str) -> None: ...
    def get(self, key: str) -> str | None: ...
    def size(self) -> int: ...


@dataclass
class InMemoryIdempotencyStore:
    """TTL-aware dict standing in for ElastiCache Redis SET NX EX."""

    _data: dict[str, tuple[str, float]] = field(default_factory=dict)
    now_fn: callable = time.time  # type: ignore[assignment]

    def _purge(self, key: str) -> None:
        item = self._data.get(key)
        if item and item[1] <= self.now_fn():
            del self._data[key]

    def claim(self, key: str, *, ttl_s: int = 86400) -> ClaimResult:
        self._purge(key)
        if key in self._data:
            return ClaimResult(False, key, self._data[key][0])
        self._data[key] = ("PROCESSING", self.now_fn() + ttl_s)
        return ClaimResult(True, key, None)

    def complete(self, key: str) -> None:
        if key in self._data:
            _, exp = self._data[key]
            self._data[key] = ("COMPLETE", exp)

    def get(self, key: str) -> str | None:
        self._purge(key)
        item = self._data.get(key)
        return item[0] if item else None

    def size(self) -> int:
        now = self.now_fn()
        return sum(1 for _, exp in self._data.values() if exp > now)
