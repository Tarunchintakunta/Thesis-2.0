"""The three application-level write paths (master prompt 2.3).

P1 plain put        unconditional PutItem - a redelivery writes the item again
P2 conditional put  PutItem with attribute_not_exists(pk) - a redelivery fails the condition
P3 idempotency key  Powertools-style: claim IDEMP#<request_id> as IN_PROGRESS, do the business
                    write, mark the key COMPLETED with the stored result; a redelivery gets the
                    stored result back (REPLAYED) or is refused while the key is IN_PROGRESS

Every call asks for ReturnConsumedCapacity=TOTAL. A failed condition is still billed,
but its error response has no ConsumedCapacity, so those units are added from the
documented rule (one write unit per started KB of the item) in a separate field.
"""
from __future__ import annotations

import json
import math
import time

from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from botocore.exceptions import ClientError

CCF = "ConditionalCheckFailedException"
_SER, _DES = TypeSerializer(), TypeDeserializer()


def typed(d: dict) -> dict:
    return {k: _SER.serialize(v) for k, v in d.items()}


def plain(d: dict) -> dict:
    return {k: _DES.deserialize(v) for k, v in d.items()}


def item_bytes(item: dict) -> int:
    size = 0
    for k, v in item.items():
        if isinstance(v, bool) or v is None:
            size += len(k) + 1
        elif isinstance(v, int | float):
            size += len(k) + (len(str(abs(v)).replace(".", "")) + 1) // 2 + 1
        else:
            size += len(k) + len(str(v).encode("utf-8"))
    return size


def write_units(item: dict) -> float:
    return float(max(1, math.ceil(item_bytes(item) / 1024)))


def _cc(resp: dict) -> float:
    return float((resp.get("ConsumedCapacity") or {}).get("CapacityUnits", 0.0))


def business_item(request_id: str, payload: dict, exec_id: str, delivery: int) -> dict:
    # exec_id differs on every delivery, so a repeated write always changes the item
    return {"pk": f"REQ#{request_id}", "request_id": request_id, **payload, "exec_id": exec_id,
            "delivery": int(delivery), "written_at_ms": int(time.time() * 1000)}


def _result(outcome: str, **kw) -> dict:
    base = {"outcome": outcome, "rcu": 0.0, "wcu": 0.0, "wcu_ccf_rule": 0.0, "ccf": 0, "calls": 0,
            "business_writes": 0}
    base.update(kw)
    return base


def p1(client, table, request_id, payload, exec_id, delivery, **_):
    item = business_item(request_id, payload, exec_id, delivery)
    resp = client.put_item(TableName=table, Item=typed(item), ReturnConsumedCapacity="TOTAL")
    return _result("APPLIED", wcu=_cc(resp), calls=1, business_writes=1)


def p2(client, table, request_id, payload, exec_id, delivery, **_):
    item = business_item(request_id, payload, exec_id, delivery)
    try:
        resp = client.put_item(TableName=table, Item=typed(item), ConditionExpression="attribute_not_exists(pk)",
                               ReturnConsumedCapacity="TOTAL")
        return _result("APPLIED", wcu=_cc(resp), calls=1, business_writes=1)
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") != CCF:
            raise
        reported = _cc(exc.response)
        return _result("SUPPRESSED", wcu=reported, wcu_ccf_rule=0.0 if reported else write_units(item), ccf=1, calls=1)


