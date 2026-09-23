"""Per-batch dependent variables from the raw per-operation records of all its Lambdas.

Percentiles are computed on the merged raw records (not averaged from each
Lambda's own percentiles, which would be wrong).
"""
from __future__ import annotations

import gzip
import io

import numpy as np
import pandas as pd


def read_raw(data: bytes | str) -> pd.DataFrame:
    if isinstance(data, str):
        with open(data, "rb") as fh:
            data = fh.read()
    return pd.read_csv(io.BytesIO(gzip.decompress(data)), keep_default_na=False)


def batch_metrics(raws: list[pd.DataFrame], wall_s: float) -> dict:
    r = pd.concat(raws, ignore_index=True)
    ok = r["ok"] == 1
    lat = r.loc[ok, "latency_ms"].to_numpy(float)
    resp = r.loc[ok, "response_ms"].to_numpy(float)
    reads = r["op"] == "R"

    def pc(x, q):
        return float(np.percentile(x, q)) if len(x) else float("nan")

    return {
        "attempted": int(len(r)), "succeeded": int(ok.sum()), "throttled": int(r["throttled"].sum()),
        "errors": int((~ok & (r["throttled"] == 0)).sum()),
        "throttle_rate": float(r["throttled"].mean()) if len(r) else float("nan"),
        "reads": int(reads.sum()), "writes": int((~reads).sum()),
        "rcu": float(r.loc[reads, "units"].sum()), "wcu": float(r.loc[~reads, "units"].sum()),
        "latency_mean_ms": float(lat.mean()) if len(lat) else float("nan"),
        "latency_p50_ms": pc(lat, 50), "latency_p95_ms": pc(lat, 95), "latency_p99_ms": pc(lat, 99),
        "response_p99_ms": pc(resp, 99),
        "wall_s": float(wall_s), "throughput_ops_s": float(ok.sum() / wall_s) if wall_s > 0 else float("nan"),
        "hot_rank_share": float((r["rank"] < 0.10 * max(1, r["rank"].max() + 1)).mean()) if len(r) else float("nan"),
    }
