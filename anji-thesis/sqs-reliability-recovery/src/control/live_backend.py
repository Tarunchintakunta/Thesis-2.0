"""Live AWS backend. Needs a deployed stack in YOUR OWN account.

One run applies SQS/ESM settings, purges queues, injects faults via SSM,
sends orders, drains, then collects DynamoDB/DLQ/CloudWatch evidence.
"""
from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from control.fault_controller import SsmFaultController, schedule_for_run
from control.run_result import RunResult
from producer.generate_orders import make_orders
from producer.loadgen import arrival_times, post_to_api, send_to_sqs


@dataclass
class StackOutputs:
    queue_url: str
    dlq_url: str
    queue_arn: str
    api_url: str
    orders_table: str
    events_table: str
    consumer_function: str
    mapping_id: str
    fault_param: str

    @classmethod
    def from_terraform(cls, terraform_dir: str | Path) -> "StackOutputs":
        """Load outputs from ``terraform output -json``."""
        import subprocess

        tf_dir = Path(terraform_dir)
        proc = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=tf_dir,
            check=True,
            capture_output=True,
            text=True,
        )
        raw = json.loads(proc.stdout or "{}")

        def _val(key: str) -> str:
            entry = raw.get(key)
            if entry is None:
                raise KeyError(f"terraform output missing: {key}")
            value = entry.get("value") if isinstance(entry, dict) else entry
            if value is None:
                raise KeyError(f"terraform output {key} is null (Lambda packages missing?)")
            return str(value)

        return cls(
            queue_url=_val("orders_queue_url"),
            dlq_url=_val("orders_dlq_url"),
            queue_arn=_val("orders_queue_arn"),
            api_url=_val("sync_api_url"),
            orders_table=_val("orders_table_name"),
            events_table=_val("events_table_name"),
            consumer_function=_val("consumer_function_name"),
            mapping_id=_val("consumer_mapping_id"),
            fault_param=_val("fault_param_name"),
        )


def apply_queue_settings(sqs, lam, outputs: StackOutputs, spec, wait_s: float = 120.0) -> None:
    redrive = {"deadLetterTargetArn": _dlq_arn(sqs, outputs.dlq_url), "maxReceiveCount": str(spec.max_receive_count)}
    sqs.set_queue_attributes(
        QueueUrl=outputs.queue_url,
        Attributes={
            "VisibilityTimeout": str(spec.visibility_timeout),
            "RedrivePolicy": json.dumps(redrive),
            "DelaySeconds": str(spec.delivery_delay),
        },
    )
    lam.update_event_source_mapping(
        UUID=outputs.mapping_id,
        BatchSize=spec.batch_size,
        MaximumBatchingWindowInSeconds=int(spec.batching_window_s),
    )
    deadline = time.time() + wait_s
    while time.time() < deadline:
        state = lam.get_event_source_mapping(UUID=outputs.mapping_id)["State"]
        if state == "Enabled":
            return
        time.sleep(5)
    raise TimeoutError("event source mapping did not return to Enabled")


def _dlq_arn(sqs, dlq_url: str) -> str:
    return sqs.get_queue_attributes(QueueUrl=dlq_url, AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]


def queue_depth(sqs, queue_url: str) -> dict[str, int]:
    attrs = sqs.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=[
            "ApproximateNumberOfMessages",
            "ApproximateNumberOfMessagesNotVisible",
            "ApproximateNumberOfMessagesDelayed",
        ],
    )["Attributes"]
    return {
        "visible": int(attrs.get("ApproximateNumberOfMessages", 0)),
        "inflight": int(attrs.get("ApproximateNumberOfMessagesNotVisible", 0)),
        "delayed": int(attrs.get("ApproximateNumberOfMessagesDelayed", 0)),
    }


def drain_order_ids(sqs, queue_url: str, delete: bool = True, max_empty: int = 3) -> list[str]:
    """Read every message left in a queue and return their order ids."""
    ids: list[str] = []
    empty = 0
    while empty < max_empty:
        resp = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=1, VisibilityTimeout=60)
        msgs = resp.get("Messages", [])
        if not msgs:
            empty += 1
            continue
        empty = 0
        for msg in msgs:
            try:
                ids.append(json.loads(msg["Body"])["order_id"])
            except (ValueError, KeyError):
                ids.append("unparseable")
        if delete:
            sqs.delete_message_batch(
                QueueUrl=queue_url,
                Entries=[{"Id": str(i), "ReceiptHandle": m["ReceiptHandle"]} for i, m in enumerate(msgs)],
            )
    return ids


