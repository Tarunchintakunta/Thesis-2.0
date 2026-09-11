"""Synthetic traffic: a diurnal Poisson process with scale-up bursts.

Bursts are what make the *benign elasticity* the study cares about: sudden
load forces Lambda to start new execution environments (cold starts), which
look a lot like an anomaly in the logs (Nguyen et al., 2025).
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

DAY_S = 86400.0


@dataclass(frozen=True)
class Burst:
    start: float
    length: float
    factor: float

    def covers(self, t: float) -> bool:
        return self.start <= t < self.start + self.length


def diurnal_rate(t: float, base: float, amplitude: float) -> float:
    """Requests per second at epoch time t. Lowest around 04:00, highest around 16:00."""
    hour = (t % DAY_S) / 3600.0
    return max(0.0, base * (1.0 + amplitude * math.sin(2 * math.pi * (hour - 10.0) / 24.0)))


def regular_bursts(t0: float, t1: float, every_s: float, length_s: float, factor: float,
                   rng: random.Random) -> list[Burst]:
    """One burst per ``every_s`` seconds, at a random offset inside each slot."""
    if every_s <= 0 or factor <= 1:
        return []
    bursts = []
    slot = t0
    while slot < t1:
        start = slot + rng.uniform(0, max(0.0, every_s - length_s))
        if start + length_s <= t1:
            bursts.append(Burst(start, length_s, factor))
        slot += every_s
    return bursts


def arrivals(t0: float, t1: float, base: float, amplitude: float, bursts: list[Burst],
             rng: random.Random) -> list[float]:
    """Non-homogeneous Poisson arrivals by thinning."""
    peak = base * (1.0 + amplitude) * max([b.factor for b in bursts] + [1.0])
    if peak <= 0:
        return []
    times = []
    t = t0
    while True:
        t += rng.expovariate(peak)
        if t >= t1:
            break
        rate = diurnal_rate(t, base, amplitude)
        for b in bursts:
            if b.covers(t):
                rate *= b.factor
                break
        if rng.random() * peak <= rate:
            times.append(t)
    return times


def pick_route(mix: dict[str, float], rng: random.Random) -> str:
    x = rng.random() * sum(mix.values())
    for route, weight in mix.items():
        x -= weight
        if x <= 0:
            return route
    return next(iter(mix))


def make_event(route: str, rng: random.Random, order_ids: list[str]) -> dict:
    """An API Gateway HTTP API (payload v2) style event."""
    event = {"version": "2.0", "routeKey": route, "rawPath": route.split(" ")[1]}
    if route == "POST /orders":
        oid = f"ord-{rng.getrandbits(48):012x}"
        order_ids.append(oid)
        if len(order_ids) > 5000:
            del order_ids[:1000]
        event["body"] = f'{{"order_id": "{oid}", "items": {rng.randint(1, 5)}, "amount_cents": {rng.randint(199, 9999)}}}'
    elif route == "GET /orders/{id}":
        oid = rng.choice(order_ids) if order_ids and rng.random() < 0.9 else f"ord-{rng.getrandbits(48):012x}"
        event["pathParameters"] = {"id": oid}
    return event
