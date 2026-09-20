"""Publish-time schedules: steady 5 s vs bursty with the same mean rate."""
from __future__ import annotations


def publish_times(n_messages: int, interval_s: float, rate_mode: str) -> list[float]:
    if n_messages < 0:
        raise ValueError("n_messages")
    if rate_mode == "steady":
        return [i * interval_s for i in range(n_messages)]
    if rate_mode != "bursty":
        raise ValueError(rate_mode)
    burst = 10
    intra = interval_s * 0.05
    times: list[float] = []
    t = 0.0
    i = 0
    while i < n_messages:
        chunk = min(burst, n_messages - i)
        for _ in range(chunk):
            times.append(t)
            t += intra
            i += 1
        target = i * interval_s
        if t < target:
            t = target
    return times
