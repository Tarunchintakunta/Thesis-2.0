#!/usr/bin/env python3
"""Focused LIVE lite round for S3 / Cost Explorer / CloudWatch / Wilcoxon.

Produces measured evidence under results/live/. No invented metrics.
Tags use project slug only (no personal name/ID).
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "live"
REGION = "eu-west-1"
N_OBJECTS = 24
# 160 KiB >= STANDARD_IA min billable object size (128 KiB)
OBJECT_BYTES = 160 * 1024
RATE_STANDARD_GB_MO = 0.023  # eu-west-1-ish list price; also recorded from Pricing when available
RATE_IA_GB_MO = 0.0125


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.isoformat()


def monthly_storage_usd(size_bytes: int, rate_gb_mo: float, min_billable_bytes: int = 0) -> float:
    billable = max(size_bytes, min_billable_bytes)
    return (billable / (1024**3)) * rate_gb_mo


def wilcoxon_paired(a: list[float], b: list[float], alpha: float = 0.05) -> dict:
    if len(a) != len(b):
        raise ValueError("paired samples must match length")
    if len(a) < 5:
        return {
            "test": "wilcoxon",
            "statistic": None,
            "p_value": None,
            "significant": False,
            "n": len(a),
            "note": "Sample size too small (n < 5)",
        }
    # zero differences break wilcoxon; scipy handles with prune
    try:
        statistic, p_value = stats.wilcoxon(a, b, alternative="two-sided")
        return {
            "test": "wilcoxon",
            "statistic": float(statistic),
            "p_value": float(p_value),
            "alpha": alpha,
            "significant": bool(p_value < alpha),
            "n": len(a),
        }
    except ValueError as exc:
        return {
            "test": "wilcoxon",
            "statistic": None,
            "p_value": None,
            "significant": False,
            "n": len(a),
            "error": str(exc),
        }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    started = utc_now()

    s3 = boto3.client("s3", region_name=REGION)
    ce = boto3.client("ce", region_name="us-east-1")  # CE is global, endpoint us-east-1
    cw = boto3.client("cloudwatch", region_name=REGION)
    logs = boto3.client("logs", region_name=REGION)
    pricing = boto3.client("pricing", region_name="us-east-1")

    # Resolve bucket from terraform output file if present, else prefix scan
    bucket = None
    state_path = ROOT / "terraform" / "terraform.tfstate"
    if state_path.exists():
        state = json.loads(state_path.read_text())
        bucket = (state.get("outputs") or {}).get("bucket_name", {}).get("value")
        log_group = (state.get("outputs") or {}).get("log_group", {}).get("value")
    else:
        log_group = "/research/s3-pred-opt"

    if not bucket:
        buckets = s3.list_buckets().get("Buckets", [])
        matches = [b["Name"] for b in buckets if b["Name"].startswith("s3-pred-opt-")]
        if not matches:
            print("ERROR: no s3-pred-opt-* bucket found", file=sys.stderr)
            return 1
        bucket = sorted(matches)[-1]

    log_group = log_group or "/research/s3-pred-opt"

    payload = b"x" * OBJECT_BYTES
    put_std_ms: list[float] = []
    put_ia_ms: list[float] = []
    get_std_ms: list[float] = []
    get_ia_ms: list[float] = []
    objects: list[dict] = []

    prefix = f"lite/{started.strftime('%Y%m%dT%H%M%SZ')}/"

    for i in range(N_OBJECTS):
        key_std = f"{prefix}std/obj-{i:03d}.bin"
        key_ia = f"{prefix}ia/obj-{i:03d}.bin"

        t0 = time.perf_counter()
        s3.put_object(
            Bucket=bucket,
            Key=key_std,
            Body=payload,
            StorageClass="STANDARD",
            ContentType="application/octet-stream",
            Metadata={"round": "lite", "arm": "standard"},
        )
        put_std_ms.append((time.perf_counter() - t0) * 1000.0)

        t0 = time.perf_counter()
        s3.put_object(
            Bucket=bucket,
            Key=key_ia,
            Body=payload,
            StorageClass="STANDARD_IA",
            ContentType="application/octet-stream",
            Metadata={"round": "lite", "arm": "standard_ia"},
        )
        put_ia_ms.append((time.perf_counter() - t0) * 1000.0)

        t0 = time.perf_counter()
        s3.get_object(Bucket=bucket, Key=key_std)
        get_std_ms.append((time.perf_counter() - t0) * 1000.0)

        t0 = time.perf_counter()
        s3.get_object(Bucket=bucket, Key=key_ia)
        get_ia_ms.append((time.perf_counter() - t0) * 1000.0)

        head_std = s3.head_object(Bucket=bucket, Key=key_std)
        head_ia = s3.head_object(Bucket=bucket, Key=key_ia)
        objects.append(
            {
                "key_standard": key_std,
                "key_ia": key_ia,
                "size_bytes": OBJECT_BYTES,
                "storage_class_standard": head_std.get("StorageClass", "STANDARD"),
                "storage_class_ia": head_ia.get("StorageClass"),
            }
        )

    # Listing evidence
    listed = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    listed_count = listed.get("KeyCount", 0)

    # Pricing API probe (optional; record success/failure honestly)
    pricing_probe: dict = {"ok": False}
    try:
        resp = pricing.get_products(
            ServiceCode="AmazonS3",
            Filters=[
                {"Type": "TERM_MATCH", "Field": "location", "Value": "EU (Ireland)"},
                {"Type": "TERM_MATCH", "Field": "volumeType", "Value": "Amazon S3 Standard Storage"},
            ],
            MaxResults=1,
        )
        pricing_probe = {
            "ok": True,
            "price_list_count": len(resp.get("PriceList", [])),
            "format_version": resp.get("FormatVersion"),
        }
    except ClientError as exc:
        pricing_probe = {"ok": False, "error": str(exc)}

    # Cost Explorer — last 7 complete days ending yesterday (CE needs closed days)
    end = utc_now().date()
    start = end - timedelta(days=7)
    ce_s3: dict = {"ok": False}
    try:
        ce_resp = ce.get_cost_and_usage(
            TimePeriod={"Start": start.isoformat(), "End": end.isoformat()},
            Granularity="DAILY",
            Metrics=["UnblendedCost"],
            Filter={
                "Dimensions": {
                    "Key": "SERVICE",
                    "Values": ["Amazon Simple Storage Service"],
                }
            },
        )
        daily = []
        total = 0.0
        for row in ce_resp.get("ResultsByTime", []):
            amt = float(row["Total"]["UnblendedCost"]["Amount"])
            total += amt
            daily.append({"start": row["TimePeriod"]["Start"], "unblended_usd": amt})
        ce_s3 = {
            "ok": True,
            "window": {"start": start.isoformat(), "end": end.isoformat()},
            "daily": daily,
            "sum_unblended_usd": total,
        }
    except ClientError as exc:
        ce_s3 = {"ok": False, "error": str(exc)}

    # CloudWatch metrics for this bucket (BucketSizeBytes lags ~1 day; record whatever returns)
    cw_metrics: dict = {"ok": False}
    try:
        listed_metrics = cw.list_metrics(
            Namespace="AWS/S3",
            Dimensions=[{"Name": "BucketName", "Value": bucket}],
        )
        end_cw = utc_now()
        start_cw = end_cw - timedelta(days=2)
        size_stats = cw.get_metric_statistics(
            Namespace="AWS/S3",
            MetricName="BucketSizeBytes",
            Dimensions=[
                {"Name": "BucketName", "Value": bucket},
                {"Name": "StorageType", "Value": "StandardStorage"},
            ],
            StartTime=start_cw,
            EndTime=end_cw,
            Period=86400,
            Statistics=["Average"],
            Unit="Bytes",
        )
        cw_metrics = {
            "ok": True,
            "list_metrics_count": len(listed_metrics.get("Metrics", [])),
            "bucket_size_datapoints": [
                {"timestamp": iso(dp["Timestamp"]), "average_bytes": dp["Average"]}
                for dp in size_stats.get("Datapoints", [])
            ],
            "note": "BucketSizeBytes often empty for brand-new buckets (daily lag).",
        }
    except ClientError as exc:
        cw_metrics = {"ok": False, "error": str(exc)}

    # CloudWatch Logs write probe
    cw_logs: dict = {"ok": False}
    stream = f"lite-{started.strftime('%Y%m%dT%H%M%SZ')}"
    try:
        try:
            logs.create_log_stream(logGroupName=log_group, logStreamName=stream)
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") != "ResourceAlreadyExistsException":
                raise
        msg = json.dumps(
            {
                "event": "live_lite_round",
                "bucket": bucket,
                "objects": N_OBJECTS * 2,
                "project": "s3-predictive-optimization",
            }
        )
        put = logs.put_log_events(
            logGroupName=log_group,
            logStreamName=stream,
            logEvents=[{"timestamp": int(utc_now().timestamp() * 1000), "message": msg}],
        )
        cw_logs = {
            "ok": True,
            "log_group": log_group,
            "log_stream": stream,
            "rejected_events": put.get("rejectedLogEventsInfo"),
        }
    except ClientError as exc:
        cw_logs = {"ok": False, "error": str(exc)}

    # Cost model from live object sizes (STANDARD vs IA min-billable)
    cost_std = [
        monthly_storage_usd(OBJECT_BYTES, RATE_STANDARD_GB_MO) for _ in range(N_OBJECTS)
    ]
    cost_ia = [
        monthly_storage_usd(OBJECT_BYTES, RATE_IA_GB_MO, min_billable_bytes=128 * 1024)
        for _ in range(N_OBJECTS)
    ]
    wilcoxon_cost = wilcoxon_paired(cost_std, cost_ia)
    wilcoxon_get = wilcoxon_paired(get_std_ms, get_ia_ms)
    wilcoxon_put = wilcoxon_paired(put_std_ms, put_ia_ms)

    finished = utc_now()
    summary = {
        "round": "live_lite",
        "mode": "live_aws",
        "collected_at": iso(finished),
        "started_at": iso(started),
        "elapsed_s": (finished - started).total_seconds(),
        "region": REGION,
        "bucket": bucket,
        "log_group": log_group,
        "tags_policy": {
            "project": "s3-predictive-optimization",
            "managed_by": "terraform",
            "purpose": "research-eval",
            "data": "synthetic",
            "note": "No personal name/ID tags applied by this round.",
        },
        "s3": {
            "prefix": prefix,
            "objects_per_arm": N_OBJECTS,
            "object_bytes": OBJECT_BYTES,
            "listed_key_count": listed_count,
            "put_standard_ms": {
                "n": len(put_std_ms),
                "mean": statistics.fmean(put_std_ms),
                "stdev": statistics.stdev(put_std_ms) if len(put_std_ms) > 1 else 0.0,
                "min": min(put_std_ms),
                "max": max(put_std_ms),
            },
            "put_standard_ia_ms": {
                "n": len(put_ia_ms),
                "mean": statistics.fmean(put_ia_ms),
                "stdev": statistics.stdev(put_ia_ms) if len(put_ia_ms) > 1 else 0.0,
                "min": min(put_ia_ms),
                "max": max(put_ia_ms),
            },
            "get_standard_ms": {
                "n": len(get_std_ms),
                "mean": statistics.fmean(get_std_ms),
                "stdev": statistics.stdev(get_std_ms) if len(get_std_ms) > 1 else 0.0,
                "min": min(get_std_ms),
                "max": max(get_std_ms),
            },
            "get_standard_ia_ms": {
                "n": len(get_ia_ms),
                "mean": statistics.fmean(get_ia_ms),
                "stdev": statistics.stdev(get_ia_ms) if len(get_ia_ms) > 1 else 0.0,
                "min": min(get_ia_ms),
                "max": max(get_ia_ms),
            },
            "sample_objects": objects[:3],
        },
        "pricing_api": pricing_probe,
        "cost_explorer": ce_s3,
        "cloudwatch_metrics": cw_metrics,
        "cloudwatch_logs": cw_logs,
        "storage_cost_model_usd_per_month": {
            "rate_standard_gb_mo": RATE_STANDARD_GB_MO,
            "rate_ia_gb_mo": RATE_IA_GB_MO,
            "sum_standard": sum(cost_std),
            "sum_ia": sum(cost_ia),
            "delta_standard_minus_ia": sum(cost_std) - sum(cost_ia),
            "note": (
                "Modeled from live object sizes × published list rates; "
                "not a settled Cost Explorer bill for this round."
            ),
        },
        "wilcoxon": {
            "storage_cost_standard_vs_ia": wilcoxon_cost,
            "get_latency_ms_standard_vs_ia": wilcoxon_get,
            "put_latency_ms_standard_vs_ia": wilcoxon_put,
            "note": (
                "Cost Wilcoxon uses paired per-object modeled monthly storage; "
                "latency Wilcoxon uses live PUT/GET wall times. "
                "Not a multi-workload savings campaign."
            ),
        },
        "limitations": [
            "Lite probe only: 24 objects × 2 storage classes; not multi-workload CA2 protocol.",
            "Cost Explorer window reflects account S3 spend (often near-zero / lagged), not round savings.",
            "CloudWatch BucketSizeBytes typically lags ~24h for new buckets.",
            "src/metadata/ collector still absent; no S3 Inventory job in this round.",
        ],
        "destroy_after": True,
    }

    raw = {
        "put_standard_ms": put_std_ms,
        "put_standard_ia_ms": put_ia_ms,
        "get_standard_ms": get_std_ms,
        "get_standard_ia_ms": get_ia_ms,
        "cost_standard_usd_mo": cost_std,
        "cost_ia_usd_mo": cost_ia,
        "objects": objects,
    }

    summary_path = OUT_DIR / "live_lite_summary.json"
    raw_path = OUT_DIR / "live_lite_raw.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    raw_path.write_text(json.dumps(raw, indent=2) + "\n")
    print(json.dumps({"summary": str(summary_path), "bucket": bucket, "listed": listed_count}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
