"""Queue consumer Lambda.

Wired to the orders queue by an event source mapping with
``FunctionResponseTypes: [ReportBatchItemFailures]``. Records that fail on
their own (bad payload, rejected write) are returned in ``batchItemFailures`` so
only they go back to the queue. Anything that takes the whole invocation down
(kill, unhandled error, timeout) makes Lambda treat the entire batch as failed.
"""
from __future__ import annotations

import os
import time
from typing import Any

from common.faults import FaultInjector, load_fault_config
from common.models import Outcome
from common.processing import Deps, process_order_message

RECORD_FAILURES = (Outcome.WRITE_REJECTED, Outcome.INVALID)


def handle_batch(records: list[dict[str, Any]], deps: Deps) -> dict[str, Any]:
    failures = []
    for record in records:
        receive_count = int(record.get("attributes", {}).get("ApproximateReceiveCount", "1"))
        outcome = process_order_message(record["body"], record["messageId"], receive_count, deps)
        if outcome in RECORD_FAILURES:
            failures.append({"itemIdentifier": record["messageId"]})
    return {"batchItemFailures": failures}


# boto3 clients are built once per execution environment (warm starts reuse them)
_STORE = None
_EVENTS = None


def _live_deps(context) -> Deps:
    global _STORE, _EVENTS
    from common.dynamo import DynamoEventLog, DynamoOrderStore

    if _STORE is None:
        _STORE = DynamoOrderStore(os.environ["ORDERS_TABLE"])
        _EVENTS = DynamoEventLog(os.environ["EVENTS_TABLE"])
    # fault config is re-read every invocation (SSM value is cached ~5 s)
    injector = FaultInjector(load_fault_config(), hard_kill=os.environ.get("FAULT_HARD_KILL", "1") == "1")
    return Deps(
        store=_STORE,
        events=_EVENTS,
        injector=injector,
        arm="queue",
        run_id=os.environ.get("RUN_ID", ""),
        now=time.time,
        remaining_s=lambda: context.get_remaining_time_in_millis() / 1000.0,
        idempotent=os.environ.get("IDEMPOTENCY", "on") != "off",
    )


def lambda_handler(event: dict[str, Any], context) -> dict[str, Any]:
    return handle_batch(event.get("Records", []), _live_deps(context))
