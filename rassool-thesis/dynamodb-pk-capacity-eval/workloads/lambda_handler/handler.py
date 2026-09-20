"""Load-generator Lambda: one measured batch (or a settle / warm-up call) against one table.

Event (built by scripts/run_matrix.py):
    mode          measure | settle | warmup
    batch_id      e.g. "b07-K2-provisioned-W4-r12-l1"
    table         e.g. "ddbpk-k2-provisioned"
    key_design    K1 | K2 | K3
    workload      W1..W4 (profiles.py), or `profile` with an explicit override (tests, pilot)
    seed          decides keys, read/write mix and K3 shards - batches are reproducible
    scale         this Lambda's share of the offered rate (1 / lambdas_per_batch)
    seconds       settle only: run the base-rate phase this long
    zipf_s, orders, perm_seed, k3_shards, item_size_kb, threads
    results_bucket / raw_dir   where the per-operation CSV goes (measure only)

SDK retries are switched off (total_max_attempts = 1), so every throttle reaches the
record instead of being hidden inside the client. Arrivals are open-loop: an
operation is dispatched at its planned time whether or not earlier ones have
finished; `response_ms` (from the planned time) includes any generator backlog,
`latency_ms` is the service time of the call itself.
"""
from __future__ import annotations

import csv
import gzip
import io
import os
import time
from concurrent.futures import ThreadPoolExecutor

import boto3
import numpy as np
from boto3.dynamodb.types import TypeSerializer
from botocore.config import Config
from botocore.exceptions import ClientError

from workloads.generator import keys
from workloads.generator.profiles import PROFILES, op_plan
from workloads.generator.zipf import Zipf

THROTTLE_CODES = {"ProvisionedThroughputExceededException", "ThrottlingException", "RequestLimitExceeded"}
RAW_FIELDS = ["seq", "t_planned_s", "t_start_s", "latency_ms", "response_ms", "op", "order", "rank",
              "ok", "throttled", "code", "units"]

_COLD = True          # first call in this execution environment
_ZIPF: dict = {}      # CDF + permutation are built once per environment (in the warm-up call)
_SER = TypeSerializer()


def _zipf(n: int, s: float, seed: int) -> Zipf:
    key = (n, s, seed)
    if key not in _ZIPF:
        _ZIPF[key] = Zipf(n, s, seed)
    return _ZIPF[key]


def _typed(d: dict) -> dict:
    return {k: _SER.serialize(v) for k, v in d.items()}


def make_client(threads: int, endpoint_url: str | None = None, region: str | None = None):
    # total_max_attempts = 1 means no retry at all. (botocore's "max_attempts": 1 would still
    # allow one retry - it counts retries, not attempts - and that would hide throttles.)
    cfg = Config(retries={"total_max_attempts": 1, "mode": "standard"}, max_pool_connections=threads + 4,
                 connect_timeout=2, read_timeout=5)
    region = region or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "eu-west-1"
    return boto3.client("dynamodb", config=cfg, endpoint_url=endpoint_url, region_name=region)


def _units(resp: dict) -> float:
    cc = resp.get("ConsumedCapacity")
    if isinstance(cc, list):
        return float(sum(c.get("CapacityUnits", 0.0) for c in cc))
    return float((cc or {}).get("CapacityUnits", 0.0))


def one_op(client, table: str, design: str, order: int, is_read: bool, shard_draw: int,
           kb: int, shards: int, rank: int) -> tuple:
    """Returns (ok, throttled, code, units)."""
    try:
        is_hot = True if design == "K3" else (rank < 1000)
        active_shards = shards if is_hot else 1

        if is_read and design in ("K3", "K4"):
            resp = client.batch_get_item(
                RequestItems={table: {"Keys": [_typed(k) for k in keys.all_shard_keys(design, order, shards, is_hot)]}},
                ReturnConsumedCapacity="TOTAL")
            left = len(resp.get("UnprocessedKeys", {}).get(table, {}).get("Keys", []))
            # unprocessed keys are how a batch call reports throttling
            return (left == 0, left > 0, "UnprocessedKeys" if left else "", _units(resp))
        if is_read:
            resp = client.get_item(TableName=table, Key=_typed(keys.key_for(design, order)),
                                   ReturnConsumedCapacity="TOTAL")
            return (True, False, "", _units(resp))
        shard = shard_draw % active_shards if design in ("K3", "K4") else 0
        item = keys.make_item(design, order, kb, version=time.time_ns() // 1000, shard=shard, status="UPDATED")
        resp = client.put_item(TableName=table, Item=_typed(item), ReturnConsumedCapacity="TOTAL")
        return (True, False, "", _units(resp))
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "ClientError")
        return (False, code in THROTTLE_CODES, code, 0.0)

