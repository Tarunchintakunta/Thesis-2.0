"""Key designs K1-K3 and the synthetic order items (no personal data).

K1 simple     partition key orderId                       (1,000,000 distinct values)
K2 composite  partition key customerId, sort key orderTs   (10,000 partition-key values)
K3 sharded    partition key shardKey = "<orderId>#<shard>" with shard in 0..N-1

K3 shard rule (master prompt 2.1 asks for it to be documented):
  * write: shard is drawn uniformly at random for every PutItem, so repeated
    writes to one hot order are spread over N partition-key values
  * read: BatchGetItem of all N shard keys, newest `version` wins
    (scatter-gather - this is what K3 pays for spreading the writes)
  * seed: each order is loaded once, at shard = index mod N
"""
from __future__ import annotations

import datetime as dt

N_ORDERS = 1_000_000
N_CUSTOMERS = 10_000
DESIGNS = ("K1", "K2", "K3")
KEY_SCHEMA = {
    "K1": {"hash": "orderId", "range": None},
    "K2": {"hash": "customerId", "range": "orderTs"},
    "K3": {"hash": "shardKey", "range": None},
}
_BASE = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)


def order_id(i: int) -> str:
    return f"o{i:07d}"


def customer_of(i: int) -> str:
    # 7919 is prime and does not divide 10,000, so every customer gets exactly 100 orders
    return f"c{(i * 7919 + 13) % N_CUSTOMERS:05d}"


def order_ts(i: int) -> str:
    return (_BASE + dt.timedelta(seconds=31 * i)).strftime("%Y-%m-%dT%H:%M:%SZ")


def shard_key(i: int, shard: int) -> str:
    return f"{order_id(i)}#{shard}"


def key_for(design: str, i: int, shard: int = 0) -> dict:
    if design == "K1":
        return {"orderId": order_id(i)}
    if design == "K2":
        return {"customerId": customer_of(i), "orderTs": order_ts(i)}
    if design == "K3":
        return {"shardKey": shard_key(i, shard)}
    raise ValueError(f"unknown key design {design}")


def all_shard_keys(i: int, n_shards: int) -> list[dict]:
    return [{"shardKey": shard_key(i, k)} for k in range(n_shards)]


def attr_size(name: str, value) -> int:
    """DynamoDB item size rule: attribute name bytes + value bytes (numbers ~ digits/2 + 1)."""
    if isinstance(value, bool) or value is None:
        return len(name) + 1
    if isinstance(value, int | float):
        digits = len(str(abs(value)).replace(".", "").lstrip("0")) or 1
        return len(name) + (digits + 1) // 2 + 1
    return len(name) + len(str(value).encode("utf-8"))


def item_size(item: dict) -> int:
    return sum(attr_size(k, v) for k, v in item.items())


def make_item(design: str, i: int, size_kb: int, version: int, shard: int = 0, status: str = "NEW") -> dict:
    """An order item padded to just under size_kb KB, so a write costs exactly size_kb WCU."""
    item = {**key_for(design, i, shard), "orderId": order_id(i), "customerId": customer_of(i),
            "orderTs": order_ts(i), "status": status, "version": int(version), "payload": ""}
    room = size_kb * 1024 - item_size(item) - 8  # a few bytes of margin
    item["payload"] = "x" * max(0, room)
    return item
