"""In-memory delivered-record store standing in for DynamoDB.

Schema matches the live table: pk=msg_id, sk=delivery_id.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MockDynamoDB:
    items: list[dict[str, Any]] = field(default_factory=list)

    def put_item(self, item: dict[str, Any]) -> None:
        if "msg_id" not in item or "delivery_id" not in item:
            raise ValueError("item requires msg_id and delivery_id")
        self.items.append(dict(item))

    def query_run(self, run_id: str) -> list[dict[str, Any]]:
        return [dict(i) for i in self.items if i.get("run_id") == run_id]

    def all_items(self) -> list[dict[str, Any]]:
        return [dict(i) for i in self.items]
