"""D3 - CloudWatch-style threshold alarms (the operational reference line).

Built on per-window *metrics* (what CloudWatch Lambda / API Gateway metrics
give an operator), not on log templates:

    lambda_errors    Lambda Errors      (timeouts + crashed invocations)
    api_5xx          API Gateway 5XXError
    duration_p99_ms  Lambda Duration p99
    throttles        Lambda Throttles

Thresholds = max(calibration quantile over the clean training windows, floor).
A window is flagged when any alarm is above its threshold.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

METRICS = ["invocations", "lambda_errors", "api_5xx", "duration_p99_ms", "throttles"]


def metric_windows(requests: pd.DataFrame, t0: float, t1: float, window_s: float) -> pd.DataFrame:
    n = int(math.ceil((t1 - t0) / window_s))
    out = pd.DataFrame(0.0, index=range(n), columns=METRICS)
    if requests.empty:
        return out
    df = requests.copy()
    df["w"] = np.clip(((df["t"] - t0) // window_s).astype(int), 0, n - 1)
    for col in ("throttled", "error", "timeout", "killed"):
        df[col] = df[col].astype(str).str.lower().isin(["true", "1"])
    ran = df[~df["throttled"]]
    g_all = df.groupby("w")
    g_ran = ran.groupby("w")
    out["invocations"] = g_ran.size()
    out["lambda_errors"] = g_ran["error"].sum()
    out["api_5xx"] = g_all["status"].apply(lambda s: int((pd.to_numeric(s) >= 500).sum()))
    out["duration_p99_ms"] = g_ran["duration_ms"].quantile(0.99)
    out["throttles"] = g_all["throttled"].sum()
    return out.fillna(0.0).astype(float)


class ThresholdAlarms:
    name = "d3_thresholds"

    def __init__(self, alarms: list[dict], calibration_quantile: float = 0.99) -> None:
        self.alarms = alarms
        self.q = calibration_quantile
        self.thresholds: dict[str, float] = {}

    def fit(self, train: pd.DataFrame) -> "ThresholdAlarms":
        for alarm in self.alarms:
            values = train[alarm["metric"]].to_numpy(dtype=float)
            self.thresholds[alarm["name"]] = max(float(np.quantile(values, self.q)), float(alarm.get("floor", 0)))
        return self

    def states(self, windows: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({a["name"]: windows[a["metric"]].to_numpy(dtype=float) > self.thresholds[a["name"]]
                             for a in self.alarms})

    def predict(self, windows: pd.DataFrame) -> np.ndarray:
        return self.states(windows).any(axis=1).to_numpy()

    def score(self, windows: pd.DataFrame) -> np.ndarray:
        """How far over its threshold the worst alarm is (only used for ranking plots)."""
        ratios = [windows[a["metric"]].to_numpy(dtype=float) / max(self.thresholds[a["name"]], 1e-9)
                  for a in self.alarms]
        return np.max(np.vstack(ratios), axis=0)
