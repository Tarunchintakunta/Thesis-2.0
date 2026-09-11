from tests.conftest import SMALL, create_table
from workloads.generator import keys
from workloads.seed.seed import chunks, items_for, seed_table, write_batch


def test_chunks_of_25():
    sizes = [len(c) for c in chunks(range(103))]
    assert sizes == [25, 25, 25, 25, 3]


def test_k3_seed_uses_index_mod_n():
    first = list(items_for("K3", 0, 12, 1, 10))
    assert first[3]["shardKey"] == "o0000003#3" and first[11]["shardKey"] == "o0000011#1"


def test_seed_loads_every_order_once(aws):
    create_table(aws, "K2", "seed-k2")
    stats = seed_table("seed-k2", "K2", SMALL, kb=1, shards=10, threads=4, client=aws)
    assert stats["items"] == SMALL and stats["requests"] == SMALL // 25
    assert aws.describe_table(TableName="seed-k2")["Table"]["ItemCount"] in (0, SMALL)  # moto may lag
    count = sum(len(p["Items"]) for p in aws.get_paginator("scan").paginate(TableName="seed-k2"))
    assert count == SMALL
    got = aws.get_item(TableName="seed-k2", Key={"customerId": {"S": keys.customer_of(7)},
                                                  "orderTs": {"S": keys.order_ts(7)}})["Item"]
    assert got["orderId"]["S"] == "o0000007"


class FlakyClient:
    """First call leaves 5 items unprocessed, then everything goes through."""

    def __init__(self):
        self.calls = 0

    def batch_write_item(self, RequestItems):
        self.calls += 1
        table = next(iter(RequestItems))
        if self.calls == 1:
            return {"UnprocessedItems": {table: RequestItems[table][:5]}}
        return {"UnprocessedItems": {}}


def test_unprocessed_items_are_retried():
    c = FlakyClient()
    retries = write_batch(c, "t", list(items_for("K1", 0, 25, 1, 10)))
    assert retries == 1 and c.calls == 2
