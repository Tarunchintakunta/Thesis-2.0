"""Metrics + cost proxy for one run, and raw evidence dumps.

Works on the ``RunResult`` from the simulator and on the equivalent structure
the live backend builds from DynamoDB / SQS / CloudWatch.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import yaml

from common.metrics import compute_run_metrics

# rough USD list prices, only used as a cost *proxy* (see configs/pricing.yaml)
DEFAULT_PRICING = {
    "lambda_per_gb_s": 0.0000166667,
    "lambda_per_million_requests": 0.20,
    "sqs_per_million_requests": 0.40,
    "dynamodb_per_million_writes": 1.25,
    "api_per_million_requests": 1.00,
}


def load_pricing(path: str | Path | None = None) -> dict[str, float]:
    if path and Path(path).exists():
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        return {**DEFAULT_PRICING, **{k: float(v) for k, v in data.get("prices", {}).items()}}
    return dict(DEFAULT_PRICING)


def metrics_from_result(spec, result) -> dict[str, Any]:
    metrics = compute_run_metrics(
        produced=result.produced,
        events=result.events,
        dlq_order_ids=result.dlq_order_ids,
        samples=result.samples,
        fault_window=result.fault_window,
        remaining_ids=result.remaining_ids,
        recovery_kwargs=spec.recovery,
    )
    # >1 means an order was really applied twice (only possible without idempotency)
    metrics["max_apply_count"] = result.max_apply_count
    return metrics


def estimate_cost(counters: dict[str, float], pricing: dict[str, float] | None = None) -> dict[str, Any]:
    p = pricing or DEFAULT_PRICING
    sqs_requests = (
        counters.get("sqs_send_batch_calls", 0)
        + counters.get("sqs_receive_calls", 0)
        + counters.get("delete_batch_calls", 0)
        + counters.get("sqs_moved_to_dlq", 0)
    )
    lambda_requests = counters.get("invocations", 0)
    gb_s = counters.get("lambda_gb_s", 0.0)
    ddb_writes = counters.get("dynamo_order_writes", 0) + counters.get("dynamo_event_writes", 0)
    api_requests = counters.get("api_requests", 0)
    usd = {
        "lambda_compute": gb_s * p["lambda_per_gb_s"],
        "lambda_requests": lambda_requests / 1e6 * p["lambda_per_million_requests"],
        "sqs": sqs_requests / 1e6 * p["sqs_per_million_requests"],
        "dynamodb": ddb_writes / 1e6 * p["dynamodb_per_million_writes"],
        "api": api_requests / 1e6 * p["api_per_million_requests"],
    }
    return {
        "sqs_requests": sqs_requests,
        "lambda_requests": lambda_requests,
        "lambda_gb_s": gb_s,
        "dynamodb_writes": ddb_writes,
        "api_requests": api_requests,
        "usd_breakdown": usd,
        "usd_total": sum(usd.values()),
    }


def write_raw(out_dir: str | Path, run_id: str, result) -> Path:
    """events.csv + samples.csv for one run (results/raw is gitignored)."""
    folder = Path(out_dir) / "raw" / run_id
    folder.mkdir(parents=True, exist_ok=True)
    fields = ["ts", "run_id", "arm", "message_id", "order_id", "receive_count", "outcome", "fault_mode"]
    with open(folder / "events.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(result.events)
    with open(folder / "samples.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["t", "visible", "inflight", "delayed"])
        writer.writeheader()
        writer.writerows(result.samples)
    with open(folder / "produced.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["order_id", "produced_at"])
        writer.writerows(sorted(result.produced.items(), key=lambda kv: kv[1]))
    return folder
