"""Write-path Lambda: one delivery of one request through P1, P2 or P3.

Event
    request_id   the driver's id - the same on every delivery of a request
    path         P1 | P2 | P3
    delivery     1..N
    inject       none | after_commit | p3_between
    payload      synthetic business fields (data/payload_template.json)

Injected timeout : after the path's writes have
committed, the handler logs its record and then sleeps past the function
timeout, so the platform ends the invocation with "Task timed out" while the
state change is already in DynamoDB. The driver sees a failure and redelivers
the same request_id. With INJECT_MODE=raise (local driver, tests) it raises
InjectedTimeout instead of sleeping.

SDK retries are off (total_max_attempts = 1): the only retries in the
experiment are the driver's scheduled ones, so the ground truth stays known.
"""
from __future__ import annotations

import json
import os
import time
import uuid

import boto3
from botocore.config import Config

from lambda_fn import paths

TTL_S = int(os.environ.get("P3_KEY_TTL_S", "3600"))
_CLIENT = None
_COLD = True  # first call in this execution environment (a timeout resets the environment, so it comes back)


def table_name(event: dict) -> str:
    # read per call, not at import, so the local driver and the tests can point it elsewhere
    return event.get("table") or os.environ.get("TABLE_NAME", "idem-eval")


class InjectedTimeout(Exception):
    """Local stand-in for the Lambda timeout (INJECT_MODE=raise)."""


def client():
    global _CLIENT
    if _CLIENT is None:
        region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "eu-west-1"
        _CLIENT = boto3.client("dynamodb", region_name=region,
                               config=Config(retries={"total_max_attempts": 1, "mode": "standard"}))
    return _CLIENT


def _log(record: dict) -> None:
    print(json.dumps({"type": "delivery", **record}), flush=True)


def _fail_after_commit(record: dict, context) -> None:
    _log(record)  # written before failing, so the driver can still read the capacity from the log tail
    if os.environ.get("INJECT_MODE", "sleep") == "raise":
        raise InjectedTimeout(json.dumps(record))
    remaining = context.get_remaining_time_in_millis() / 1000 if context else 2.0
    time.sleep(remaining + 1.0)  # the platform stops the invocation at its timeout


def _record(base: dict, res: dict, t0: float) -> dict:
    return {**base, **res, "consumed_capacity": round(res["rcu"] + res["wcu"], 3),
            "latency_ms": round((time.perf_counter() - t0) * 1000, 3)}


def lambda_handler(event: dict, context=None) -> dict:
    global _COLD
    cold, _COLD = _COLD, False
    if event.get("warmup"):  # driver warm-up call, no table access
        return {"type": "warmup", "cold_start": cold}
    t0 = time.perf_counter()
    path, rid = event["path"], event["request_id"]
    delivery, inject = int(event.get("delivery", 1)), event.get("inject", "none")
    exec_id = getattr(context, "aws_request_id", None) or f"local-{uuid.uuid4()}"
    now_ms = int(time.time() * 1000)
    remaining = context.get_remaining_time_in_millis() if context else 2000
    base = {"request_id": rid, "path": path, "delivery": delivery, "delivery_index": delivery, "exec_id": exec_id,
            "inject": inject, "cold_start": cold}

    def crash_between(partial: dict) -> None:
        _fail_after_commit(_record(base, partial, t0), context)

    res = paths.run(path, client(), table_name(event), rid, event["payload"], exec_id, delivery,
                    now_ms=now_ms, in_progress_until_ms=now_ms + remaining, ttl_s=TTL_S,
                    between=crash_between if (inject == "p3_between" and path == "P3") else None)
    record = _record(base, res, t0)
    if inject == "after_commit":
        _fail_after_commit(record, context)
    _log(record)
    return record
