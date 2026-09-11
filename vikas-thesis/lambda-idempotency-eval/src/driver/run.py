"""Run one phase: write the schedule + ground truth, then deliver every request N times.

    python -m driver.run --phase pilot --out data/runs/live/pilot
    python -m driver.run --phase campaign --n 1000 --workers 16 --out data/runs/live/campaign
    python -m driver.run --backend local --moto --phase pilot --out /tmp/pilot     # functional check

Every delivery is a synchronous invoke (RequestResponse, LogType=Tail). Lambda
does not retry synchronous invokes, and the SDK's own retries are switched off
here too, so the only redeliveries are the scheduled ones. An injected timeout
comes back as FunctionError; the handler's structured record is still in the
log tail, so its consumed capacity is not lost.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from driver.schedule import build, deliveries, write_ground_truth, write_schedule  # noqa: E402

FIELDS = ["request_id", "phase", "path", "multiplicity", "delivery", "inject", "status", "outcome", "wcu", "rcu",
          "wcu_ccf_rule", "consumed_capacity", "ccf", "calls", "business_writes", "latency_ms", "ddb_ms", "rtt_ms",
          "cold_start", "exec_id", "function_error", "t_start"]


def last_record(log_text: str) -> dict | None:
    for line in reversed(log_text.splitlines()):
        start = line.find('{"type": "delivery"')
        if start >= 0:
            try:
                return json.loads(line[start:].strip())
            except json.JSONDecodeError:
                continue
    return None


class LambdaBackend:
    source = "live"

    def __init__(self, function_name: str, region: str):
        import boto3
        from botocore.config import Config

        self.fn = function_name
        # no SDK retries: a retried Invoke would be an unscheduled delivery
        self.lam = boto3.client("lambda", region_name=region,
                                config=Config(read_timeout=30, retries={"total_max_attempts": 1}))

    def invoke(self, event: dict) -> dict:
        t0 = time.perf_counter()
        resp = self.lam.invoke(FunctionName=self.fn, Payload=json.dumps(event).encode(), LogType="Tail")
        rtt = (time.perf_counter() - t0) * 1000
        body = json.loads(resp["Payload"].read() or b"null")
        tail = base64.b64decode(resp.get("LogResult") or b"").decode("utf-8", "replace")
        if resp.get("FunctionError"):
            msg = body.get("errorMessage", "") if isinstance(body, dict) else ""
            status = "timeout" if "timed out" in msg.lower() else "error"
            return {"status": status, "record": last_record(tail), "rtt_ms": rtt, "function_error": msg[:200]}
        return {"status": "ok", "record": body, "rtt_ms": rtt, "function_error": ""}


class LocalContext:
    """The two things the handler reads from a Lambda context.

    remaining_ms = -1 makes a P3 claim expire at once. On Lambda the redelivery
    only starts after the timed-out invocation has ended, i.e. after its claim
    expired; locally the redelivery comes a few ms later, so without this the
    local run would refuse it (REJECTED_IN_PROGRESS) where Lambda would not.
    """

    def __init__(self, remaining_ms: int = -1):
        self.aws_request_id = f"local-{uuid.uuid4()}"
        self.remaining_ms = remaining_ms

    def get_remaining_time_in_millis(self) -> int:
        return self.remaining_ms


class LocalBackend:
    """The handler in this process (moto or DynamoDB Local); InjectedTimeout stands in for the timeout."""

    def __init__(self, source: str = "local", remaining_ms: int = -1):
        os.environ["INJECT_MODE"] = "raise"
        from lambda_fn import handler

        self.h = handler
        self.source = source
        self.remaining_ms = remaining_ms

    def invoke(self, event: dict) -> dict:
        t0 = time.perf_counter()
        try:
            rec = self.h.lambda_handler(event, LocalContext(self.remaining_ms))
            return {"status": "ok", "record": rec, "rtt_ms": (time.perf_counter() - t0) * 1000, "function_error": ""}
        except self.h.InjectedTimeout as exc:
            return {"status": "timeout", "record": json.loads(str(exc)), "rtt_ms": (time.perf_counter() - t0) * 1000,
                    "function_error": "injected timeout"}


def warm_up(backend, workers: int, rounds: int) -> dict:
    """Warm-up policy: `rounds` waves of `workers` concurrent no-op calls before a phase (not analysed)."""
    calls = cold = 0
    for _ in range(rounds):
        with ThreadPoolExecutor(max_workers=workers) as pool:
            res = list(pool.map(lambda _: backend.invoke({"warmup": True}), range(workers)))
        calls += len(res)
        cold += sum(bool((r["record"] or {}).get("cold_start")) for r in res)
    return {"calls": calls, "cold": cold}


def run_phase(reqs: list[dict], backend, out: Path, max_invocations: int, workers: int = 1, warmup_rounds: int = 0,
              log=print, meta: dict | None = None) -> dict:
    out = Path(out)
    if (out / "deliveries.jsonl").exists():
        raise FileExistsError(f"{out} already has deliveries - use a new --out")
    planned = sum(r["multiplicity"] for r in reqs) + workers * warmup_rounds
    if planned > max_invocations:
        raise RuntimeError(f"{planned} invocations planned, budget allows {max_invocations}")
    write_schedule(reqs, out / "schedule.csv")  # both written before the first invoke
    write_ground_truth(reqs, out / "ground_truth.jsonl")
    warm = warm_up(backend, workers, warmup_rounds)
    lock = threading.Lock()
    fh = open(out / "deliveries.jsonl", "a", encoding="utf-8")
    t_start = time.time()
    done = [0]

    def one_request(req: dict) -> None:
        for d in deliveries(req):
            ev = {"request_id": req["request_id"], "path": req["path"], "delivery": d["delivery"],
                  "inject": d["inject"], "payload": req["payload"]}
            t = time.time()
            res = backend.invoke(ev)
            rec = res["record"] or {}
            row = {**rec, "request_id": req["request_id"], "phase": req["phase"], "path": req["path"],
                   "multiplicity": req["multiplicity"], "delivery": d["delivery"], "inject": d["inject"],
                   "status": res["status"], "rtt_ms": round(res["rtt_ms"], 3), "function_error": res["function_error"],
                   "t_start": round(t, 3)}
            with lock:
                fh.write(json.dumps({k: row.get(k) for k in FIELDS}) + "\n")
                done[0] += 1

    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            list(pool.map(one_request, reqs))
    finally:
        fh.close()
    info = {"phase": reqs[0]["phase"] if reqs else None, "backend": backend.source, "requests": len(reqs),
            "invocations": done[0], "workers": workers, "warmup": warm, "t_start": t_start, "t_end": time.time(),
            "t_start_utc": dt.datetime.fromtimestamp(t_start, dt.timezone.utc).isoformat(timespec="seconds"),
            "versions": yaml.safe_load(open(ROOT / "config/versions.yaml")), **(meta or {})}
    (out / "run_info.json").write_text(json.dumps(info, indent=2) + "\n")
    log(f"{info['requests']} requests, {info['invocations']} invocations (+{warm['calls']} warm-up) -> {out}")
    return info


def create_local_table(client, name: str) -> str:
    client.create_table(TableName=name, KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
                        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
                        BillingMode="PAY_PER_REQUEST",
                        StreamSpecification={"StreamEnabled": True, "StreamViewType": "NEW_AND_OLD_IMAGES"})
    return client.describe_table(TableName=name)["Table"]["LatestStreamArn"]


def ids_already_used(ddb, table: str, reqs: list[dict], k: int = 5) -> bool:
    """True if the first requests' business items exist already.

    Re-running a phase with the same seed against the same table would reuse
    the request ids: P2/P3 would then suppress even the first delivery, and the
    stream would mix both runs. So a repeated phase needs a new --seed.
    """
    for r in reqs[:k]:
        if ddb.get_item(TableName=table, Key={"pk": {"S": f"REQ#{r['request_id']}"}}).get("Item"):
            return True
    return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase", choices=["pilot", "campaign", "sensitivity"], required=True)
    ap.add_argument("--n", type=int, help="requests per cell (default: config)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--backend", choices=["lambda", "local"], default="lambda")
    ap.add_argument("--moto", action="store_true", help="local backend against in-memory DynamoDB (moto)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--seed", type=int, help="request-id seed (default: config); a repeated phase needs a new one")
    ap.add_argument("--config", default=str(ROOT / "config/experiment.yaml"))
    args = ap.parse_args(argv)
    cfg = yaml.safe_load(open(args.config))
    seed = args.seed if args.seed is not None else cfg["campaign"]["seed"]
    reqs = build(cfg, args.phase, args.n, seed)
    out, cap, rounds = Path(args.out), cfg["budget"]["max_invocations"], cfg.get("warmup_rounds", 0)
    meta = {"seed": seed}
    if args.backend == "lambda":
        import boto3

        region = yaml.safe_load(open(ROOT / "config/versions.yaml"))["region"]
        if ids_already_used(boto3.client("dynamodb", region_name=region), cfg["table_name"], reqs):
            print("these request ids are already in the table (phase run before?) - pass a new --seed", file=sys.stderr)
            return 2
        run_phase(reqs, LambdaBackend(cfg["function_name"], region), out, cap, args.workers, rounds, meta=meta)
        print("next: python -m driver.streams --out", out, "(stream records expire after 24 h)")
        return 0
    if not args.moto:
        run_phase(reqs, LocalBackend(), out, cap, args.workers, rounds, meta=meta)
        return 0
    import boto3
    from moto import mock_aws

    from driver.streams import dump_stream

    for k, v in {"AWS_ACCESS_KEY_ID": "testing", "AWS_SECRET_ACCESS_KEY": "testing",
                 "AWS_DEFAULT_REGION": "eu-west-1", "TABLE_NAME": cfg["table_name"]}.items():
        os.environ[k] = v
    with mock_aws():
        arn = create_local_table(boto3.client("dynamodb", region_name="eu-west-1"), cfg["table_name"])
        run_phase(reqs, LocalBackend("moto"), out, cap, args.workers, rounds, meta=meta)
        n = dump_stream(boto3.client("dynamodbstreams", region_name="eu-west-1"), arn, out / "stream.jsonl", pause=0)
    print(f"{n} stream records -> {out / 'stream.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
