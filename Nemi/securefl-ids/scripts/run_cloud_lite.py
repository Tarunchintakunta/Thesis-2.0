#!/usr/bin/env python3
"""Minimal live-cloud FL round: train on this host, persist rounds to S3, emit CW metrics.

Lite floor: 2 in-process clients, 3 rounds, small UNSW/synthetic sample.
Not a 50-round / 2.5M-flow campaign.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time
import traceback
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import torch

from src.baseline.baseline_fl_ids import BaselineFLIDS
from src.improved.securefl_ids import SecureFLIDS


def _jsonable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, (np.floating, float)):
        return float(obj)
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _imds(path: str) -> Optional[str]:
    try:
        token_req = urllib.request.Request(
            "http://169.254.169.254/latest/api/token",
            method="PUT",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
        )
        token = urllib.request.urlopen(token_req, timeout=2).read().decode()
        req = urllib.request.Request(
            f"http://169.254.169.254/latest/meta-data/{path}",
            headers={"X-aws-ec2-metadata-token": token},
        )
        return urllib.request.urlopen(req, timeout=2).read().decode()
    except Exception:
        return None


def _meminfo() -> Dict[str, str]:
    out: Dict[str, str] = {}
    try:
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                if ":" not in line:
                    continue
                key, val = line.split(":", 1)
                if key in {"MemTotal", "MemAvailable", "SwapTotal", "SwapFree"}:
                    out[key] = val.strip()
    except OSError:
        pass
    return out


class CloudBus:
    """S3 parameter/artefact bus + CloudWatch metrics/logs. No-ops when offline."""

    def __init__(
        self,
        *,
        offline: bool,
        region: str,
        bucket: Optional[str],
        log_group: Optional[str],
        run_id: str,
    ):
        self.offline = offline
        self.region = region
        self.bucket = bucket
        self.log_group = log_group
        self.run_id = run_id
        self.prefix = f"lite/{run_id}"
        self.s3_keys: List[str] = []
        self.cw_puts = 0
        self.log_events_ok = 0
        self._s3 = None
        self._cw = None
        self._logs = None
        self._seq = None
        self._log_stream = None
        if offline:
            return
        import boto3

        self._s3 = boto3.client("s3", region_name=region)
        self._cw = boto3.client("cloudwatch", region_name=region)
        self._logs = boto3.client("logs", region_name=region)
        if log_group:
            stream = f"lite-{run_id}"
            try:
                self._logs.create_log_stream(logGroupName=log_group, logStreamName=stream)
            except Exception as exc:  # noqa: BLE001
                if "already exists" not in str(exc).lower() and "ResourceAlreadyExists" not in type(exc).__name__:
                    print(f"[warn] create_log_stream: {exc}", flush=True)
            self._log_stream = stream
        else:
            self._log_stream = None

    def put_bytes(self, relkey: str, body: bytes, content_type: str = "application/octet-stream") -> str:
        key = f"{self.prefix}/{relkey.lstrip('/')}"
        if self.offline or not self.bucket:
            return key
        self._s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=body,
            ContentType=content_type,
        )
        self.s3_keys.append(key)
        return key

    def put_json(self, relkey: str, payload: dict) -> str:
        body = json.dumps(_jsonable(payload), indent=2).encode("utf-8")
        return self.put_bytes(relkey, body, "application/json")

    def put_state(self, relkey: str, state: dict) -> str:
        buf = io.BytesIO()
        torch.save(state, buf)
        return self.put_bytes(relkey, buf.getvalue())

    def get_state(self, key: str) -> dict:
        if self.offline or not self.bucket:
            raise RuntimeError("offline: cannot round-trip S3 state")
        obj = self._s3.get_object(Bucket=self.bucket, Key=key)
        blob = io.BytesIO(obj["Body"].read())
        try:
            return torch.load(blob, map_location="cpu", weights_only=False)
        except TypeError:
            blob.seek(0)
            return torch.load(blob, map_location="cpu")

    def put_metrics(self, arm: str, round_idx: int, metrics: dict) -> None:
        if self.offline or self._cw is None:
            return
        dims = [
            {"Name": "project", "Value": "securefl-ids"},
            {"Name": "arm", "Value": arm},
            {"Name": "run_id", "Value": self.run_id},
        ]
        mapping = [
            ("Accuracy", metrics.get("accuracy")),
            ("F1", metrics.get("f1_score")),
            ("CommMB", metrics.get("communication_cost")),
            ("RoundTimeSeconds", metrics.get("round_time")),
        ]
        data = []
        ts = datetime.now(timezone.utc)
        for name, val in mapping:
            if val is None:
                continue
            data.append(
                {
                    "MetricName": name,
                    "Dimensions": dims,
                    "Timestamp": ts,
                    "Value": float(val),
                    "Unit": "None",
                }
            )
        if not data:
            return
        try:
            self._cw.put_metric_data(Namespace="SecureFL-IDS", MetricData=data)
            self.cw_puts += 1
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] put_metric_data: {exc}", flush=True)

    def log(self, message: str) -> None:
        print(message, flush=True)
        if self.offline or self._logs is None or not self.log_group or not self._log_stream:
            return
        kwargs = {
            "logGroupName": self.log_group,
            "logStreamName": self._log_stream,
            "logEvents": [
                {"timestamp": int(time.time() * 1000), "message": message[:250000]}
            ],
        }
        if self._seq:
            kwargs["sequenceToken"] = self._seq
        try:
            resp = self._logs.put_log_events(**kwargs)
            self._seq = resp.get("nextSequenceToken")
            self.log_events_ok += 1
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] put_log_events: {exc}", flush=True)


def _resolve_data_path(explicit: Optional[str]) -> str:
    candidates = []
    if explicit:
        candidates.append(explicit)
    candidates.extend(
        [
            os.path.join("data", "unsw_lite_cloud.csv"),
            os.path.join("data", "UNSW_NB15_training-set.csv"),
        ]
    )
    for path in candidates:
        if path and os.path.exists(path):
            return path
    raise FileNotFoundError(
        "No UNSW CSV found. Package data/unsw_lite_cloud.csv or pass --data-path."
    )


def _data_provenance(path: str) -> dict:
    import pandas as pd

    df = pd.read_csv(path, nrows=3)
    n_rows = sum(1 for _ in open(path, encoding="utf-8")) - 1
    kind = "real-lite" if len(df.columns) >= 30 else "synthetic-lite"
    return {
        "local_path": path,
        "kind": kind,
        "n_rows": n_rows,
        "n_cols": int(len(df.columns)),
        "columns_sample": [str(c) for c in list(df.columns[:12])],
    }


def _summary_from_history(system) -> dict:
    return _jsonable(system.get_results_summary())


def run_arm(
    *,
    arm: str,
    system,
    num_rounds: int,
    local_epochs: int,
    learning_rate: float,
    bus: CloudBus,
    communication_efficient: bool,
    privacy,
) -> dict:
    from src.common.federated import federated_learning_round

    history_rounds = []
    bus.log(f"arm={arm} start rounds={num_rounds}")
    for round_idx in range(num_rounds):
        t0 = time.time()
        round_result = federated_learning_round(
            server=system.server,
            clients=system.clients,
            local_epochs=local_epochs,
            learning_rate=learning_rate,
            privacy_mechanism=privacy,
            communication_efficient=communication_efficient,
        )
        elapsed = time.time() - t0
        test_metrics = system.evaluate(system.test_X, system.test_y)
        global_params = {
            name: param.detach().cpu().clone()
            for name, param in system.global_model.named_parameters()
        }
        key = bus.put_state(f"rounds/{arm}/round-{round_idx + 1:02d}/global.pt", global_params)
        round_trip_ok = False
        if not bus.offline:
            reloaded = bus.get_state(key)
            with torch.no_grad():
                for name, param in system.global_model.named_parameters():
                    if name in reloaded:
                        param.copy_(reloaded[name].to(param.device))
            for client in system.clients:
                client.update_model(
                    {k: v.clone() for k, v in reloaded.items()}
                )
            round_trip_ok = True
        rec = {
            "round": round_idx + 1,
            "accuracy": float(test_metrics["accuracy"]),
            "f1_score": float(test_metrics["f1_score"]),
            "precision": float(test_metrics.get("precision", 0.0)),
            "recall": float(test_metrics.get("recall", 0.0)),
            "communication_cost": float(round_result["communication_cost"]),
            "round_time": float(elapsed),
            "s3_global_key": key,
            "s3_round_trip": round_trip_ok,
        }
        history_rounds.append(rec)
        system.history["rounds"].append(round_idx + 1)
        system.history["test_accuracy"].append(rec["accuracy"])
        system.history["test_f1"].append(rec["f1_score"])
        system.history["communication_cost"].append(rec["communication_cost"])
        system.history["round_time"].append(rec["round_time"])
        bus.put_metrics(arm, round_idx + 1, rec)
        bus.put_json(f"rounds/{arm}/round-{round_idx + 1:02d}/metrics.json", rec)
        bus.log(
            f"arm={arm} round={round_idx + 1}/{num_rounds} "
            f"acc={rec['accuracy']:.4f} f1={rec['f1_score']:.4f} "
            f"comm={rec['communication_cost']:.3f}MB t={rec['round_time']:.2f}s "
            f"s3_rt={round_trip_ok}"
        )
    return {
        "arm": arm,
        "summary": _summary_from_history(system),
        "rounds": history_rounds,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="SecureFL-IDS lite cloud FL")
    parser.add_argument("--offline", action="store_true", help="Train without S3/CW (local smoke)")
    parser.add_argument("--bucket", default=os.environ.get("SECUREFL_BUCKET", ""))
    parser.add_argument("--region", default=os.environ.get("AWS_DEFAULT_REGION", "eu-west-1"))
    parser.add_argument("--log-group", default=os.environ.get("SECUREFL_LOG_GROUP", ""))
    parser.add_argument("--run-id", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--num-clients", type=int, default=2)
    parser.add_argument("--num-rounds", type=int, default=3)
    parser.add_argument("--local-epochs", type=int, default=1)
    parser.add_argument("--sample-size", type=int, default=2500)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--data-path", default="")
    parser.add_argument("--skip-improved", action="store_true")
    parser.add_argument("--out", default="results/live/cloud_lite_summary.json")
    args = parser.parse_args()

    if not args.offline and not args.bucket:
        print("ERROR: --bucket required unless --offline", file=sys.stderr)
        return 2

    started = _utc_now()
    t0 = time.perf_counter()
    data_path = _resolve_data_path(args.data_path or None)
    provenance = _data_provenance(data_path)
    bus = CloudBus(
        offline=args.offline,
        region=args.region,
        bucket=args.bucket or None,
        log_group=args.log_group or None,
        run_id=args.run_id,
    )
    instance_id = _imds("instance-id")
    instance_type = _imds("instance-type")
    bus.log(
        f"lite start run_id={args.run_id} offline={args.offline} "
        f"instance={instance_id} type={instance_type} data={data_path}"
    )
    bus.put_json(
        "config.json",
        {
            "num_clients": args.num_clients,
            "num_rounds": args.num_rounds,
            "local_epochs": args.local_epochs,
            "sample_size": args.sample_size,
            "learning_rate": args.learning_rate,
            "data_path": data_path,
            "data_provenance": provenance,
        },
    )

    arms: Dict[str, Any] = {}
    errors: Dict[str, str] = {}

    try:
        baseline = BaselineFLIDS(num_clients=args.num_clients)
        baseline.setup(data_path=data_path, sample_size=args.sample_size)
        arms["baseline"] = run_arm(
            arm="baseline",
            system=baseline,
            num_rounds=args.num_rounds,
            local_epochs=args.local_epochs,
            learning_rate=args.learning_rate,
            bus=bus,
            communication_efficient=False,
            privacy=baseline.privacy,
        )
    except Exception as exc:  # noqa: BLE001
        errors["baseline"] = f"{exc}\n{traceback.format_exc()}"
        bus.log(f"baseline FAILED: {exc}")

    if not args.skip_improved:
        try:
            improved = SecureFLIDS(
                num_clients=args.num_clients,
                communication_efficient=True,
                compression_ratio=0.5,
            )
            improved.setup(data_path=data_path, sample_size=args.sample_size)
            arms["improved"] = run_arm(
                arm="improved",
                system=improved,
                num_rounds=args.num_rounds,
                local_epochs=args.local_epochs,
                learning_rate=args.learning_rate,
                bus=bus,
                communication_efficient=True,
                privacy=improved.privacy,
            )
        except Exception as exc:  # noqa: BLE001
            errors["improved"] = f"{exc}\n{traceback.format_exc()}"
            bus.log(f"improved FAILED: {exc}")

    elapsed = time.perf_counter() - t0
    payload = {
        "round": "live_cloud_fl_lite",
        "mode": "offline_smoke" if args.offline else "live_aws",
        "started_at": started,
        "finished_at": _utc_now(),
        "elapsed_s": elapsed,
        "region": args.region,
        "bucket": args.bucket or None,
        "log_group": args.log_group or None,
        "run_id": args.run_id,
        "instance_id": instance_id,
        "instance_type": instance_type,
        "meminfo": _meminfo(),
        "tags_policy": {
            "project": "securefl-ids",
            "managed_by": "terraform",
            "purpose": "research-eval",
            "data": "unsw-nb15-lite",
            "note": "No personal name/ID in resource names or tags.",
        },
        "config": {
            "num_clients": args.num_clients,
            "num_rounds": args.num_rounds,
            "local_epochs": args.local_epochs,
            "sample_size": args.sample_size,
            "learning_rate": args.learning_rate,
            "clients_execution": "in-process on one EC2 server (client_count=0)",
            "aggregation_bus": "s3_round_trip" if not args.offline else "in_memory",
            "lambda_used": False,
        },
        "data_provenance": provenance,
        "arms": {k: {"summary": v["summary"], "rounds": v["rounds"]} for k, v in arms.items()},
        "errors": errors or None,
        "s3": {
            "prefix": bus.prefix,
            "object_count": len(bus.s3_keys),
            "sample_keys": bus.s3_keys[:12],
        },
        "cloudwatch": {
            "metric_puts": bus.cw_puts,
            "log_events_ok": bus.log_events_ok,
            "namespace": "SecureFL-IDS",
        },
        "limitations": [
            "Lite floor only: 2 clients × 3 rounds × small sample; not full 2.5M-flow / 50-round campaign.",
            "Federated clients are in-process on one t3.micro; multi-instance WAN FL is out of scope here.",
            "Docker/Kubernetes not executed in this lite script.",
            "Did not use Lambda (Vikas campaign_r5 holds shared ConcurrentExecutions).",
        ],
        "destroy_after": True,
        "destroy_status": {
            "terraform_destroy": "pending_orchestrator",
        },
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(_jsonable(payload), fh, indent=2)
        fh.write("\n")
    bus.put_json("cloud_lite_summary.json", payload)
    bus.log(f"wrote {args.out} elapsed_s={elapsed:.1f} arms={list(arms)} errors={list(errors)}")
    if "baseline" not in arms:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