def cloudwatch_counters(cw, function_name: str, queue_name: str, start: float, end: float) -> dict[str, float]:
    """Best effort request/duration totals for the cost proxy."""
    import datetime as dt

    def total(namespace: str, metric: str, dims: list[dict[str, str]], stat: str = "Sum") -> float:
        resp = cw.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric,
            Dimensions=dims,
            StartTime=dt.datetime.fromtimestamp(start - 60, tz=dt.timezone.utc),
            EndTime=dt.datetime.fromtimestamp(end + 300, tz=dt.timezone.utc),
            Period=60,
            Statistics=[stat],
        )
        return float(sum(p[stat] for p in resp.get("Datapoints", [])))

    fn = [{"Name": "FunctionName", "Value": function_name}]
    q = [{"Name": "QueueName", "Value": queue_name}]
    try:
        duration_ms = total("AWS/Lambda", "Duration", fn)
        return {
            "invocations": total("AWS/Lambda", "Invocations", fn),
            "invocation_error": total("AWS/Lambda", "Errors", fn),
            "lambda_gb_s": duration_ms / 1000.0 * 0.25,  # 256 MB function
            "sqs_receive_calls": total("AWS/SQS", "NumberOfEmptyReceives", q)
            + total("AWS/SQS", "NumberOfMessagesReceived", q) / 10.0,
            "delete_batch_calls": total("AWS/SQS", "NumberOfMessagesDeleted", q) / 10.0,
        }
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] cloudwatch counters unavailable: {exc}")
        return {}


def run_live(spec, outputs: StackOutputs, clients: dict[str, Any] | None = None, cooldown_s: float = 61.0) -> RunResult:
    if clients is None:
        import boto3

        clients = {name: boto3.client(name) for name in ("sqs", "lambda", "ssm", "dynamodb", "cloudwatch")}
    sqs = clients["sqs"]
    faults = SsmFaultController(outputs.fault_param, clients["ssm"])
    faults.disable()

    if spec.arm == "queue":
        apply_queue_settings(sqs, clients["lambda"], outputs, spec)
        sqs.purge_queue(QueueUrl=outputs.queue_url)
        sqs.purge_queue(QueueUrl=outputs.dlq_url)
        time.sleep(cooldown_s)  # purge takes up to 60 s

    orders = make_orders(spec.order_count, spec.run_id, spec.seed, spec.poison_rate)
    offsets = arrival_times(
        spec.order_count, spec.load_profile, spec.rate_per_sec, spec.seed,
        burst_start=spec.burst_start_s, burst_len=spec.burst_len_s, burst_factor=spec.burst_factor,
    )
    run_start = time.time()
    faults.enable(schedule_for_run(spec.fault_mode, spec.fault_rate, run_start, spec.fault_start_s, spec.fault_window_s, spec.fault_point))

    produced: dict[str, float] = {}
    sync_results: list[dict[str, Any]] = []

    def producer() -> None:
        if spec.arm == "queue":
            produced.update(send_to_sqs(sqs, outputs.queue_url, orders, offsets, delay_s=spec.delivery_delay))
        else:
            sync_results.extend(post_to_api(outputs.api_url, orders, offsets, retries=spec.sync_client_retries, backoff_s=spec.sync_backoff_s))

    sender = threading.Thread(target=producer, daemon=True)
    sender.start()

    samples: list[dict[str, float]] = []
    horizon = run_start + max(offsets[-1], spec.fault_start_s + spec.fault_window_s) + spec.drain_timeout_s
    while time.time() < horizon:
        if spec.arm == "queue":
            samples.append({"t": time.time() - run_start, **queue_depth(sqs, outputs.queue_url)})
            if not sender.is_alive() and samples[-1]["visible"] + samples[-1]["inflight"] + samples[-1]["delayed"] == 0 and time.time() - run_start > spec.fault_start_s + spec.fault_window_s + 30:
                break
        elif not sender.is_alive():
            break
        time.sleep(spec.sample_interval_s)
    sender.join(timeout=60)
    run_end = time.time()
    faults.disable()

    if spec.arm == "sync":
        produced = {r["order_id"]: r["produced_at"] for r in sync_results}

    from common.dynamo import DynamoEventLog

    events = DynamoEventLog(outputs.events_table, clients["dynamodb"]).query_run(spec.run_id)
    for ev in events:  # make times relative to the run start like the simulator
        ev["ts"] -= run_start
    produced = {k: v - run_start for k, v in produced.items()}

    dlq_ids: list[str] = []
    remaining: list[str] = []
    if spec.arm == "queue":
        remaining = drain_order_ids(sqs, outputs.queue_url)
        dlq_ids = drain_order_ids(sqs, outputs.dlq_url)

    counters = cloudwatch_counters(
        clients["cloudwatch"], outputs.consumer_function, outputs.queue_url.rsplit("/", 1)[-1], run_start, run_end
    )
    counters["dynamo_event_writes"] = len(events)
    counters["sqs_send_batch_calls"] = len(produced) / 10.0

    window = spec.fault_window
    return RunResult(
        produced=produced,
        events=events,
        dlq_order_ids=dlq_ids,
        remaining_ids=remaining,
        samples=samples,
        fault_window=window,
        counters=counters,
        end_time=run_end - run_start,
        max_apply_count=0,
    )
