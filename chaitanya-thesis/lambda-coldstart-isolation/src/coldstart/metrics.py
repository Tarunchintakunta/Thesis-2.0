"""Join client-side invocation records with REPORT lines (on request id).

The REPORT line from CloudWatch Logs wins; the one from the invoke log tail is
the fallback. REPORT lines with no client record are warmer pings (warm-target)
or strays; they are kept (they cost money) but flagged so no analysis uses them
as samples.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .backends import FUNCTIONS
from .logs import function_of
from .report_parser import parse_report

REPORT_COLS = ["duration_ms", "billed_ms", "memory_mb", "max_memory_used_mb", "init_ms"]
COLUMNS = [
    "seq", "phase", "data_mode", "function", "runtime", "variant", "memory_mb", "role", "pattern",
    "warming", "intended_cold", "force_cold", "rep", "block", "burst_id", "idle_gap_min",
    "t_start", "t_start_utc", "request_id", "status", "function_error", "error", "rtt_ms",
    "duration_ms", "billed_ms", "init_ms", "cold", "max_memory_used_mb", "report_source",
]


def load_invocations(raw_root: str | Path) -> pd.DataFrame:
    rows = []
    for p in sorted(Path(raw_root).glob("*/invocations.jsonl")):
        with open(p, encoding="utf-8") as fh:
            rows += [json.loads(line) for line in fh if line.strip()]
    return pd.DataFrame(rows)


def reports_frame(events: list[dict], stack: str) -> pd.DataFrame:
    rows = []
    for e in events:
        rep = parse_report(e["message"])
        if rep is None:
            continue
        d = rep.to_dict()
        d["function"] = function_of(e["log_group"], stack)
        d["log_timestamp"] = e["timestamp"]
        rows.append(d)
    return pd.DataFrame(rows, columns=["request_id", *REPORT_COLS, "cold", "function", "log_timestamp"])


def build_metrics(inv: pd.DataFrame, reports: pd.DataFrame) -> pd.DataFrame:
    inv = inv.copy()
    reports = reports.drop_duplicates("request_id")
    # tail REPORT fields, used when CloudWatch had no line for the request
    tail = pd.DataFrame([r if isinstance(r, dict) else {} for r in inv.get("tail_report", [])], index=inv.index)
    logs = reports.set_index("request_id")
    matched = inv["request_id"].isin(logs.index)
    for col in REPORT_COLS:
        from_logs = inv["request_id"].map(logs[col]) if col in logs else np.nan
        from_tail = tail[col] if col in tail else np.nan
        inv[col] = pd.Series(np.where(matched, from_logs, from_tail), index=inv.index)
    has_tail = tail["duration_ms"].notna() if "duration_ms" in tail else pd.Series(False, index=inv.index)
    inv["report_source"] = np.where(matched, "logs", np.where(has_tail, "tail", "missing"))
    inv["init_ms"] = pd.to_numeric(inv["init_ms"], errors="coerce")
    inv["cold"] = inv["init_ms"].notna() & (inv["report_source"] != "missing")

    # REPORT lines nobody asked for: warmer pings and strays
    extra = reports[~reports["request_id"].isin(inv["request_id"])].copy()
    if len(extra):
        mode = inv["data_mode"].iloc[0] if len(inv) else "unknown"
        extra["role"] = np.where(extra["function"] == "warm-target", "warmer_ping", "unmatched")
        extra["data_mode"] = mode
        extra["phase"] = "background"
        extra["runtime"] = extra["function"].map(lambda f: FUNCTIONS.get(f, (None, None))[0])
        extra["variant"] = extra["function"].map(lambda f: FUNCTIONS.get(f, (None, None))[1])
        extra["t_start"] = extra["log_timestamp"] / 1000.0
        extra["report_source"] = "logs"
        extra["status"] = 200
        inv = pd.concat([inv, extra], ignore_index=True)

    inv["error"] = inv["function_error"].notna() | (pd.to_numeric(inv["status"], errors="coerce") != 200) \
        if "function_error" in inv else False
    for col in COLUMNS:
        if col not in inv:
            inv[col] = np.nan
    return inv[COLUMNS].sort_values(["t_start", "seq"], na_position="last").reset_index(drop=True)


def discarded_intended_colds(m: pd.DataFrame) -> pd.DataFrame:
    """Intended-cold measure calls that came back warm: counted and published, never analysed as cold."""
    x = m[(m["role"] == "measure") & (m["intended_cold"] == True) & (~m["error"])]  # noqa: E712
    return (x.assign(came_back_warm=~x["cold"])
             .groupby(["phase", "function", "memory_mb"], dropna=False)
             .agg(intended_cold=("cold", "size"), came_back_warm=("came_back_warm", "sum"))
             .reset_index())
