"""Integrated webhook pipeline: HMAC → queue → retry/DLQ → Redis idempotency."""
from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from dlq.queue import InMemoryQueue
from fault.injector import FaultKind, FaultPlan, decide
from idempotency.store import InMemoryIdempotencyStore, idempotency_key
from ingestion.hmac_auth import sign, verify
from metrics.collect import RunMetrics
from retry.backoff import BackoffConfig, delay_ms, should_retry


class ConfigMode(str, Enum):
    B = "B"      # baseline: no retry orchestration, no DLQ, no idempotency
    R = "R"      # retry + backoff/jitter only
    RD = "RD"    # retry + DLQ
    RDI = "RDI"  # retry + DLQ + idempotency


@dataclass
class PipelineConfig:
    mode: ConfigMode = ConfigMode.RDI
    hmac_secret: str = "test-webhook-secret"
    max_receive_count: int = 3
    visibility_timeout_s: float = 0.0  # instantaneous reappear in sim
    idem_ttl_s: int = 86_400
    backoff: BackoffConfig = field(default_factory=BackoffConfig)
    process_base_ms: float = 2.0
    process_jitter_ms: float = 1.0


@dataclass
class Pipeline:
    cfg: PipelineConfig
    rng: random.Random
    store: InMemoryIdempotencyStore = field(default_factory=InMemoryIdempotencyStore)
    main_q: InMemoryQueue = field(init=False)
    dlq: InMemoryQueue = field(init=False)
    sink: set[str] = field(default_factory=set)  # successfully processed event_ids
    metrics: RunMetrics = field(default_factory=RunMetrics)

    def __post_init__(self) -> None:
        use_dlq = self.cfg.mode in (ConfigMode.RD, ConfigMode.RDI)
        mrc = 1 if self.cfg.mode == ConfigMode.B else self.cfg.max_receive_count
        self.dlq = InMemoryQueue("dlq", max_receive_count=1)
        self.main_q = InMemoryQueue(
            "main",
            max_receive_count=mrc,
            visibility_timeout_s=self.cfg.visibility_timeout_s,
            dlq=self.dlq if use_dlq else None,
        )
        self.metrics.config = self.cfg.mode.value

    def ingest(self, event: dict[str, Any], *, signed: bool = True) -> tuple[bool, str]:
        """HMAC verify then enqueue. Returns (accepted, reason)."""
        body = json.dumps(event, sort_keys=True).encode("utf-8")
        ts = str(int(time.time()))
        if signed:
            sig = sign(self.cfg.hmac_secret, body, ts)
        else:
            sig = "deadbeef"
        auth = verify(self.cfg.hmac_secret, body, sig, ts)
        if not auth.ok:
            self.metrics.auth_rejected += 1
            return False, auth.reason
        self.main_q.send({"event": event, "body": body.decode("utf-8")})
        return True, "enqueued"

    def _process_body(self, event: dict[str, Any], fault: FaultKind) -> tuple[str, float]:
        """Simulate processing latency; return (outcome, latency_ms)."""
        lat = self.cfg.process_base_ms + self.rng.uniform(0, self.cfg.process_jitter_ms)
        if self.cfg.mode in (ConfigMode.R, ConfigMode.RD, ConfigMode.RDI):
            lat += 0.3
        if self.cfg.mode == ConfigMode.RDI:
            lat += 0.4  # Redis round-trip stand-in
        if fault == FaultKind.TRANSIENT:
            return "transient", lat
        if fault == FaultKind.PERMANENT:
            return "permanent", lat
        eid = event["event_id"]
        self.sink.add(eid)
        return "ok", lat

    def _idem_key(self, event: dict[str, Any]) -> str:
        return idempotency_key(event.get("source", "webhook"), event["event_id"])

    def drain_once(self, plan: FaultPlan) -> None:
        msgs = self.main_q.receive(1)
        if not msgs:
            return
        msg = msgs[0]
        event = msg.body["event"]
        self.metrics.attempted += 1

        # Idempotency guard (RDI only): suppress only COMPLETE; allow PROCESSING retry
        if self.cfg.mode == ConfigMode.RDI:
            key = self._idem_key(event)
            status = self.store.get(key)
            if status == "COMPLETE":
                self.metrics.duplicates_suppressed += 1
                self.main_q.delete(msg.message_id)
                self.metrics.latencies_ms.append(0.5)
                return
            if status is None:
                self.store.claim(key, ttl_s=self.cfg.idem_ttl_s)
            # status PROCESSING → continue (retry after transient)

        fault = decide(plan, self.rng)

        # Baseline (B): single attempt, no retry — any fault loses the event
        if self.cfg.mode == ConfigMode.B:
            outcome, lat = self._process_body(event, fault)
            self.metrics.latencies_ms.append(lat)
            if outcome == "ok":
                self.main_q.delete(msg.message_id)
            else:
                if outcome == "transient":
                    self.metrics.transient_failures += 1
                else:
                    self.metrics.permanent_failures += 1
                self.main_q.delete(msg.message_id)  # drop — no retry/DLQ
            return

        outcome, lat = self._process_body(event, fault)
        if outcome != "ok":
            _ = delay_ms(max(0, msg.receive_count - 1), self.cfg.backoff, self.rng)
            lat += 0.1
        self.metrics.latencies_ms.append(lat)

        if outcome == "ok":
            if self.cfg.mode == ConfigMode.RDI:
                self.store.complete(self._idem_key(event))
            self.main_q.delete(msg.message_id)
            return

        if outcome == "transient":
            self.metrics.transient_failures += 1
        else:
            self.metrics.permanent_failures += 1

        if self.cfg.mode == ConfigMode.R:
            if should_retry(msg.receive_count, self.cfg.max_receive_count):
                msg.visible_at = time.time()
            else:
                # exhausted retries, no DLQ → drop; release idempotency if any
                self.main_q.delete(msg.message_id)
            return

        # RD / RDI: fail → retry or DLQ
        result = self.main_q.fail(msg.message_id)
        if result == "dlq":
            self.metrics.dlq_captured += 1
            # Leave PROCESSING marker; replay will complete or suppress safely

    def replay_dlq(self, *, clear_permanent: bool = True) -> int:
        """Replay DLQ after fixing root cause. Recovered events land in sink."""
        if self.cfg.mode not in (ConfigMode.RD, ConfigMode.RDI):
            return 0
        recovered = 0
        pending = list(self.dlq._messages)
        self.dlq._messages.clear()
        for msg in pending:
            self.metrics.dlq_replayed += 1
            event = msg.body["event"]
            eid = event["event_id"]
            if clear_permanent or not event.get("poison"):
                if self.cfg.mode == ConfigMode.RDI:
                    key = self._idem_key(event)
                    status = self.store.get(key)
                    if status == "COMPLETE":
                        recovered += 1
                        continue
                    if status is None:
                        self.store.claim(key, ttl_s=self.cfg.idem_ttl_s)
                    self.store.complete(key)
                self.sink.add(eid)
                recovered += 1
            else:
                self.dlq._messages.append(msg)
        self.metrics.dlq_recovered += recovered
        return recovered
