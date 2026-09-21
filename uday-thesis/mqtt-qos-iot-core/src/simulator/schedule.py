"""Publish-time schedules: steady 5 s vs bursty with the same mean rate."""

from __future__ import annotations


def publish_times(n_messages: int, interval_s: float, rate_mode: str) -> list[float]:
    if n_messages < 0:
        raise ValueError("n_messages")
    if rate_mode == "steady":
        return [float(i) * interval_s for i in range(n_messages)]
    if rate_mode != "bursty":
        raise ValueError(f"unknown rate_mode: {rate_mode}")

    # Bursty ON/OFF with mean inter-message time == interval_s.
    # Clusters of up to 5 messages at 50 ms spacing, then idle to the mean schedule.
    intra = 0.05
    times: list[float] = []
    t = 0.0
    i = 0
    while i < n_messages:
        burst = min(5, n_messages - i)
        for _ in range(burst):
            times.append(t)
            t += intra
            i += 1
        target = float(i) * interval_s
        if t < target:
            t = target
    return times
