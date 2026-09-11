"""The load-generator Lambda against in-memory DynamoDB (moto)."""
import gzip

import pytest
from botocore.exceptions import ClientError

from tests.conftest import SMALL, ZIPF_S
from workloads.lambda_handler import handler as h

PROFILE = {"read_fraction": 0.5, "cycle": [[100, 1.0]], "cycles": 1}  # 100 operations in one second


def event(design, table, tmp_path, **kw):
    ev = {"mode": "measure", "batch_id": f"t-{design}", "table": table, "key_design": design,
          "workload": "W3", "profile": PROFILE, "seed": 11, "scale": 1.0, "zipf_s": ZIPF_S,
          "orders": SMALL, "perm_seed": 1, "k3_shards": 10, "item_size_kb": 1, "threads": 8,
          "raw_dir": str(tmp_path)}
    ev.update(kw)
    return ev


@pytest.mark.parametrize("design", ["K1", "K2", "K3"])
def test_measure_batch_all_succeed(tables, tmp_path, design):
    out = h.lambda_handler(event(design, tables[design], tmp_path))
    assert out["attempted"] == out["planned_ops"] == 100
    assert out["succeeded"] == 100 and out["throttled"] == 0 and out["errors"] == 0
    assert out["reads"] + out["writes"] == 100
    assert out["latency_ms"]["p50"] > 0 and out["latency_ms"]["p99"] >= out["latency_ms"]["p50"]
    raw = gzip.decompress(open(out["raw"], "rb").read()).decode().splitlines()
    assert raw[0].startswith("seq,t_planned_s") and len(raw) == 101


def test_k3_writes_spread_over_shard_keys(tables, aws, tmp_path):
    write_only = {"read_fraction": 0.0, "cycle": [[200, 1.0]], "cycles": 1}
    h.lambda_handler(event("K3", tables["K3"], tmp_path, profile=write_only, seed=3))
    pages = aws.get_paginator("scan").paginate(TableName=tables["K3"], ProjectionExpression="shardKey")
    keys_seen = [it["shardKey"]["S"] for p in pages for it in p["Items"]]
    assert len(keys_seen) > SMALL  # new shard keys appeared next to the seeded ones
    shards = {k.split("#")[1] for k in keys_seen}
    assert len(shards) == 10


def test_same_seed_same_plan(tables, tmp_path):
    a = h.lambda_handler(event("K1", tables["K1"], tmp_path / "a"))
    b = h.lambda_handler(event("K1", tables["K1"], tmp_path / "b"))
    assert (a["reads"], a["writes"]) == (b["reads"], b["writes"])


def test_warmup_reports_cold_then_warm(tables, monkeypatch):
    monkeypatch.setattr(h, "_COLD", True)
    ev = {"mode": "warmup", "table": tables["K1"], "zipf_s": ZIPF_S, "orders": SMALL, "perm_seed": 1}
    assert h.lambda_handler(ev)["cold_start"] is True
    assert h.lambda_handler(ev)["cold_start"] is False


def test_settle_runs_base_rate_without_raw(tables, tmp_path):
    out = h.lambda_handler(event("K2", tables["K2"], tmp_path, mode="settle", seconds=0.5))
    assert out["attempted"] == 50 and "raw" not in out


def test_client_never_retries():
    # botocore turns this into total attempts; 1 = the first try only
    assert h.make_client(4).meta.config.retries["total_max_attempts"] == 1


class ThrottlingClient:
    """Every call is throttled - checks that throttles are counted, not retried or hidden."""

    def _throttle(self, **_):
        raise ClientError({"Error": {"Code": "ProvisionedThroughputExceededException", "Message": "slow down"}},
                          "PutItem")

    get_item = put_item = batch_get_item = _throttle


def test_throttles_are_counted():
    ok, throttled, code, units = h.one_op(ThrottlingClient(), "t", "K1", 5, False, 0, 1, 10)
    assert (ok, throttled, code, units) == (False, True, "ProvisionedThroughputExceededException", 0.0)
    plan = {"t": [0.0, 0.001, 0.002], "order": [1, 2, 3], "rank": [0, 1, 2], "read": [True, False, True],
            "shard_draw": [0, 0, 0]}
    rows = h.run_plan(ThrottlingClient(), plan, "t", "K1", 1, 10, 2)
    s = h.summarise(rows, 1.0)
    assert s["throttled"] == 3 and s["succeeded"] == 0 and s["errors"] == 0
    assert s["error_codes"] == {"ProvisionedThroughputExceededException": 3}


class PartialBatchClient:
    def batch_get_item(self, RequestItems, **_):
        table = next(iter(RequestItems))
        return {"Responses": {table: []}, "UnprocessedKeys": {table: {"Keys": RequestItems[table]["Keys"][:3]}},
                "ConsumedCapacity": [{"TableName": table, "CapacityUnits": 3.5}]}


def test_k3_unprocessed_keys_count_as_throttled():
    ok, throttled, code, units = h.one_op(PartialBatchClient(), "t", "K3", 5, True, 0, 1, 10)
    assert (ok, throttled, code, units) == (False, True, "UnprocessedKeys", 3.5)