def p3(client, table, request_id, payload, exec_id, delivery, now_ms, in_progress_until_ms, ttl_s=3600,
       between=None, **_):
    now_s = now_ms // 1000
    key = {"pk": f"IDEMP#{request_id}", "status": "IN_PROGRESS", "in_progress_expiry": int(in_progress_until_ms),
           "expiry": int(now_s + ttl_s), "owner": exec_id}
    try:
        r = client.put_item(
            TableName=table, Item=typed(key),
            ConditionExpression="attribute_not_exists(pk) OR (#s = :inprog AND in_progress_expiry < :now) OR #e < :now_s",
            ExpressionAttributeNames={"#s": "status", "#e": "expiry"},
            ExpressionAttributeValues={":inprog": {"S": "IN_PROGRESS"}, ":now": {"N": str(int(now_ms))},
                                       ":now_s": {"N": str(int(now_s))}},
            ReturnValuesOnConditionCheckFailure="ALL_OLD", ReturnConsumedCapacity="TOTAL")
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") != CCF:
            raise
        old = plain(exc.response.get("Item", {}))
        reported = _cc(exc.response)
        rule = 0.0 if reported else write_units(key)
        if old.get("status") == "COMPLETED":
            return _result("REPLAYED", wcu=reported, wcu_ccf_rule=rule, ccf=1, calls=1,
                           replayed_result=json.loads(old.get("result", "{}")))
        return _result("REJECTED_IN_PROGRESS", wcu=reported, wcu_ccf_rule=rule, ccf=1, calls=1)
    wcu = _cc(r)
    item = business_item(request_id, payload, exec_id, delivery)
    r = client.put_item(TableName=table, Item=typed(item), ReturnConsumedCapacity="TOTAL")
    wcu += _cc(r)
    if between is not None:  # sensitivity case: crash after the business write, key still IN_PROGRESS
        between(_result("CRASH_BETWEEN", wcu=wcu, calls=2, business_writes=1))
    result = {"request_id": request_id, "applied_by": exec_id}
    r = client.update_item(
        TableName=table, Key=typed({"pk": key["pk"]}),
        UpdateExpression="SET #s = :done, #r = :res, #e = :exp",
        ExpressionAttributeNames={"#s": "status", "#r": "result", "#e": "expiry"},
        ExpressionAttributeValues={":done": {"S": "COMPLETED"}, ":res": {"S": json.dumps(result)},
                                   ":exp": {"N": str(int(now_s + ttl_s))}},
        ReturnConsumedCapacity="TOTAL")
    wcu += _cc(r)
    return _result("APPLIED", wcu=wcu, calls=3, business_writes=1)


def p4(client, table, request_id, payload, exec_id, delivery, now_ms, ttl_s=3600, between=None, **_):
    now_s = now_ms // 1000
    result = {"request_id": request_id, "applied_by": exec_id}
    key_item = {
        "pk": f"IDEMP#{request_id}",
        "status": "COMPLETED",
        "result": json.dumps(result),
        "expiry": int(now_s + ttl_s),
        "owner": exec_id
    }
    b_item = business_item(request_id, payload, exec_id, delivery)
    
    try:
        resp = client.transact_write_items(
            TransactItems=[
                {
                    "Put": {
                        "TableName": table,
                        "Item": typed(key_item),
                        "ConditionExpression": "attribute_not_exists(pk)",
                        "ReturnValuesOnConditionCheckFailure": "ALL_OLD"
                    }
                },
                {
                    "Put": {
                        "TableName": table,
                        "Item": typed(b_item)
                    }
                }
            ],
            ReturnConsumedCapacity="TOTAL"
        )
        wcu = sum(_cc(cap) for cap in resp.get("ConsumedCapacity", []))
        if between is not None:
            between(_result("CRASH_BETWEEN", wcu=wcu, calls=1, business_writes=1))
        return _result("APPLIED", wcu=wcu, calls=1, business_writes=1)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code == "TransactionCanceledException":
            reasons = exc.response.get("CancellationReasons", [])
            if reasons and reasons[0].get("Code") == "ConditionalCheckFailed":
                # It exists! It's a replay.
                old = plain(reasons[0].get("Item", {}))
                
                # AWS currently does not return ConsumedCapacity on TransactionCanceledException uniformly,
                # but it bills for the condition check on transactions.
                # A rejected transact write item is billed 1 WCU per item. So 2 WCUs rule.
                reported = sum(_cc(cap) for cap in exc.response.get("ConsumedCapacity", []))
                rule = 2.0 if not reported else 0.0
                
                if old.get("status") == "COMPLETED":
                    return _result("REPLAYED", wcu=reported, wcu_ccf_rule=rule, ccf=1, calls=1,
                                   replayed_result=json.loads(old.get("result", "{}")))
        raise

PATHS = {"P1": p1, "P2": p2, "P3": p3, "P4": p4}


def run(path: str, client, table: str, request_id: str, payload: dict, exec_id: str, delivery: int, **kw) -> dict:
    if path not in PATHS:
        raise ValueError(f"unknown path {path}")
    t0 = time.perf_counter()
    res = PATHS[path](client, table, request_id, payload, exec_id, delivery, **kw)
    res["ddb_ms"] = round((time.perf_counter() - t0) * 1000, 3)
    return res
