#!/usr/bin/env python
"""Run the matrix: warm-up -> settle -> measured batch for every cell, in randomised blocks.

    python scripts/run_matrix.py --dry-run                       # print the plan and the cost estimate
    python scripts/run_matrix.py --results-bucket <bucket> --out results/          # live campaign
    python scripts/run_matrix.py --pilot --results-bucket <bucket> --out results_pilot/
    python scripts/run_matrix.py --backend local --moto --blocks 2 --workloads W3,W4 \\
        --rate-scale 0.05 --time-scale 0.02 --orders 2000 --out results_smoke/      # CI smoke

Resumable: batch ids already in <out>/batches.csv are skipped. `--moto` runs the
real handler against an in-memory fake DynamoDB - its numbers only prove the
pipeline works and are labelled data_source = moto-smoke.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from analysis.batch_metrics import batch_metrics, read_raw  # noqa: E402
from analysis.cost_model import load_prices, on_demand_cost, provisioned_cost  # noqa: E402
from analysis.design_checks import capacity_plan  # noqa: E402
from workloads.generator.profiles import PROFILES, duration_s, planned_ops  # noqa: E402
from workloads.matrix import CONFIGS, lambda_events, scaled_profile, schedule  # noqa: E402


class LambdaBackend:
    source = "live"

    def __init__(self, function_name: str, region: str, results_bucket: str):
        import boto3
        from botocore.config import Config

        self.fn = function_name
        self.bucket = results_bucket
        self.lam = boto3.client("lambda", region_name=region,
                                config=Config(read_timeout=960, retries={"total_max_attempts": 1}))
        self.s3 = boto3.client("s3", region_name=region)

    def extra(self) -> dict:
        return {"results_bucket": self.bucket}

    def invoke(self, events: list[dict]) -> list[dict]:
        def one(ev):
            resp = self.lam.invoke(FunctionName=self.fn, Payload=json.dumps(ev).encode())
            body = json.loads(resp["Payload"].read())
            if resp.get("FunctionError"):
                raise RuntimeError(f"driver failed: {body}")
            return body

        with ThreadPoolExecutor(max_workers=len(events)) as pool:
            return list(pool.map(one, events))

    def fetch_raw(self, ref: str) -> bytes:
        bucket, key = ref.removeprefix("s3://").split("/", 1)
        return self.s3.get_object(Bucket=bucket, Key=key)["Body"].read()


class LocalBackend:
    """The handler in this process - against moto, or DynamoDB Local via --endpoint-url."""

    def __init__(self, raw_dir: Path, endpoint_url: str | None = None, source: str = "local"):
        from workloads.lambda_handler import handler

        self.handler = handler
        self.raw_dir = raw_dir
        self.endpoint = endpoint_url
        self.source = source

    def extra(self) -> dict:
        ex = {"raw_dir": str(self.raw_dir)}
        if self.endpoint:
            ex["endpoint_url"] = self.endpoint
        return ex

    def invoke(self, events: list[dict]) -> list[dict]:
        with ThreadPoolExecutor(max_workers=len(events)) as pool:
            return list(pool.map(self.handler.lambda_handler, events))

    def fetch_raw(self, ref: str) -> bytes:
        return Path(ref).read_bytes()


def estimate(cfg: dict, cells: list[dict], prices: dict, rate_scale: float, time_scale: float) -> dict:
    """Up-front cost estimate (arithmetic, before any run)."""
    cap = capacity_plan(cfg).set_index("key_design")
    kb = cfg["dataset"]["item_size_kb"]
    total = 0.0
    hours = 0.0
    for c in cells:
        p = PROFILES[c["workload"]]
        ops = planned_ops(p) * rate_scale + p["cycle"][0][0] * rate_scale * cfg["settling_seconds"] * time_scale
        secs = (duration_s(p) + cfg["settling_seconds"]) * time_scale
        hours += secs / 3600
        reads = ops * p["read_fraction"]
        rcu = reads * 0.5 * (cfg["k3_shards"] if c["key_design"] == "K3" else 1) * max(1, kb / 4)
        wcu = (ops - reads) * kb
        if c["capacity_mode"] == "on_demand":
            total += on_demand_cost(rcu, wcu, prices)
        else:
            row = cap.loc[c["key_design"]]
            total += provisioned_cost(row.read_min, row.write_min, secs, prices)
    return {"cells": len(cells), "hours_of_load": round(hours, 2), "request_path_usd": round(total, 2)}


def done_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(pd.read_csv(path)["batch_id"])


def append_row(path: Path, row: dict) -> None:
    new = not path.exists()
    with open(path, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(row))
        if new:
            w.writeheader()
        w.writerow(row)


def seed_moto(cfg: dict, orders: int) -> None:
    import boto3

    from tests.conftest import create_table
    from workloads.matrix import table_name
    from workloads.seed.seed import seed_table

    client = boto3.client("dynamodb", region_name=cfg["region"])
    for k, m in CONFIGS:
        name = table_name(cfg["table_prefix"], k, m)
        create_table(client, k, name)
        seed_table(name, k, orders, kb=cfg["dataset"]["item_size_kb"], shards=cfg["k3_shards"], threads=4, client=client)


def run(cfg: dict, cells: list[dict], backend, out: Path, rate_scale: float, time_scale: float,
        lambdas: int, log=print) -> int:
    out.mkdir(parents=True, exist_ok=True)
    (out / "raw").mkdir(exist_ok=True)
    batches = out / "batches.csv"
    skip = done_ids(batches)
    cap = capacity_plan(cfg).set_index("key_design")
    prices = load_prices()
    thr_limit, streak_needed = cfg["abort"]["throttle_rate"], cfg["abort"]["consecutive_batches"]
    streak: dict = {}
    aborted: set = set()
    spent: dict = {}
    scaled = rate_scale != 1.0 or time_scale != 1.0
    n_done = 0
    for cell in cells:
        key = (cell["configuration"], cell["workload"])
        if cell["batch_id"] in skip or key in aborted:
            continue
        day = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
        if spent.get(day, 0.0) > cfg["abort"]["daily_budget_usd"]:
            log(f"daily budget reached ({day}) - stopping")
            return 3
        prof = scaled_profile(cell["workload"], rate_scale, time_scale) if scaled else None
        settle = cfg["settling_seconds"] * time_scale
        for _ in range(int(cfg["warmup_invocations"])):
            backend.invoke(lambda_events(cell, cfg, "warmup", lambdas))
        backend.invoke(lambda_events(cell, cfg, "settle", lambdas, profile=prof, settle_seconds=settle))
        resps = backend.invoke(lambda_events(cell, cfg, "measure", lambdas, profile=prof, extra=backend.extra()))
        frames = [read_raw(backend.fetch_raw(r["raw"])) for r in resps]
        merged = pd.concat([f.assign(lambda_id=i) for i, f in enumerate(frames)], ignore_index=True)
        merged.to_csv(out / "raw" / f"{cell['batch_id']}.csv.gz", index=False,
                      compression={"method": "gzip", "mtime": 0})
        m = batch_metrics(frames, max(r["wall_s"] for r in resps))
        prov = cap.loc[cell["key_design"]] if cell["capacity_mode"] == "provisioned" else None
        row = {**cell, **m, "t_start_epoch": min(r["t_start_epoch"] for r in resps),
               "t_end_epoch": max(r["t_end_epoch"] for r in resps),
               "cold_contaminated": any(r["cold_start"] for r in resps), "lambdas": lambdas,
               "rate_scale": rate_scale, "time_scale": time_scale, "data_source": backend.source,
               "prov_rcu_avg": float(prov.read_min) if prov is not None else float("nan"),
               "prov_wcu_avg": float(prov.write_min) if prov is not None else float("nan"),
               "prov_source": "config" if prov is not None else ""}
        append_row(batches, row)
        cost = on_demand_cost(m["rcu"], m["wcu"], prices) if prov is None else \
            provisioned_cost(row["prov_rcu_avg"], row["prov_wcu_avg"], m["wall_s"] + settle, prices)
        spent[day] = spent.get(day, 0.0) + cost
        streak[key] = streak.get(key, 0) + 1 if m["throttle_rate"] > thr_limit else 0
        if streak[key] >= streak_needed:
            aborted.add(key)
            log(f"ABORT {key}: {streak_needed} batches in a row above {thr_limit:.0%} throttled")
        n_done += 1
        log(f"{cell['batch_id']:34s} ok={m['succeeded']:6d} thr={m['throttled']:5d} "
            f"p99={m['latency_p99_ms']:.1f} ms  ${cost:.4f}")
    if aborted:
        (out / "aborted.json").write_text(json.dumps(sorted(map(list, aborted)), indent=2) + "\n")
    log(f"{n_done} batches written to {batches}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=str(ROOT / "config/experiment.yaml"))
    ap.add_argument("--out", default=str(ROOT / "results"))
    ap.add_argument("--backend", choices=["lambda", "local"], default="lambda")
    ap.add_argument("--moto", action="store_true", help="local backend against in-memory fake DynamoDB")
    ap.add_argument("--endpoint-url", help="local backend against DynamoDB Local")
    ap.add_argument("--function-name", default="ddbpk-driver")
    ap.add_argument("--results-bucket")
    ap.add_argument("--blocks", type=int)
    ap.add_argument("--workloads", help="comma list, default all four")
    ap.add_argument("--key-designs", help="comma list, default factors.key_design from config (K1-K3)")
    ap.add_argument("--rate-scale", type=float, default=1.0)
    ap.add_argument("--time-scale", type=float, default=1.0)
    ap.add_argument("--orders", type=int, help="override dataset size (pilot / smoke / key-cell)")
    ap.add_argument("--lambdas", type=int)
    ap.add_argument("--pilot", action="store_true", help="1 block at 25%% of the rate")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    with open(args.config, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    if args.orders:
        cfg["dataset"]["orders"] = args.orders
    if args.pilot:
        args.blocks, args.rate_scale = args.blocks or 1, 0.25
    key_designs = args.key_designs.split(",") if args.key_designs else None
    cells = schedule(cfg, args.blocks, args.workloads.split(",") if args.workloads else None,
                     key_designs=key_designs)
    lambdas = args.lambdas or cfg["driver"]["lambdas_per_batch"]
    est = estimate(cfg, cells, load_prices(), args.rate_scale, args.time_scale)
    print(f"{est['cells']} batches, {est['hours_of_load']} h of load, "
          f"estimated request-path cost ${est['request_path_usd']} (prices {load_prices()['publication_date'][:10]})")
    if args.dry_run:
        for c in cells[:30]:
            print(f"  {c['batch_id']}  table={c['table']}  seed={c['seed']}")
        return 0
    out = Path(args.out)
    if args.backend == "lambda":
        if not args.results_bucket:
            ap.error("--results-bucket is needed (terraform output results_bucket)")
        return run(cfg, cells, LambdaBackend(args.function_name, cfg["region"], args.results_bucket), out,
                   args.rate_scale, args.time_scale, lambdas)
    if args.moto:
        import os

        from moto import mock_aws

        for k, v in {"AWS_ACCESS_KEY_ID": "testing", "AWS_SECRET_ACCESS_KEY": "testing",
                     "AWS_DEFAULT_REGION": cfg["region"]}.items():
            os.environ.setdefault(k, v)
        with mock_aws():
            seed_moto(cfg, cfg["dataset"]["orders"])
            t0 = time.time()
            code = run(cfg, cells, LocalBackend(out / "raw_tmp", source="moto-smoke"), out,
                       args.rate_scale, args.time_scale, lambdas)
            print(f"smoke took {time.time() - t0:.0f} s")
            return code
    return run(cfg, cells, LocalBackend(out / "raw_tmp", args.endpoint_url), out, args.rate_scale,
               args.time_scale, lambdas)


if __name__ == "__main__":
    raise SystemExit(main())