def run_plan(client, plan: dict, table: str, design: str, kb: int, shards: int, threads: int) -> list[list]:
    n = len(plan["t"])
    rows: list = [None] * n
    t0 = time.perf_counter() + 0.05

    def work(k: int):
        target = t0 + plan["t"][k]
        start = time.perf_counter()
        ok, throttled, code, units = one_op(client, table, design, int(plan["order"][k]), bool(plan["read"][k]),
                                            int(plan["shard_draw"][k]), kb, shards, int(plan["rank"][k]))
        end = time.perf_counter()
        rows[k] = [k, round(plan["t"][k], 6), round(start - t0, 6), round((end - start) * 1000, 3),
                   round((end - target) * 1000, 3), "R" if plan["read"][k] else "W", int(plan["order"][k]),
                   int(plan["rank"][k]), int(ok), int(throttled), code, units]

    with ThreadPoolExecutor(max_workers=threads) as pool:
        for k in range(n):
            delay = t0 + plan["t"][k] - time.perf_counter()
            if delay > 0:
                time.sleep(delay)
            pool.submit(work, k)
    return rows


def summarise(rows: list[list], wall_s: float) -> dict:
    a = np.array([[r[3], r[4], r[8], r[9], r[11], r[5] == "R", r[2] - r[1]] for r in rows], dtype=float)
    lat, resp, ok, thr, units, is_read, lag = (a[:, i] for i in range(7))
    good = ok == 1

    def pct(x):
        return {"mean": float(x.mean()), "p50": float(np.percentile(x, 50)), "p95": float(np.percentile(x, 95)),
                "p99": float(np.percentile(x, 99))} if len(x) else {}

    codes: dict = {}
    for r in rows:
        if r[10]:
            codes[r[10]] = codes.get(r[10], 0) + 1
    return {"attempted": len(rows), "succeeded": int(good.sum()), "throttled": int(thr.sum()),
            "errors": int((~good & (thr == 0)).sum()), "reads": int(is_read.sum()), "writes": int((~is_read.astype(bool)).sum()),
            "rcu": float(units[is_read == 1].sum()), "wcu": float(units[is_read == 0].sum()),
            "latency_ms": pct(lat[good]), "response_ms": pct(resp[good]),
            "lag_ms_p99": float(np.percentile(lag, 99) * 1000) if len(lag) else 0.0,
            "wall_s": wall_s, "throughput_ops_s": float(good.sum() / wall_s) if wall_s > 0 else 0.0,
            "error_codes": codes}


def _write_raw(rows, event: dict) -> str | None:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(RAW_FIELDS)
    w.writerows(rows)
    data = gzip.compress(buf.getvalue().encode(), mtime=0)
    name = f"{event['batch_id']}.csv.gz"
    if event.get("raw_dir"):
        os.makedirs(event["raw_dir"], exist_ok=True)
        path = os.path.join(event["raw_dir"], name)
        with open(path, "wb") as fh:
            fh.write(data)
        return path
    if event.get("results_bucket"):
        key = f"raw/{name}"
        boto3.client("s3").put_object(Bucket=event["results_bucket"], Key=key, Body=data)
        return f"s3://{event['results_bucket']}/{key}"
    return None


def lambda_handler(event: dict, context=None) -> dict:
    global _COLD
    cold, _COLD = _COLD, False
    z = _zipf(int(event.get("orders", keys.N_ORDERS)), float(event["zipf_s"]), int(event.get("perm_seed", 20250920)))
    threads = int(event.get("threads", 32))
    client = make_client(threads, event.get("endpoint_url"))
    if event.get("mode") == "warmup":
        client.describe_table(TableName=event["table"])
        return {"mode": "warmup", "cold_start": cold, "table": event["table"]}

    profile = event.get("profile") or PROFILES[event["workload"]]
    if event.get("mode") == "settle":
        rate = profile["cycle"][0][0]
        profile = {**profile, "cycle": [(rate, float(event["seconds"]))], "cycles": 1}
    plan = op_plan(profile, z, int(event["seed"]), float(event.get("scale", 1.0)))
    design, kb, shards = event["key_design"], int(event.get("item_size_kb", 1)), int(event.get("k3_shards", 10))
    t_start = time.time()
    w0 = time.perf_counter()
    rows = run_plan(client, plan, event["table"], design, kb, shards, threads)
    wall = time.perf_counter() - w0
    out = {"mode": event.get("mode", "measure"), "batch_id": event.get("batch_id"), "table": event["table"],
           "key_design": design, "workload": event.get("workload"), "seed": int(event["seed"]),
           "scale": float(event.get("scale", 1.0)), "cold_start": cold, "planned_ops": len(plan["t"]),
           "t_start_epoch": t_start, "t_end_epoch": time.time(), **summarise(rows, wall)}
    if out["mode"] == "measure":
        out["raw"] = _write_raw(rows, event)
    return out
