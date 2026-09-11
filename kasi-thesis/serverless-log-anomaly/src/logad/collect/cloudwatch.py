"""Live mode: pull the function's logs from CloudWatch Logs (LocalStack or AWS).

    python -m logad.collect.cloudwatch --group /aws/lambda/kasireddy-orders \
        --start 2026-06-01T00:00:00Z --end 2026-06-02T00:00:00Z --out data/raw/live/phase_A.log

Set AWS_ENDPOINT_URL=http://localhost:4566 for LocalStack. The output file has
the same "<ISO time>\\t<message>" format the emulator writes, so everything
after collection is identical in both modes.

Not executed in this repository (Docker/LocalStack were not available while
building it); unit tested against moto.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
from pathlib import Path

from logad.collect.runtime import iso


def _to_ms(value: str) -> int:
    return int(dt.datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)


def fetch_events(logs_client, group: str, start_ms: int, end_ms: int) -> list[tuple[float, str]]:
    events: list[tuple[float, str]] = []
    paginator = logs_client.get_paginator("filter_log_events")
    for page in paginator.paginate(logGroupName=group, startTime=start_ms, endTime=end_ms):
        for ev in page.get("events", []):
            for part in ev["message"].rstrip("\n").split("\n"):
                events.append((ev["timestamp"] / 1000.0, part))
    events.sort(key=lambda e: e[0])
    return events


def write_log(events: list[tuple[float, str]], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for ts, message in events:
            fh.write(f"{iso(ts)}\t{message}\n")
    return path


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--group", default="/aws/lambda/kasireddy-orders")
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)
    import boto3

    client = boto3.client("logs", endpoint_url=os.environ.get("AWS_ENDPOINT_URL") or None)
    events = fetch_events(client, args.group, _to_ms(args.start), _to_ms(args.end))
    write_log(events, args.out)
    print(f"{len(events)} log lines -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
