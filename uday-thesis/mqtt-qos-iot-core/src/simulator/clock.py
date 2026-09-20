"""Simulated time. Dry-run must not sleep wall-clock 5 s intervals."""
from __future__ import annotations


class VirtualClock:
    def __init__(self, start_s: float = 0.0) -> None:
        self._t = float(start_s)

    @property
    def s(self) -> float:
        return self._t

    @property
    def ms(self) -> int:
        return int(self._t * 1000)

    def set(self, t_s: float) -> None:
        self._t = float(t_s)

    def advance(self, dt_s: float) -> None:
        if dt_s < 0:
            raise ValueError("cannot rewind")
        self._t += dt_s
