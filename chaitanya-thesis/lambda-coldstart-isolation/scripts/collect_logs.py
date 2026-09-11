#!/usr/bin/env python
"""Collect REPORT lines for every phase under a raw folder.

    DATA_MODE=mock python scripts/collect_logs.py --runs data/raw/mock/
    DATA_MODE=live python scripts/collect_logs.py --runs data/raw/live/
    DATA_MODE=live python scripts/collect_logs.py --start 2026-03-01T10:00:00Z --end 2026-03-01T12:00:00Z --out data/raw/logs/

Writes <out>/events.jsonl (default out: <runs>/logs_collected/). Live mode reads
each phase's window from its run_info.json and queries CloudWatch Logs for all
eight function log groups; mock mode merges the synthetic events the mock wrote.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coldstart.backends import FUNCTIONS, data_mode  # noqa: E402
from coldstart.config import load_config  # noqa: E402
from coldstart.logs import collect_live, collect_mock, log_group, pull_reports, write_events  # noqa: E402


def _ms(iso: str) -> int:
    return int(dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp() * 1000)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", help="raw folder with one sub-folder per phase")
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--out")
    ap.add_argument("--config", default="configs/experiment.yaml")
    args = ap.parse_args(argv)
    if not args.runs and not (args.start and args.end and args.out):
        ap.error("give --runs, or --start/--end/--out")
    cfg = load_config(args.config)
    mode = data_mode()
    out = Path(args.out) if args.out else Path(args.runs) / "logs_collected"

    if mode == "mock":
        if not args.runs:
            ap.error("mock mode needs --runs (the mock writes its own logs)")
        events = collect_mock(args.runs)
    else:
        import boto3

        logs = boto3.client("logs", region_name=cfg["region"])
        if args.runs:
            events = collect_live(args.runs, logs, cfg["stack_name"])
        else:
            events = []
            for fn in FUNCTIONS:
                try:
                    events += pull_reports(logs, log_group(cfg["stack_name"], fn), _ms(args.start), _ms(args.end))
                except logs.exceptions.ResourceNotFoundException:
                    continue
    path = write_events(events, out / "events.jsonl")
    n_report = sum(e["message"].startswith("REPORT") for e in events)
    print(f"DATA_MODE={mode}: {len(events)} events ({n_report} REPORT) -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
