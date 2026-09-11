#!/usr/bin/env python
"""Pull CloudWatch table metrics for every batch window.

    python scripts/collect_metrics.py --results results/

Writes results/cloudwatch.csv (one row per batch) and fills prov_rcu_avg /
prov_wcu_avg in batches.csv with the capacity that was really provisioned
(auto-scaling may have moved it away from the configured minimum). The API
ConsumedCapacity numbers in batches.csv stay the primary consumption figures;
CloudWatch consumption is the cross-check.
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
from pathlib import Path

import pandas as pd

METRICS = [
    ("ConsumedReadCapacityUnits", "Sum"),
    ("ConsumedWriteCapacityUnits", "Sum"),
    ("ReadThrottleEvents", "Sum"),
    ("WriteThrottleEvents", "Sum"),
    ("ProvisionedReadCapacityUnits", "Average"),
    ("ProvisionedWriteCapacityUnits", "Average"),
]


def window(t_start: float, t_end: float) -> tuple[dt.datetime, dt.datetime]:
    """Whole minutes around the batch (CloudWatch table metrics have 1-minute resolution)."""
    s = dt.datetime.fromtimestamp(math.floor(t_start / 60) * 60, dt.timezone.utc)
    e = dt.datetime.fromtimestamp(math.ceil(t_end / 60) * 60 + 60, dt.timezone.utc)
    return s, e


def queries(table: str) -> list[dict]:
    return [{"Id": f"m{i}", "ReturnData": True,
             "MetricStat": {"Metric": {"Namespace": "AWS/DynamoDB", "MetricName": name,
                                       "Dimensions": [{"Name": "TableName", "Value": table}]},
                            "Period": 60, "Stat": stat}}
            for i, (name, stat) in enumerate(METRICS)]


def collect_one(cw, table: str, t_start: float, t_end: float) -> dict:
    s, e = window(t_start, t_end)
    resp = cw.get_metric_data(MetricDataQueries=queries(table), StartTime=s, EndTime=e)
    by_id = {r["Id"]: r["Values"] for r in resp["MetricDataResults"]}
    row = {}
    for i, (name, stat) in enumerate(METRICS):
        vals = by_id.get(f"m{i}", [])
        if stat == "Sum":
            row[f"cw_{name}"] = float(sum(vals))
        else:
            row[f"cw_{name}"] = float(sum(vals) / len(vals)) if vals else float("nan")
    return row


def collect(batches: pd.DataFrame, cw) -> pd.DataFrame:
    rows = []
    for b in batches.itertuples():
        rows.append({"batch_id": b.batch_id, "table": b.table, **collect_one(cw, b.table, b.t_start_epoch, b.t_end_epoch)})
    return pd.DataFrame(rows)


def merge_provisioned(batches: pd.DataFrame, cwdf: pd.DataFrame) -> pd.DataFrame:
    b = batches.merge(cwdf[["batch_id", "cw_ProvisionedReadCapacityUnits", "cw_ProvisionedWriteCapacityUnits"]],
                      on="batch_id", how="left")
    prov = (b["capacity_mode"] == "provisioned") & b["cw_ProvisionedReadCapacityUnits"].notna()
    b.loc[prov, "prov_rcu_avg"] = b.loc[prov, "cw_ProvisionedReadCapacityUnits"]
    b.loc[prov, "prov_wcu_avg"] = b.loc[prov, "cw_ProvisionedWriteCapacityUnits"]
    b.loc[prov, "prov_source"] = "cloudwatch"
    return b.drop(columns=["cw_ProvisionedReadCapacityUnits", "cw_ProvisionedWriteCapacityUnits"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default="results")
    ap.add_argument("--region", default="eu-west-1")
    args = ap.parse_args(argv)
    import boto3

    res = Path(args.results)
    batches = pd.read_csv(res / "batches.csv")
    cwdf = collect(batches, boto3.client("cloudwatch", region_name=args.region))
    cwdf.to_csv(res / "cloudwatch.csv", index=False)
    merge_provisioned(batches, cwdf).to_csv(res / "batches.csv", index=False)
    print(f"{len(cwdf)} batch windows -> {res / 'cloudwatch.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
