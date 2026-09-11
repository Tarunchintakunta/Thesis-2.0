"""Load run manifests into one flat pandas DataFrame.

The manifests (``results/**/manifests/*.json``) are the only source of truth
for the analysis. Nothing here reads a hand-edited CSV.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import src  # noqa: E402,F401  (puts src/ on sys.path)
from control.manifest import read_manifests  # noqa: E402

NUMERIC = [
    "loss_rate", "true_loss_rate", "stranded_rate", "duplicate_rate", "dlq_capture_rate",
    "success_rate", "recovery_time_s", "recovery_time_visible_s", "recovery_censored_at_s",
    "throughput_msg_s", "latency_p50_s", "latency_p95_s", "latency_mean_s", "usd_total",
    "visibility_timeout", "max_receive_count", "batch_size", "delivery_delay",
]


def load_runs(path: str | Path) -> pd.DataFrame:
    rows = []
    for m in read_manifests(path):
        row = {
            "run_id": m["run_id"],
            "campaign": m["campaign"],
            "repeat": m["repeat"],
            "backend": m["backend"],
            "config_hash": m["config_hash"],
            "seed": m["seed"],
            "order_position": m.get("order_position"),
            "fault_rate": m["fault_schedule"]["rate"],
            "usd_total": m["cost"]["usd_total"],
            "git_sha": m.get("git", {}).get("sha"),
        }
        row.update(m["cell"])
        row.update(m["metrics"])
        rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    for col in NUMERIC:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def recovery_lower_bound(df: pd.DataFrame, col: str = "recovery_time_s") -> pd.Series:
    """Recovery time where runs that never recovered get the time they were
    watched for (a lower bound). Only use this with rank based tests."""
    out = df[col].copy()
    if "recovery_censored_at_s" in df:
        missing = out.isna() & df["recovery_censored_at_s"].notna()
        out[missing] = df.loc[missing, "recovery_censored_at_s"]
    return out


def floor_duplicate_rate(df: pd.DataFrame) -> float:
    """At-least-once duplicate floor = mean duplicate rate of no-fault queue runs."""
    base = df[(df["fault_mode"] == "none") & (df["arm"] == "queue")]
    if base.empty:
        return float("nan")
    return float(np.nanmean(base["duplicate_rate"]))


if __name__ == "__main__":
    frame = load_runs(sys.argv[1] if len(sys.argv) > 1 else ROOT / "results")
    print(frame.groupby("campaign").size() if not frame.empty else "no manifests found")
