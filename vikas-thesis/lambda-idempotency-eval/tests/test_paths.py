"""The three write paths and the injection mechanism against in-memory DynamoDB (moto).

These are functional checks of the implementation - not measurements of AWS.
"""
import json

import pytest

from lambda_fn import handler, paths
from tests.conftest import TABLE

PAYLOAD = {"account": "ACC-00001", "amount_cents": 1234, "currency": "EUR", "note": "x" * 700}


def event(path, rid="r-1", delivery=1, inject="none"):
    return {"request_id": rid, "path": path, "delivery": delivery, "inject": inject, "payload": PAYLOAD}


def business(ddb, rid="r-1"):
    return ddb.get_item(TableName=TABLE, Key={"pk": {"S": f"REQ#{rid}"}}, ConsistentRead=True).get("Item")


def deliver(path, n, inject="after_commit", rid="r-1"):
    """n deliveries of one request; 1..n-1 time out after commit (INJECT_MODE=raise)."""
    outs = []
    for d in range(1, n + 1):
        try:
            outs.append(handler.lambda_handler(event(path, rid, d, inject if d < n else "none")))
        except handler.InjectedTimeout as exc:
            outs.append({"timed_out": str(exc)})
    return outs


def test_p1_writes_again_on_every_delivery(ddb):
    outs = deliver("P1", 5)
    assert outs[-1]["outcome"] == "APPLIED"
    assert business(ddb)["delivery"]["N"] == "5"  # the last delivery overwrote the item


def test_p2_suppresses_redeliveries(ddb):
    outs = deliver("P2", 5)
    assert outs[-1]["outcome"] == "SUPPRESSED" and outs[-1]["ccf"] == 1
    assert business(ddb)["delivery"]["N"] == "1"  # still the first write
    assert outs[-1]["wcu_ccf_rule"] == 1.0  # billed although nothing changed


def test_p3_replays_the_stored_result(ddb):
    outs = deliver("P3", 5)
    last = outs[-1]
    assert last["outcome"] == "REPLAYED" and last["replayed_result"]["request_id"] == "r-1"
    assert business(ddb)["delivery"]["N"] == "1"
    key = ddb.get_item(TableName=TABLE, Key={"pk": {"S": "IDEMP#r-1"}})["Item"]
    assert key["status"]["S"] == "COMPLETED"


def test_p3_first_delivery_uses_three_writes(ddb):
    out = handler.lambda_handler(event("P3"))
    # moto hard-codes 0.5 units for UpdateItem, so 1 + 1 + 0.5 here; real DynamoDB bills >= 1 per write
    assert out["outcome"] == "APPLIED" and out["calls"] == 3 and out["wcu"] == 2.5


def test_p3_crash_between_writes_leaves_key_in_progress(ddb):
    with pytest.raises(handler.InjectedTimeout):
        handler.lambda_handler(event("P3", "r-9", 1, "p3_between"))
    key = ddb.get_item(TableName=TABLE, Key={"pk": {"S": "IDEMP#r-9"}})["Item"]
    assert key["status"]["S"] == "IN_PROGRESS"
    # a redelivery while the claim is still valid is refused - and writes nothing
    now = int(key["in_progress_expiry"]["N"]) - 500
    res = paths.p3(ddb, TABLE, "r-9", PAYLOAD, "e2", 2, now_ms=now, in_progress_until_ms=now + 2000)
    assert res["outcome"] == "REJECTED_IN_PROGRESS" and res["business_writes"] == 0
    # once the claim has expired (the invocation is long dead) the redelivery runs the write again
    later = int(key["in_progress_expiry"]["N"]) + 1
    res = paths.p3(ddb, TABLE, "r-9", PAYLOAD, "e3", 2, now_ms=later, in_progress_until_ms=later + 2000)
    assert res["outcome"] == "APPLIED" and res["business_writes"] == 1


def test_capacity_is_reported_for_every_call(ddb):
    out = handler.lambda_handler(event("P1", "r-c"))
    assert out["wcu"] == 1.0 and out["rcu"] == 0.0


def test_structured_log_line_is_written_before_the_failure(ddb, capsys):
    with pytest.raises(handler.InjectedTimeout):
        handler.lambda_handler(event("P2", "r-log", 1, "after_commit"))
    line = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert line["type"] == "delivery" and line["request_id"] == "r-log" and line["outcome"] == "APPLIED"
    # master prompt 6: request_id, path, delivery_index, outcome, consumed_capacity, latency_ms
    for field in ("path", "delivery_index", "consumed_capacity", "latency_ms", "exec_id", "cold_start"):
        assert field in line
    assert line["consumed_capacity"] == 1.0


def test_warmup_call_and_cold_start_flag(ddb):
    assert handler.lambda_handler({"warmup": True}) == {"type": "warmup", "cold_start": True}
    assert handler.lambda_handler(event("P1", "r-w"))["cold_start"] is False


def test_business_item_fits_one_write_unit():
    item = paths.business_item("0" * 36, PAYLOAD | {"note": "x" * 760}, "e" * 36, 1)
    assert paths.write_units(item) == 1.0


def test_unknown_path_is_rejected():
    with pytest.raises(ValueError):
        paths.run("P9", None, TABLE, "r", PAYLOAD, "e", 1)


def test_function_client_never_retries(ddb):
    assert handler.client().meta.config.retries["total_max_attempts"] == 1

def test_p4_first_delivery_uses_one_write(ddb):
    out = handler.lambda_handler(event("P4", "r-4a"))
    assert out["outcome"] == "APPLIED" and out["calls"] == 1 
    # transacts cost 2x write units, and 2 items = 4 WCU. Moto doesn't always reflect exact billing
    # but we can check if it passed.

def test_p4_suppresses_redeliveries(ddb):
    outs = deliver("P4", 5, rid="r-4b")
    last = outs[-1]
    assert last["outcome"] == "REPLAYED" and last["replayed_result"]["request_id"] == "r-4b"
    assert business(ddb, "r-4b")["delivery"]["N"] == "1"

def test_p4_no_intermittency_bug(ddb):
    # With P3, an injected crash led to a rejected_in_progress state, and a full overwrite on retry.
    # P4 has no intermediate state. It's atomic. It either fails (no items exist) or succeeds (both exist).
    # "after_commit" crashes the lambda AFTER the DynamoDB transaction completes.
    outs = deliver("P4", 2, rid="r-4c")
    # Delivery 1: crashes after the TransactWriteItems succeeds. DynamoDB has the items.
    # Delivery 2: condition fails, returns REPLAYED. 
    assert outs[-1]["outcome"] == "REPLAYED"
    assert business(ddb, "r-4c")["delivery"]["N"] == "1"

