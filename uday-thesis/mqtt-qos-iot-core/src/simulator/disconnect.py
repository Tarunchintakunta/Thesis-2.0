"""Controlled publisher disconnect windows."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DisconnectWindow:
    start_s: float
    end_s: float

    @classmethod
    def from_schedule(cls, times: list[float], disconnect_s: int) -> "DisconnectWindow":
        """Impose the cut at message index n/3 so bursty idle gaps are not accidentally missed."""
        if disconnect_s <= 0 or not times:
            return cls(start_s=0.0, end_s=0.0)
        idx = max(0, min(len(times) - 1, len(times) // 3))
        start = float(times[idx])
        return cls(start_s=start, end_s=start + float(disconnect_s))

    @classmethod
    def from_campaign(cls, n_messages: int, interval_s: float, disconnect_s: int) -> "DisconnectWindow":
        if disconnect_s <= 0:
            return cls(start_s=0.0, end_s=0.0)
        start = (float(n_messages) / 3.0) * float(interval_s)
        return cls(start_s=start, end_s=start + float(disconnect_s))

    def active(self) -> bool:
        return self.end_s > self.start_s

    def disconnected_at(self, t_s: float) -> bool:
        if not self.active():
            return False
        return self.start_s <= t_s < self.end_s

    def in_inflight_cut(self, t_s: float, window_s: float = 0.0) -> bool:
        if not self.active():
            return False
        return (self.start_s - float(window_s)) <= t_s < self.start_s
