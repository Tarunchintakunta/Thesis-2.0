"""Mutation ground truth from the table's DynamoDB stream.

The stream records every INSERT / MODIFY / REMOVE of an item, independently of
what the function says it did. Each business write carries the delivery's
exec_id, so a repeated write always changes the item and always shows up as a
MODIFY record. Stream records are kept for 24 hours: collect right after a run.

    python -m driver.streams --out data/runs/live/campaign     # live
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import yaml


def read_stream(streams, stream_arn: str, max_empty: int = 10, pause: float = 0.2) -> list[dict]:
    """Every record in the stream.

    A closed shard is read to its end. An open shard has no end, and GetRecords
    can return an empty page before the last record, so an open shard is only
    left after `max_empty` empty pages in a row (with a pause, to stay under
    the per-shard read limit).
    """
    events = []
    shards = []
    kw = {"StreamArn": stream_arn}
    while True:
        desc = streams.describe_stream(**kw)["StreamDescription"]
        shards += desc["Shards"]
        if not desc.get("LastEvaluatedShardId"):
            break
        kw["ExclusiveStartShardId"] = desc["LastEvaluatedShardId"]
    for sh in shards:
        closed = "EndingSequenceNumber" in sh.get("SequenceNumberRange", {})
        it = streams.get_shard_iterator(StreamArn=stream_arn, ShardId=sh["ShardId"],
                                        ShardIteratorType="TRIM_HORIZON")["ShardIterator"]
        empty = 0
        while it:
            resp = streams.get_records(ShardIterator=it, Limit=1000)
            recs = resp.get("Records", [])
            if recs:
                empty = 0
            else:
                empty += 1
                if not closed and empty >= max_empty:
                    break
                time.sleep(pause)
            for r in recs:
                new, old = r["dynamodb"].get("NewImage") or {}, r["dynamodb"].get("OldImage") or {}
                pk = r["dynamodb"]["Keys"]["pk"]["S"]
                kind, _, rid = pk.partition("#")
                events.append({
                    "event": r["eventName"], "seq": r["dynamodb"].get("SequenceNumber"), "pk": pk,
                    "kind": "business" if kind == "REQ" else "idem_key", "request_id": rid,
                    "exec_id": _s(new, "exec_id"), "delivery": _n(new, "delivery"), "status": _s(new, "status"),
                    "old_exec_id": _s(old, "exec_id"), "old_delivery": _n(old, "delivery"),
                    "old_status": _s(old, "status"),
                })
            it = resp.get("NextShardIterator")
    events.sort(key=lambda e: (e["pk"], int(e["seq"] or 0)))
    return events


def _s(img: dict, k: str) -> str | None:
    return img[k]["S"] if k in img else None


def _n(img: dict, k: str) -> int | None:
    return int(img[k]["N"]) if k in img else None


def dump_stream(streams, stream_arn: str, path: str | Path, pause: float = 0.2) -> int:
    events = read_stream(streams, stream_arn, pause=pause)
    with open(path, "w", encoding="utf-8") as fh:
        for e in events:
            fh.write(json.dumps(e) + "\n")
    return len(events)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="run folder (writes stream.jsonl there)")
    args = ap.parse_args(argv)
    import boto3

    root = Path(__file__).resolve().parents[2]
    cfg = yaml.safe_load(open(root / "config/experiment.yaml"))
    region = yaml.safe_load(open(root / "config/versions.yaml"))["region"]
    arn = boto3.client("dynamodb", region_name=region).describe_table(TableName=cfg["table_name"])["Table"]["LatestStreamArn"]
    n = dump_stream(boto3.client("dynamodbstreams", region_name=region), arn, Path(args.out) / "stream.jsonl")
    print(f"{n} stream records -> {Path(args.out) / 'stream.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
