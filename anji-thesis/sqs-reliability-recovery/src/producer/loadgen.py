"""Load profiles and the live senders.

Profiles (all seeded, so the same config always gives the same schedule):

* ``normal`` - Poisson arrivals at ``rate`` msg/s
* ``burst``  - same, but ``burst_factor`` x faster during a burst window
* ``batch``  - the whole workload is pushed as fast as SendMessageBatch
  allows, before/while consumers drain it. This mirrors the "process a big
  batch of records" setup of the Kyrychenko et al. (2025) baseline.
"""
from __future__ import annotations

import json
import random
import time
import urllib.error
import urllib.request
from typing import Any, Sequence

from common.models import Order

PROFILES = ("normal", "burst", "batch")


def arrival_times(
    n: int,
    profile: str,
    rate: float,
    seed: int,
    burst_start: float = 30.0,
    burst_len: float = 15.0,
    burst_factor: float = 5.0,
    preload_rate: float = 500.0,
) -> list[float]:
    """Send offsets in seconds from the start of the run."""
    if profile not in PROFILES:
        raise ValueError(f"unknown load profile {profile!r}")
    if n <= 0:
        return []
    if profile == "batch":
        return [i / preload_rate for i in range(n)]

    rng = random.Random(seed)
    times: list[float] = []
    t = 0.0
    while len(times) < n:
        current = rate
        if profile == "burst" and burst_start <= t < burst_start + burst_len:
            current = rate * burst_factor
        t += rng.expovariate(current)
        times.append(t)
    return times


# ---------------------------------------------------------------------------
# live senders (DRY_RUN=0 only)
# ---------------------------------------------------------------------------

def send_to_sqs(
    sqs_client,
    queue_url: str,
    orders: Sequence[Order],
    offsets: Sequence[float],
    delay_s: int = 0,
    clock=time.time,
    sleep=time.sleep,
) -> dict[str, float]:
    """Send orders following the schedule. Returns order_id -> produce time."""
    produced: dict[str, float] = {}
    start = clock()
    i = 0
    while i < len(orders):
        wait = start + offsets[i] - clock()
        if wait > 0:
            sleep(wait)
        # group everything that is already due into one SendMessageBatch (max 10)
        now_rel = clock() - start
        batch = []
        while i < len(orders) and len(batch) < 10 and offsets[i] <= now_rel + 0.05:
            batch.append(orders[i])
            i += 1
        if not batch:
            batch.append(orders[i])
            i += 1
        entries = [
            {"Id": str(k), "MessageBody": o.to_json(), "DelaySeconds": int(delay_s)}
            for k, o in enumerate(batch)
        ]
        resp = sqs_client.send_message_batch(QueueUrl=queue_url, Entries=entries)
        sent_at = clock()
        failed = {f["Id"] for f in resp.get("Failed", [])}
        for k, o in enumerate(batch):
            if str(k) not in failed:
                produced[o.order_id] = sent_at
    return produced


def post_to_api(
    api_url: str,
    orders: Sequence[Order],
    offsets: Sequence[float],
    retries: int = 2,
    backoff_s: float = 0.2,
    timeout_s: float = 30.0,
    clock=time.time,
    sleep=time.sleep,
) -> list[dict[str, Any]]:
    """Sync arm: POST each order, the client retries a couple of times."""
    results = []
    start = clock()
    for order, offset in zip(orders, offsets):
        wait = start + offset - clock()
        if wait > 0:
            sleep(wait)
        produced_at = clock()
        status = None
        attempts = 0
        for attempt in range(retries + 1):
            attempts += 1
            req = urllib.request.Request(
                api_url,
                data=order.to_json().encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                    status = resp.status
            except urllib.error.HTTPError as err:
                status = err.code
            except (urllib.error.URLError, TimeoutError):
                status = 599
            if status == 200:
                break
            sleep(backoff_s * (2**attempt))
        results.append(
            {
                "order_id": order.order_id,
                "produced_at": produced_at,
                "done_at": clock(),
                "status": status,
                "attempts": attempts,
                "body": json.loads(order.to_json()),
            }
        )
    return results
