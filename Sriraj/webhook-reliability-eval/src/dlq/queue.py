"""In-memory SQS + DLQ model with maxReceiveCount redrive and replay."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Message:
    body: dict[str, Any]
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    receive_count: int = 0
    visible_at: float = 0.0
    enqueued_at: float = field(default_factory=time.time)


@dataclass
class QueueStats:
    sent: int = 0
    received: int = 0
    deleted: int = 0
    redrove_to_dlq: int = 0
    replayed: int = 0


@dataclass
class InMemoryQueue:
    name: str
    max_receive_count: int = 3
    visibility_timeout_s: float = 30.0
    dlq: "InMemoryQueue | None" = None
    _messages: list[Message] = field(default_factory=list)
    stats: QueueStats = field(default_factory=QueueStats)
    now_fn: callable = time.time  # type: ignore[assignment]

    def send(self, body: dict[str, Any]) -> Message:
        msg = Message(body=dict(body), enqueued_at=self.now_fn())
        self._messages.append(msg)
        self.stats.sent += 1
        return msg

    def receive(self, max_messages: int = 1) -> list[Message]:
        now = self.now_fn()
        out: list[Message] = []
        for msg in self._messages:
            if len(out) >= max_messages:
                break
            if msg.visible_at <= now:
                msg.receive_count += 1
                msg.visible_at = now + self.visibility_timeout_s
                out.append(msg)
                self.stats.received += 1
        return out

    def delete(self, message_id: str) -> bool:
        for i, msg in enumerate(self._messages):
            if msg.message_id == message_id:
                del self._messages[i]
                self.stats.deleted += 1
                return True
        return False

    def fail(self, message_id: str) -> str:
        """Mark processing failed: redrive to DLQ if over maxReceiveCount, else reappear after VT."""
        for msg in self._messages:
            if msg.message_id == message_id:
                if self.dlq is not None and msg.receive_count >= self.max_receive_count:
                    self._messages.remove(msg)
                    self.dlq.send(msg.body)
                    self.stats.redrove_to_dlq += 1
                    return "dlq"
                # Make visible immediately for simulator (skip waiting VT in unit tests / pilot)
                msg.visible_at = self.now_fn()
                return "retry"
        return "missing"

    def depth(self) -> int:
        return len(self._messages)

    def replay_from_dlq(self, limit: int = 100) -> int:
        """Move up to `limit` DLQ messages back to this (source) queue."""
        if self.dlq is None:
            return 0
        n = 0
        while n < limit and self.dlq._messages:
            msg = self.dlq._messages.pop(0)
            # Reset receive count on replay
            fresh = Message(body=msg.body, receive_count=0, enqueued_at=self.now_fn())
            self._messages.append(fresh)
            self.stats.replayed += 1
            self.dlq.stats.deleted += 1
            n += 1
        return n
