#!/usr/bin/env python3
"""Orchestrate Free-Tier-safe AWS live K8s eval for Pooja PAKS.

Flow:
  1) terraform apply (1× t3.micro + k3s + S3 + CW) — project=paks-k8s-live
  2) wait SSM Online + /opt/paks/READY
  3) upload minimal framework tarball to S3 → SSM pull + run live_scale_on_node.py
  4) pull TRACE JSON, PutMetricData, write results/formal_k8s_live_aws.json
  5) optionally terraform destroy (default: destroy=yes)

NEVER touches project=distributed-matrix-scaling (Venkat).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

import boto3

FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]
TERRAFORM_DIR = FRAMEWORK_ROOT / "terraform"
RESULTS_DIR = FRAMEWORK_ROOT / "results"
PROJECT_TAG = "paks-k8s-live"
VENKAT_TAG = "distributed-matrix-scaling"
REGION_DEFAULT = "eu-west-1"


def _run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=check, text=True)


def _terraform_output(name: str) -> str:
    out = subprocess.check_output(
        ["terraform", "output", "-raw", name],
        cwd=str(TERRAFORM_DIR),
        text=True,
    ).strip()
    return out


def _assert_not_venkat(instance_id: str, ec2) -> None:
    resp = ec2.describe_instances(InstanceIds=[instance_id])
    for res in resp.get("Reservations", []):
        for inst in res.get("Instances", []):
            tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
            proj = tags.get("project") or tags.get("Project") or ""
            if proj == VENKAT_TAG or "matrix-scale" in tags.get("Name", ""):
                raise RuntimeError(
                    f"Refusing to operate on Venkat instance {instance_id} tags={tags}"
                )
            if proj != PROJECT_TAG:
                raise RuntimeError(
                    f"Instance {instance_id} project tag={proj!r}, expected {PROJECT_TAG}"
                )


def _wait_ssm(instance_id: str, ssm, timeout_s: int = 600) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        resp = ssm.describe_instance_information(
            Filters=[{"Key": "InstanceIds", "Values": [instance_id]}]
        )
        infos = resp.get("InstanceInformationList", [])
        if infos and infos[0].get("PingStatus") == "Online":
            print(f"SSM Online: {instance_id}", flush=True)
            return
        print("waiting SSM Online…", flush=True)
        time.sleep(10)
    raise TimeoutError(f"SSM not Online for {instance_id} within {timeout_s}s")


def _ssm_run(instance_id: str, ssm, commands: list[str], timeout_s: int = 900) -> str:
    resp = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={"commands": commands},
        TimeoutSeconds=min(timeout_s, 3600),
        Comment="paks-k8s-live eval",
    )
    cmd_id = resp["Command"]["CommandId"]
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        time.sleep(5)
        inv = ssm.get_command_invocation(CommandId=cmd_id, InstanceId=instance_id)
        status = inv["Status"]
        if status in {"Success", "Cancelled", "TimedOut", "Failed"}:
            stdout = inv.get("StandardOutputContent") or ""
            stderr = inv.get("StandardErrorContent") or ""
            if status != "Success":
                raise RuntimeError(
                    f"SSM command {cmd_id} status={status}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
                )
            return stdout
        print(f"SSM {cmd_id} status={status}…", flush=True)
    raise TimeoutError(f"SSM command {cmd_id} timed out")


def _wait_ready_marker(instance_id: str, ssm, timeout_s: int = 900) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            out = _ssm_run(
                instance_id,
                ssm,
                [
                    "test -f /opt/paks/READY && cat /opt/paks/READY "
                    "&& kubectl get deploy paks-demo"
                ],
                timeout_s=120,
            )
            if "k3s+paks-demo ready" in out or "paks-demo" in out:
                print("k3s READY marker OK", flush=True)
                print(out, flush=True)
                return
        except RuntimeError as exc:
            print(f"READY poll: {exc}", flush=True)
        time.sleep(20)
    raise TimeoutError("k3s /opt/paks/READY not seen in time")


def _build_tarball(dest: Path) -> Path:
    """Minimal tree for on-node live eval."""
    tar_path = dest / "paks-live.tgz"
    include = [
        "src/__init__.py",
        "src/k8s/__init__.py",
        "src/k8s/api_shapes.py",
        "src/k8s/adaptive_engine.py",
        "src/k8s/dry_run_client.py",
        "src/k8s/live_client.py",
        "src/eval/__init__.py",
        "src/eval/metrics.py",
        "src/models/__init__.py",
        "src/models/lstm_predictor.py",
        "scripts/live_scale_on_node.py",
        "data/traces/alibaba_v2018_machine_usage_sample_cluster_cpu.csv",
    ]
    with tarfile.open(tar_path, "w:gz") as tf:
        for rel in include:
            path = FRAMEWORK_ROOT / rel
            if not path.exists():
                print(f"WARN missing {rel}", flush=True)
                continue
            tf.add(path, arcname=rel)
    return tar_path


def terraform_apply() -> dict:
    _run(["terraform", "init", "-input=false"], cwd=TERRAFORM_DIR)
    _run(["terraform", "apply", "-auto-approve", "-input=false"], cwd=TERRAFORM_DIR)
    return {
        "instance_id": _terraform_output("instance_id"),
        "s3_bucket": _terraform_output("s3_bucket"),
        "cloudwatch_log_group": _terraform_output("cloudwatch_log_group"),
        "region": _terraform_output("region"),
        "project_tag": _terraform_output("project_tag"),
    }


def terraform_destroy() -> None:
    _run(["terraform", "destroy", "-auto-approve", "-input=false"], cwd=TERRAFORM_DIR)


def verify_pooja_gone(region: str) -> dict:
    """Confirm no EC2/S3/CW resources remain with project=paks-k8s-live."""
    ec2 = boto3.client("ec2", region_name=region)
    s3 = boto3.client("s3", region_name=region)
    logs = boto3.client("logs", region_name=region)

    resp = ec2.describe_instances(
        Filters=[
            {"Name": "tag:project", "Values": [PROJECT_TAG]},
            {
                "Name": "instance-state-name",
                "Values": ["pending", "running", "stopping", "stopped"],
            },
        ]
    )
    leftover_ids = []
    for res in resp.get("Reservations", []):
        for inst in res.get("Instances", []):
            leftover_ids.append(inst["InstanceId"])

    leftover_buckets = [
        b["Name"]
        for b in s3.list_buckets().get("Buckets", [])
        if b["Name"].startswith(f"{PROJECT_TAG}-")
    ]

    leftover_logs = []
    paginator = logs.get_paginator("describe_log_groups")
    for page in paginator.paginate(logGroupNamePrefix=f"/{PROJECT_TAG}/"):
        for g in page.get("logGroups", []):
            leftover_logs.append(g["logGroupName"])

    venkat = ec2.describe_instances(
        Filters=[
            {"Name": "tag:project", "Values": [VENKAT_TAG]},
            {"Name": "instance-state-name", "Values": ["running", "pending", "stopped"]},
        ]
    )
    venkat_ids = [
        i["InstanceId"]
        for r in venkat.get("Reservations", [])
        for i in r.get("Instances", [])
    ]

    return {
        "pooja_ec2_leftover": leftover_ids,
        "pooja_s3_leftover": leftover_buckets,
        "pooja_logs_leftover": leftover_logs,
        "venkat_still_present": venkat_ids,
        "destroy_confirmed": not leftover_ids and not leftover_buckets and not leftover_logs,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--region", default=os.environ.get("AWS_REGION", REGION_DEFAULT))
    ap.add_argument("--skip-apply", action="store_true", help="Reuse existing terraform state")
    ap.add_argument("--skip-destroy", action="store_true", help="Leave stack up (debug)")
    ap.add_argument("--destroy-only", action="store_true")
    ap.add_argument("--steps", type=int, default=16, help="Live scale loop steps (keep small)")
    ap.add_argument("--max-replicas", type=int, default=3)
    args = ap.parse_args()
    region = args.region
    os.environ.setdefault("AWS_DEFAULT_REGION", region)

    RESULTS_DIR.mkdir(exist_ok=True)

    if args.destroy_only:
        if (TERRAFORM_DIR / "terraform.tfstate").exists() or (
            TERRAFORM_DIR / "terraform.tfstate.backup"
        ).exists():
            terraform_destroy()
        report = verify_pooja_gone(region)
        (RESULTS_DIR / "aws_destroy_verify.json").write_text(
            json.dumps(report, indent=2) + "\n"
        )
        print(json.dumps(report, indent=2))
        return 0 if report["destroy_confirmed"] else 2

    if not args.skip_apply:
        outs = terraform_apply()
    else:
        outs = {
            "instance_id": _terraform_output("instance_id"),
            "s3_bucket": _terraform_output("s3_bucket"),
            "cloudwatch_log_group": _terraform_output("cloudwatch_log_group"),
            "region": _terraform_output("region"),
            "project_tag": _terraform_output("project_tag"),
        }

    instance_id = outs["instance_id"]
    bucket = outs["s3_bucket"]
    log_group = outs["cloudwatch_log_group"]

    ec2 = boto3.client("ec2", region_name=region)
    ssm = boto3.client("ssm", region_name=region)
    s3 = boto3.client("s3", region_name=region)
    cw = boto3.client("cloudwatch", region_name=region)
    logs_client = boto3.client("logs", region_name=region)

    _assert_not_venkat(instance_id, ec2)
    _wait_ssm(instance_id, ssm, timeout_s=1200)
    _wait_ready_marker(instance_id, ssm, timeout_s=1200)

    with tempfile.TemporaryDirectory(prefix="paks-live-") as tmp:
        tar_path = _build_tarball(Path(tmp))
        key = f"uploads/paks-live-{int(time.time())}.tgz"
        s3.upload_file(str(tar_path), bucket, key)
        print(f"uploaded s3://{bucket}/{key}", flush=True)

        run_out = _ssm_run(
            instance_id,
            ssm,
            [
                "set -euxo pipefail",
                "mkdir -p /opt/paks",
                f"aws s3 cp s3://{bucket}/{key} /opt/paks/paks-live.tgz --region {region}",
                "rm -rf /opt/paks/paks-framework",
                "mkdir -p /opt/paks/paks-framework",
                "tar -xzf /opt/paks/paks-live.tgz -C /opt/paks/paks-framework",
                "python3 -m ensurepip --user 2>/dev/null || true",
                "python3 -m pip install --user --quiet numpy pandas "
                "|| dnf -y install python3-numpy",
                "export PYTHONPATH=\"/root/.local/lib/python3.9/site-packages:${PYTHONPATH:-}\"",
                "python3 -c 'import numpy, pandas; print(numpy.__version__, pandas.__version__)'",
                "export PAKS_K8S_APPLY=1",
                "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml",
                f"export PAKS_LIVE_STEPS={args.steps}",
                f"export PAKS_LIVE_MAX_REPLICAS={args.max_replicas}",
                f"export PAKS_LIVE_SEED={os.environ.get('PAKS_LIVE_SEED', '42')}",
                "export PAKS_LIVE_OUT=/opt/paks/formal_k8s_live_aws.json",
                "cd /opt/paks/paks-framework",
                "python3 scripts/live_scale_on_node.py",
                f"aws s3 cp /opt/paks/formal_k8s_live_aws.json "
                f"s3://{bucket}/results/formal_k8s_live_aws.json --region {region}",
                "cat /opt/paks/formal_k8s_live_aws.json",
            ],
            timeout_s=1200,
        )
        print(run_out[-4000:], flush=True)

    local_json = RESULTS_DIR / "formal_k8s_live_aws.json"
    s3.download_file(bucket, "results/formal_k8s_live_aws.json", str(local_json))
    payload = json.loads(local_json.read_text())

    metric_data = []
    for policy_key, dim_val in (
        ("hpa_metrics", "reactive-hpa"),
        ("paks_metrics", "paks-adaptive"),
    ):
        m = payload.get(policy_key) or {}
        for metric_name, field in (
            ("ScalingLatencyMean", "scaling_latency_s_mean"),
            ("CpuUtilMean", "cpu_util_mean"),
            ("SlaCompliance", "sla_compliance"),
            ("ScalingEvents", "scaling_events"),
        ):
            if field in m and m[field] is not None:
                metric_data.append(
                    {
                        "MetricName": metric_name,
                        "Dimensions": [
                            {"Name": "Policy", "Value": dim_val},
                            {"Name": "Project", "Value": PROJECT_TAG},
                        ],
                        "Value": float(m[field]),
                        "Unit": "None",
                    }
                )
    if metric_data:
        cw.put_metric_data(Namespace="PAKS/LiveK8s", MetricData=metric_data[:20])

    try:
        stream = f"live-{instance_id}-{int(time.time())}"
        logs_client.create_log_stream(logGroupName=log_group, logStreamName=stream)
        logs_client.put_log_events(
            logGroupName=log_group,
            logStreamName=stream,
            logEvents=[
                {
                    "timestamp": int(time.time() * 1000),
                    "message": json.dumps(
                        {
                            "event": "paks_live_complete",
                            "instance_id": instance_id,
                            "hpa_lat": (payload.get("hpa_latency") or {}),
                            "paks_lat": (payload.get("paks_latency") or {}),
                        }
                    ),
                }
            ],
        )
    except Exception as exc:  # noqa: BLE001
        print(f"CW logs warning: {exc}", flush=True)

    payload["aws"] = {
        "region": region,
        "instance_id": instance_id,
        "s3_bucket": bucket,
        "s3_results_key": "results/formal_k8s_live_aws.json",
        "cloudwatch_namespace": "PAKS/LiveK8s",
        "cloudwatch_log_group": log_group,
        "project_tag": PROJECT_TAG,
        "live_cloudwatch": True,
    }
    payload.setdefault("evidence", {})
    payload["evidence"]["cloudwatch"] = "LIVE"
    for key in ("hpa_metrics", "paks_metrics"):
        if key in payload and isinstance(payload[key], dict):
            payload[key]["live_cloudwatch"] = True
    local_json.write_text(json.dumps(payload, indent=2, default=str) + "\n")
    s3.upload_file(str(local_json), bucket, "results/formal_k8s_live_aws.json")

    destroy_report = None
    if not args.skip_destroy:
        print("Destroying paks-k8s-live stack…", flush=True)
        terraform_destroy()
        destroy_report = verify_pooja_gone(region)
        (RESULTS_DIR / "aws_destroy_verify.json").write_text(
            json.dumps(destroy_report, indent=2) + "\n"
        )
        print(json.dumps(destroy_report, indent=2))
        if not destroy_report["destroy_confirmed"]:
            print("WARNING: destroy incomplete", flush=True)
            return 3
        if len(destroy_report.get("venkat_still_present") or []) < 1:
            print(
                "WARNING: Venkat instances not visible — check you did not destroy them",
                flush=True,
            )

    summary = {
        "wrote": str(local_json),
        "live_apply": True,
        "destroyed": destroy_report is not None and destroy_report.get("destroy_confirmed"),
        "destroy_report": destroy_report,
        "hpa_scaling_latency_mean_s": (payload.get("hpa_metrics") or {}).get(
            "scaling_latency_s_mean"
        ),
        "paks_scaling_latency_mean_s": (payload.get("paks_metrics") or {}).get(
            "scaling_latency_s_mean"
        ),
    }
    (RESULTS_DIR / "aws_live_run_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(exc.returncode or 1)
