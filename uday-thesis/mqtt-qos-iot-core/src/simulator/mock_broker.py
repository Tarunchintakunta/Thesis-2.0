"""Mock MQTT publisher + broker + IoT rule path.

THIS IS NOT AWS IOT CORE. It is a documented client-side disconnect model used
to prove the experiment harness (device-side ID log → delivered match).

Assumptions (explicit):
- QoS 0: at most once. While disconnected, intended publishes are logged and
  dropped (no client outbox). No retry, so no duplicates from this path.
- QoS 1: at least once. While disconnected, intended publishes are logged and
  queued in a local outbox (cap). On reconnect the outbox is flushed. Messages
  in an in-flight window at the cut may already have reached the broker, so a
  retry can duplicate.
- Network loss while connected is a small independent coin-flip.
- Rule/Lambda/DynamoDB is an in-memory put with simulated one-way delay.
- Subscriber persistent-session queues on IoT Core are not modelled: the
  formal CA2 disconnects the *publisher*.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from common.models import DeliveredRow
from simulator.mock_dynamodb import MockDynamoDB


@dataclass
class MockParams:
    one_way_delay_ms: float = 25.0
    delay_jitter_ms: float = 8.0
    p_network_loss_connected: float = 0.002
    p_rule_fail: float = 0.0
    qos1_outbox_cap: int = 1000
    inflight_window_s: float = 0.2
    p_inflight_already_acked: float = 0.5
    reconnect_delay_ms: float = 80.0
    reconnect_jitter_ms: float = 40.0


@dataclass
class BrokerCounters:
    publishes_attempted_connected: int = 0
    pubacks: int = 0
    reached_broker: int = 0
    rule_invocations: int = 0
    rule_failures: int = 0
    ddb_puts: int = 0
    qos0_dropped_disconnected: int = 0
    qos1_queued: int = 0
    qos1_dropped_cap: int = 0
    duplicates_injected: int = 0


class MockBroker:
    def __init__(self, table: MockDynamoDB, rng, params: MockParams | None = None) -> None:
        self.table = table
        self.rng = rng
        self.params = params or MockParams()
        self.counters = BrokerCounters()
        self._outbox: list[dict[str, Any]] = []
        self._inflight_pending_dup: list[dict[str, Any]] = []

    def _delay_ms(self) -> float:
        jitter = self.rng.uniform(-self.params.delay_jitter_ms, self.params.delay_jitter_ms)
        return max(1.0, self.params.one_way_delay_ms + jitter)

    def _deliver(self, envelope: dict[str, Any], ingest_ms: int, *, duplicate: bool = False) -> bool:
        self.counters.reached_broker += 1
        if self.rng.random() < self.params.p_rule_fail:
            self.counters.rule_failures += 1
            return False
        self.counters.rule_invocations += 1
        row = DeliveredRow(
            msg_id=envelope["msg_id"],
            delivery_id=str(uuid.uuid4()),
            device_id=envelope["device_id"],
            qos=int(envelope["qos"]),
            seq=int(envelope["seq"]),
            run_id=envelope["run_id"],
            config_id=envelope["config_id"],
            ts_publish_ms=int(envelope["ts_publish_ms"]),
            ts_ingest_ms=int(ingest_ms),
            source="mock",
        )
        self.table.put_item(row.to_dict())
        self.counters.ddb_puts += 1
        if duplicate:
            self.counters.duplicates_injected += 1
        return True

    def publish_connected(self, envelope: dict[str, Any], now_ms: int, *, maybe_inflight_cut: bool) -> None:
        self.counters.publishes_attempted_connected += 1
        qos = int(envelope["qos"])
        if self.rng.random() < self.params.p_network_loss_connected:
            if qos == 1:
                # Unacked: client will retry by queueing as if disconnected.
                self._queue(envelope)
            return
        ingest = now_ms + int(self._delay_ms())
        self._deliver(envelope, ingest)
        if qos == 1:
            self.counters.pubacks += 1
            if maybe_inflight_cut and self.rng.random() >= self.params.p_inflight_already_acked:
                # Broker got the message; PUBACK did not reach the client.
                self.counters.pubacks -= 1
                self._inflight_pending_dup.append(envelope)

    def publish_disconnected(self, envelope: dict[str, Any]) -> None:
        if int(envelope["qos"]) == 0:
            self.counters.qos0_dropped_disconnected += 1
            return
        self._queue(envelope)

    def _queue(self, envelope: dict[str, Any]) -> None:
        if len(self._outbox) >= self.params.qos1_outbox_cap:
            self.counters.qos1_dropped_cap += 1
            return
        self._outbox.append(dict(envelope))
        self.counters.qos1_queued += 1

    def flush_on_reconnect(self, reconnect_at_ms: int) -> tuple[int, int, int]:
        queued = len(self._outbox) + len(self._inflight_pending_dup)
        survived = 0
        delay = max(0.0, self.params.reconnect_delay_ms + self.rng.uniform(0, self.params.reconnect_jitter_ms))
        t = reconnect_at_ms + int(delay)
        for env in self._inflight_pending_dup:
            t += int(self._delay_ms())
            if self._deliver(env, t, duplicate=True):
                survived += 1
        self._inflight_pending_dup.clear()
        for env in self._outbox:
            t += int(self._delay_ms())
            env = dict(env)
            env["ts_publish_ms"] = t  # republish time after reconnect
            if self._deliver(env, t + int(self._delay_ms())):
                survived += 1
            if int(env["qos"]) == 1:
                self.counters.pubacks += 1
        self._outbox.clear()
        return queued, survived, int(delay)

    def outbox_depth(self) -> int:
        return len(self._outbox) + len(self._inflight_pending_dup)
