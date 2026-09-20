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
TTL_SECONDS = int(os.environ.get("TTL_SECONDS", str(14 * 86400)))


def _now_ms() -> int:
    return int(time.time() * 1000)


def normalize_event(event: Any) -> dict[str, Any]:
    if not isinstance(event, dict):
        raise ValueError("event must be a dict (IoT rule payload)")
    if "msg_id" in event:
        return event
    # Some rule encodings wrap the payload.
    for key in ("payload", "data", "body"):
        inner = event.get(key)
        if isinstance(inner, dict) and "msg_id" in inner:
            return inner
    raise ValueError("event missing msg_id")


def build_item(event: dict[str, Any], ingest_ms: int | None = None) -> dict[str, Any]:
    body = normalize_event(event)
    now_ms = ingest_ms if ingest_ms is not None else _now_ms()
    now_s = int(now_ms / 1000)
    return {
        "msg_id": str(body["msg_id"]),
        "delivery_id": str(body.get("delivery_id") or uuid.uuid4()),
        "device_id": str(body.get("device_id", "")),
        "qos": int(body.get("qos", 0)),
        "seq": int(body.get("seq", 0)),
        "run_id": str(body.get("run_id", "")),
        "config_id": str(body.get("config_id", "")),
        "ts_publish_ms": int(body.get("ts_publish_ms", now_ms)),
        "ts_ingest_ms": now_ms,
        "expires_at": now_s + TTL_SECONDS,
    }


def handler(event, context):  # noqa: ANN001
    item = build_item(event)
    if os.environ.get("DRY_RUN_HANDLER") == "1" or not TABLE_NAME:
        return {"ok": True, "dry_run": True, "item": item}
    import boto3  # provided in Lambda

    table = boto3.resource("dynamodb").Table(TABLE_NAME)
    table.put_item(Item=item)
    return {"ok": True, "delivery_id": item["delivery_id"]}
