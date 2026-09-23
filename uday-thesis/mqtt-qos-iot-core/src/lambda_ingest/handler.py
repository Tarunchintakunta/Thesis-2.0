"""IoT rule → DynamoDB ingest Lambda.

Writes one delivered-record item per invocation. Duplicates are *kept*
(same msg_id, new delivery_id) because duplication is a dependent variable.

This module is packaged by Terraform `archive_file`. Keep it stdlib-only
plus boto3 (provided on Lambda).
"""

from __future__ import annotations

import os
import time
import uuid
from typing import Any

TABLE_NAME = os.environ.get("DELIVERED_TABLE", "")
TTL_SECONDS = int(os.environ.get("TTL_SECONDS", "1209600"))


def _now_ms() -> int:
    return int(time.time() * 1000)


def normalize_event(event: Any) -> dict[str, Any]:
    if not isinstance(event, dict):
        raise ValueError("event must be a dict (IoT rule payload)")
    for key in ("payload", "data", "body"):
        nested = event.get(key)
        if isinstance(nested, dict) and "msg_id" in nested:
            return nested
    if "msg_id" not in event:
        raise ValueError("event missing msg_id")
    return event


def build_item(event: dict[str, Any], ingest_ms: int | None = None) -> dict[str, Any]:
    payload = normalize_event(event)
    now = _now_ms() if ingest_ms is None else int(ingest_ms)
    return {
        "msg_id": str(payload["msg_id"]),
        "delivery_id": str(uuid.uuid4()),
        "device_id": str(payload.get("device_id", "")),
        "qos": int(payload.get("qos", 0)),
        "seq": int(payload.get("seq", 0)),
        "run_id": str(payload.get("run_id", "")),
        "config_id": str(payload.get("config_id", "")),
        "ts_publish_ms": int(payload.get("ts_publish_ms", 0)),
        "ts_ingest_ms": now,
        "expires_at": int(now / 1000) + TTL_SECONDS,
        "source": "iot-rule",
    }


def handler(event: Any, context: Any) -> dict[str, Any]:
    item = build_item(event if isinstance(event, dict) else {})
    import boto3  # provided on Lambda

    table_name = os.environ.get("DELIVERED_TABLE", TABLE_NAME)
    table = boto3.resource("dynamodb").Table(table_name)
    table.put_item(Item=item)
    return {"ok": True, "delivery_id": item["delivery_id"]}
