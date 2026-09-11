"""CloudWatch Logs side of the pipeline.

Live: pull the REPORT lines of every function's log group for the time window of
each phase (filter_log_events, paginated). Mock: the driver already wrote
<phase>/logs/events.jsonl in the same format, so they are only merged.

Event format, one JSON object per line: {"log_group", "timestamp" (ms), "message"}
"""
from __future__ import annotations

import json
from pathlib import Path

from .backends import FUNCTIONS

MARGIN_MS = 5 * 60 * 1000  # log timestamps can trail the client clock a little


def log_group(stack: str, fn: str) -> str:
    return f"/aws/lambda/{stack}-{fn}"


def function_of(group: str, stack: str) -> str | None:
    prefix = f"/aws/lambda/{stack}-"
    if group.startswith(prefix) and group[len(prefix):] in FUNCTIONS:
        return group[len(prefix):]
    return None


def pull_reports(logs_client, group: str, start_ms: int, end_ms: int) -> list[dict]:
    out = []
    pages = logs_client.get_paginator("filter_log_events").paginate(
        logGroupName=group, startTime=int(start_ms), endTime=int(end_ms), filterPattern='"REPORT RequestId"')
    for page in pages:
        for e in page.get("events", []):
            out.append({"log_group": group, "timestamp": e["timestamp"], "message": e["message"].rstrip("\n")})
    return out


def phase_windows(raw_root: str | Path) -> list[dict]:
    """run_info.json of every phase under a raw folder."""
    infos = []
    for p in sorted(Path(raw_root).glob("*/run_info.json")):
        infos.append(json.loads(p.read_text()))
    return infos


def write_events(events: list[dict], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for e in sorted(events, key=lambda e: (e["timestamp"], e["log_group"], e["message"])):
            fh.write(json.dumps(e) + "\n")
    return path


def read_events(paths) -> list[dict]:
    out = []
    for p in paths:
        with open(p, encoding="utf-8") as fh:
            out += [json.loads(line) for line in fh if line.strip()]
    return out


def collect_mock(raw_root: str | Path) -> list[dict]:
    return read_events(sorted(Path(raw_root).glob("*/logs/events.jsonl")))


def collect_live(raw_root: str | Path, logs_client, stack: str) -> list[dict]:
    events = []
    for info in phase_windows(raw_root):
        start = int(info["t_start"] * 1000) - MARGIN_MS
        end = int(info["t_end"] * 1000) + MARGIN_MS
        for fn in FUNCTIONS:
            try:
                events += pull_reports(logs_client, log_group(stack, fn), start, end)
            except logs_client.exceptions.ResourceNotFoundException:
                continue  # function never invoked, no log group yet
    # phases can overlap in time with the margin, drop duplicates
    seen, unique = set(), []
    for e in events:
        key = (e["log_group"], e["timestamp"], e["message"])
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique
