"""Seed loader: synthetic orders into a table with BatchWriteItem, 25 items per request.

    python -m workloads.seed.seed --table ddbpk-k1-ondemand --design K1
    python -m workloads.seed.seed --all                      # all six tables from config/experiment.yaml
    python -m workloads.seed.seed --table ddbpk-k3-ondemand --design K3 --orders 2000   # pilot

K3 tables get each order once, at shard = index mod N. Unprocessed items are
retried with exponential backoff (seeding is not measured, so retries are fine
here - unlike the load generator). Run the provisioned tables with
`terraform apply -var seed_mode=true` first, see RUNBOOK.md.
"""
from __future__ import annotations

import argparse
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import boto3
import yaml
from boto3.dynamodb.types import TypeSerializer
from botocore.config import Config

from workloads.generator import keys

BATCH = 25 # BatchWriteItem limit, and the batch size fixed in the 
ROOT = Path(__file__).resolve().parents[2]
_SER = TypeSerializer()


def items_for(design: str, start: int, stop: int, kb: int, shards: int):
    # For K4, we need to know the rank to determine if it's hot (rank < 1000)
    inv_perm = None
    if design == "K4":
        from workloads.generator.zipf import Zipf
        with open(ROOT / "config/experiment.yaml", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh)
        z = Zipf(cfg["dataset"]["orders"], cfg["zipf"]["s"], cfg["zipf"]["perm_seed"])
        import numpy as np
        inv_perm = np.empty_like(z.perm)
        inv_perm[z.perm] = np.arange(len(z.perm))

    for i in range(start, stop):
        is_hot = True
        if design == "K4":
            is_hot = inv_perm[i] < 1000
        active_shards = shards if (design == "K3" or (design == "K4" and is_hot)) else 1
        yield keys.make_item(design, i, kb, version=0, shard=i % active_shards, status="NEW")


def chunks(it, n: int = BATCH):
    buf = []
    for x in it:
        buf.append(x)
        if len(buf) == n:
            yield buf
            buf = []
    if buf:
        yield buf


def write_batch(client, table: str, items: list[dict], max_tries: int = 10) -> int:
    """Write up to 25 items; returns how many retries the unprocessed items needed."""
    request = {table: [{"PutRequest": {"Item": {k: _SER.serialize(v) for k, v in it.items()}}} for it in items]}
    retries = 0
    for attempt in range(max_tries):
        resp = client.batch_write_item(RequestItems=request)
        left = resp.get("UnprocessedItems") or {}
        if not left:
            return retries
        request = left
        retries += 1
        time.sleep(min(2.0, 0.05 * 2 ** attempt))
    raise RuntimeError(f"{table}: items still unprocessed after {max_tries} tries")


def seed_table(table: str, design: str, orders: int, kb: int = 1, shards: int = 10, threads: int = 8,
               start: int = 0, client=None, progress=None) -> dict:
    client = client or boto3.client("dynamodb", config=Config(retries={"max_attempts": 10, "mode": "adaptive"},
                                                              max_pool_connections=threads + 4))
    t0 = time.perf_counter()
    done = retries = 0
    with ThreadPoolExecutor(max_workers=threads) as pool:
        futures = [pool.submit(write_batch, client, table, b) for b in chunks(items_for(design, start, orders, kb, shards))]
        for f in futures:
            retries += f.result()
            done += 1
            if progress and done % 2000 == 0:
                progress(done * BATCH)
    return {"table": table, "design": design, "items": orders - start, "requests": done, "retries": retries,
            "seconds": round(time.perf_counter() - t0, 1)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--table")
    ap.add_argument("--design", choices=keys.DESIGNS)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--orders", type=int)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--item-kb", type=int)
    ap.add_argument("--threads", type=int, default=16)
    args = ap.parse_args(argv)
    with open(ROOT / "config/experiment.yaml", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    orders = args.orders or cfg["dataset"]["orders"]
    kb = args.item_kb or cfg["dataset"]["item_size_kb"]
    if args.all:
        targets = [(f"{cfg['table_prefix']}-{d.lower()}-{m}", d) for d in keys.DESIGNS for m in ("ondemand", "provisioned")]
    elif args.table and args.design:
        targets = [(args.table, args.design)]
    else:
        ap.error("give --table and --design, or --all")
    for table, design in targets:
        stats = seed_table(table, design, orders, kb, cfg["k3_shards"], args.threads, args.start,
                           progress=lambda n, t=table: print(f"  {t}: {n:,} items"))
        print(stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
