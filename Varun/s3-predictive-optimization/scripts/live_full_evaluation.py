#!/usr/bin/env python3
"""Full-scale LIVE FinOps evaluation (three-workload Wilcoxon).

Not lite: 3 workloads × n_trials trial-buckets × objects_per_trial live S3
objects. Metadata via ListObjectsV2 (+ object user-metadata for access attrs).
Costs via SavingsEstimator vs Lifecycle and Intelligent-Tiering. Wilcoxon
paired across trial buckets. CE / Pricing / CW probes recorded honestly.

Usage:
  python scripts/live_full_evaluation.py --eval-id 1
  OUT: results/live/evaluation_r{N}/

Restored 2026-09-22 from bytecode + logs after scripts/live_full_evaluation.py
was deleted (pyc retained). Behaviour matches prior e1 live prints.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation.metrics import MetricsCalculator
from src.metadata.boto3_collector import list_object_metadata, metadata_report_from_listing
from src.pricing.s3_pricing import S3Pricing
from src.recommendation.baseline import BaselineRecommender
from src.savings.estimator import SavingsEstimator
from src.simulator.workload_generator import WorkloadGenerator

REGION = "eu-west-1"
OBJECT_BYTES = 163840  # 160 KiB body (IA min-billable friendly)

WORKLOAD_SEED_OFFSET = {
    "static_archival": 0,
    "mixed_access": 1000,
    "high_churn": 2000,
}

WORKLOADS: Dict[str, Dict[str, Any]] = {
    "static_archival": {
        "access_patterns": [{"hot": 0.05, "warm": 0.15, "cold": 0.8}],
        "size_distribution": {"mean_mb": 5, "std_mb": 2, "min_mb": 0.2, "max_mb": 20},
    },
    "mixed_access": {
        "access_patterns": [{"hot": 0.2, "warm": 0.3, "cold": 0.5}],
        "size_distribution": {"mean_mb": 8, "std_mb": 4, "min_mb": 0.2, "max_mb": 40},
    },
    "high_churn": {
        "access_patterns": [{"hot": 0.5, "warm": 0.3, "cold": 0.2}],
        "size_distribution": {"mean_mb": 4, "std_mb": 2, "min_mb": 0.2, "max_mb": 15},
    },
}

BASELINE_CONFIG = {
    "baseline": {
        "age_threshold_ia": 30,
        "age_threshold_glacier_instant": 90,
        "age_threshold_glacier_deep": 180,
        "access_threshold_ia": 5,
        "access_threshold_glacier": 1,
        "size_threshold_kb": 128,
    }
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.isoformat()


def resolve_bucket(s3, state_path: Path | None = None) -> tuple[str, str]:
    if state_path is None:
        state_path = ROOT / "terraform" / "terraform.tfstate"
    bucket = None
    log_group = "/research/s3-pred-opt"
    if state_path.exists():
        state = json.loads(state_path.read_text())
        outs = state.get("outputs") or {}
        bucket = (outs.get("bucket_name") or {}).get("value")
        log_group = (outs.get("log_group") or {}).get("value") or log_group
    if not bucket:
        matches = sorted(
            b["Name"]
            for b in s3.list_buckets().get("Buckets", [])
            if b["Name"].startswith("s3-pred-opt-")
        )
        if not matches:
            raise RuntimeError("No s3-pred-opt-* bucket; terraform apply first")
        bucket = matches[-1]
    return bucket, log_group


def put_trial_objects(s3, bucket: str, prefix: str, objects: List[Dict]) -> List[float]:
    payload = b"0" * OBJECT_BYTES
    put_ms: List[float] = []
    for obj in objects:
        key = f"{prefix}/{obj.get('key', obj.get('object_id', 'obj'))}"
        meta = {
            "age-days": str(obj.get("age_days", 0)),
            "access-frequency": str(obj.get("access_frequency", 0)),
            "last-access-days": str(obj.get("last_access_days", obj.get("age_days", 0))),
            "size-kb": str(obj.get("size_kb", OBJECT_BYTES // 1024)),
            "access-pattern": str(obj.get("access_pattern", "cold")),
        }
        t0 = time.perf_counter()
        s3.put_object(Bucket=bucket, Key=key, Body=payload, Metadata=meta)
        put_ms.append((time.perf_counter() - t0) * 1000.0)
        obj["key"] = key
        obj["size_kb"] = float(obj.get("size_kb") or (OBJECT_BYTES / 1024.0))
    return put_ms


def rebuild_from_live(s3, bucket: str, prefix: str) -> List[Dict]:
    rows = list_object_metadata(s3, bucket, prefix=prefix)
    rebuilt: List[Dict] = []
    for row in rows:
        key = row.get("key") or row.get("Key")
        head = s3.head_object(Bucket=bucket, Key=key)
        md_raw = head.get("Metadata") or {}
        md = {k.lower().replace("_", "-"): v for k, v in md_raw.items()}
        size_kb = float(
            md.get("size-kb")
            or (head.get("ContentLength", OBJECT_BYTES) / 1024.0)
        )
        rebuilt.append(
            {
                "key": key,
                "object_id": Path(key).stem,
                "age_days": float(md.get("age-days", 0)),
                "access_frequency": float(md.get("access-frequency", 0)),
                "last_access_days": float(
                    md.get("last-access-days", md.get("age-days", 0))
                ),
                "size_kb": size_kb,
                # SavingsEstimator prices on size_mb; metadata only stores size-kb.
                "size_mb": size_kb / 1024.0,
                "access_pattern": md.get("access-pattern", "cold"),
                "current_storage_class": "STANDARD",
            }
        )
    return rebuilt


def trial_costs_live(objects: List[Dict]) -> Dict[str, float]:
    t0 = time.perf_counter()
    recs = BaselineRecommender(BASELINE_CONFIG, pricing=S3Pricing()).recommend_batch(
        objects
    )
    estimator = SavingsEstimator(pricing=S3Pricing())
    cmp_ = estimator.comprehensive_comparison(objects, recs)
    overhead_s = time.perf_counter() - t0
    our = float(cmp_["our_approach"]["cost_monthly"])
    lc = float(cmp_["aws_lifecycle_policies"]["cost_monthly"])
    it = float(cmp_["aws_intelligent_tiering"]["cost_monthly"])
    return {
        "our_cost": our,
        "lifecycle_cost": lc,
        "intelligent_tiering_cost": it,
        "overhead_s": overhead_s,
        "n_objects": len(objects),
    }


def ensure_inventory_config(s3, bucket: str) -> Dict[str, Any]:
    dest_prefix = "inventory/"
    try:
        s3.put_bucket_inventory_configuration(
            Bucket=bucket,
            Id="pred-opt-daily",
            InventoryConfiguration={
                "Id": "pred-opt-daily",
                "IsEnabled": True,
                "IncludedObjectVersions": "Current",
                "Destination": {
                    "S3BucketDestination": {
                        "Bucket": f"arn:aws:s3:::{bucket}",
                        "Format": "CSV",
                        "Prefix": dest_prefix,
                    }
                },
                "Schedule": {"Frequency": "Daily"},
                "OptionalFields": ["Size", "LastModifiedDate", "StorageClass"],
            },
        )
        return {"ok": True, "prefix": dest_prefix}
    except ClientError as exc:
        return {"ok": False, "error": str(exc)}


def probe_ce_pricing_cw(bucket: str, log_group: str, eval_id: int) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    pricing = boto3.client("pricing", region_name="us-east-1")
    try:
        resp = pricing.get_products(
            ServiceCode="AmazonS3",
            Filters=[
                {"Type": "TERM_MATCH", "Field": "regionCode", "Value": REGION},
            ],
            MaxResults=1,
        )
        out["pricing_api"] = {"ok": True, "n_products": len(resp.get("PriceList", []))}
    except ClientError as exc:
        out["pricing_api"] = {"ok": False, "error": str(exc)}

    ce = boto3.client("ce", region_name="us-east-1")
    try:
        end = utc_now().date()
        start = end - timedelta(days=7)
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
        total = 0.0
        for row in ce_resp.get("ResultsByTime", []):
            total += float(row["Total"]["UnblendedCost"]["Amount"])
        out["cost_explorer"] = {
            "ok": True,
            "window_days": 7,
            "s3_unblended_sum": total,
            "note": "Account-window probe; not campaign-settled object costs",
        }
    except ClientError as exc:
        out["cost_explorer"] = {"ok": False, "error": str(exc)}

    cw = boto3.client("cloudwatch", region_name=REGION)
    try:
        metrics = cw.list_metrics(
            Namespace="AWS/S3",
            Dimensions=[{"Name": "BucketName", "Value": bucket}],
        )
        out["cloudwatch_metrics"] = {"ok": True, "n": len(metrics.get("Metrics", []))}
    except ClientError as exc:
        out["cloudwatch_metrics"] = {"ok": False, "error": str(exc)}

    logs = boto3.client("logs", region_name=REGION)
    stream = f"eval-r{eval_id}-{utc_now().strftime('%Y%m%dT%H%M%SZ')}"
    try:
        try:
            logs.create_log_stream(logGroupName=log_group, logStreamName=stream)
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") != "ResourceAlreadyExistsException":
                raise
        logs.put_log_events(
            logGroupName=log_group,
            logStreamName=stream,
            logEvents=[
                {
                    "timestamp": int(utc_now().timestamp() * 1000),
                    "message": json.dumps(
                        {"eval_id": eval_id, "bucket": bucket, "event": "probe"}
                    ),
                }
            ],
        )
        out["cloudwatch_logs"] = {"ok": True, "stream": stream}
    except ClientError as exc:
        out["cloudwatch_logs"] = {"ok": False, "error": str(exc)}
    return out


def run_evaluation(
    eval_id: int, n_trials: int, objects_per_trial: int, seed: int
) -> Dict[str, Any]:
    out_dir = ROOT / "results" / "live" / f"evaluation_r{eval_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    started = utc_now()
    s3 = boto3.client("s3", region_name=REGION)
    bucket, log_group = resolve_bucket(s3)
    inventory = ensure_inventory_config(s3, bucket)
    metrics = MetricsCalculator()

    workloads_out: Dict[str, Any] = {}
    significant_vs_both: List[str] = []
    raw_trials: Dict[str, Any] = {}
    all_put_ms: List[float] = []
    base_prefix = f"full/eval{eval_id}/{started.strftime('%Y%m%dT%H%M%SZ')}"

    for name, patterns in WORKLOADS.items():
        our_costs: List[float] = []
        lc_costs: List[float] = []
        it_costs: List[float] = []
        overheads: List[float] = []
        trial_rows: List[Dict[str, Any]] = []

        for i in range(n_trials):
            trial_seed = (
                seed
                + WORKLOAD_SEED_OFFSET[name]
                + i
                + eval_id * 17
            )
            gen = WorkloadGenerator(seed=trial_seed)
            objects = gen.generate_objects(objects_per_trial, patterns)
            prefix = f"{base_prefix}/{name}/trial-{i:02d}"
            put_ms = put_trial_objects(s3, bucket, prefix, objects)
            all_put_ms.extend(put_ms)
            live_objs = rebuild_from_live(s3, bucket, prefix)
            if len(live_objs) != objects_per_trial:
                raise RuntimeError(
                    f"{name} trial {i}: listed {len(live_objs)} != {objects_per_trial}"
                )
            row = trial_costs_live(live_objs)
            our_costs.append(row["our_cost"])
            lc_costs.append(row["lifecycle_cost"])
            it_costs.append(row["intelligent_tiering_cost"])
            overheads.append(row["overhead_s"])
            trial_rows.append(
                {
                    "trial": i + 1,
                    "seed": trial_seed,
                    "prefix": prefix,
                    "put_ms_mean": (
                        float(sum(put_ms) / len(put_ms)) if put_ms else 0.0
                    ),
                    "n_listed": len(live_objs),
                    "our_cost": row["our_cost"],
                    "lifecycle_cost": row["lifecycle_cost"],
                    "intelligent_tiering_cost": row["intelligent_tiering_cost"],
                    "overhead_s": row["overhead_s"],
                }
            )
            print(
                f"[eval {eval_id}] {name} trial {i + 1}/{n_trials} "
                f"our={row['our_cost']:.6f} lc={row['lifecycle_cost']:.6f} "
                f"it={row['intelligent_tiering_cost']:.6f}",
                flush=True,
            )

        w_lc = metrics.wilcoxon_test(our_costs, lc_costs)
        w_it = metrics.wilcoxon_test(our_costs, it_costs)
        mean_our = float(sum(our_costs) / len(our_costs))
        mean_lc = float(sum(lc_costs) / len(lc_costs))
        mean_it = float(sum(it_costs) / len(it_costs))
        sig_lc = bool(w_lc.get("significant")) and mean_our < mean_lc
        sig_it = bool(w_it.get("significant")) and mean_our < mean_it
        vs_both = sig_lc and sig_it
        if vs_both:
            significant_vs_both.append(name)

        workloads_out[name] = {
            "n_trials": n_trials,
            "objects_per_trial": objects_per_trial,
            "mean_our_cost": mean_our,
            "mean_lifecycle_cost": mean_lc,
            "mean_intelligent_tiering_cost": mean_it,
            "mean_delta_vs_lifecycle": mean_lc - mean_our,
            "mean_delta_vs_intelligent_tiering": mean_it - mean_our,
            "wilcoxon_vs_lifecycle": w_lc,
            "wilcoxon_vs_intelligent_tiering": w_it,
            "mean_overhead_s": (
                float(sum(overheads) / len(overheads)) if overheads else 0.0
            ),
            "significant_cost_cut_vs_both_natives": vs_both,
            "mode": "live_aws",
            "trials": trial_rows,
        }
        raw_trials[name] = {
            "our_costs": our_costs,
            "lifecycle_costs": lc_costs,
            "intelligent_tiering_costs": it_costs,
            "overheads_s": overheads,
        }

    probes = probe_ce_pricing_cw(bucket, log_group, eval_id)
    listing = list_object_metadata(s3, bucket, prefix=base_prefix)
    finished = utc_now()
    summary: Dict[str, Any] = {
        "evaluation": eval_id,
        "round": "live_full",
        "mode": "live_aws",
        "protocol": "three_workload_wilcoxon",
        "collected_at": iso(finished),
        "started_at": iso(started),
        "elapsed_s": (finished - started).total_seconds(),
        "region": REGION,
        "bucket": bucket,
        "log_group": log_group,
        "base_prefix": base_prefix,
        "n_trials_per_workload": n_trials,
        "objects_per_trial": objects_per_trial,
        "object_body_bytes": OBJECT_BYTES,
        "total_objects_put": n_trials * objects_per_trial * len(WORKLOADS),
        "put_ms": {
            "n": len(all_put_ms),
            "mean": float(sum(all_put_ms) / len(all_put_ms)) if all_put_ms else 0.0,
            "min": float(min(all_put_ms)) if all_put_ms else 0.0,
            "max": float(max(all_put_ms)) if all_put_ms else 0.0,
        },
        "s3_inventory": inventory,
        "metadata_path": (
            "ListObjectsV2 + HeadObject user-metadata "
            "(Inventory config set; CSV not awaited)"
        ),
        "workloads": workloads_out,
        "success_workloads_vs_both_natives": significant_vs_both,
        "pricing_api": probes.get("pricing_api"),
        "cost_explorer": probes.get("cost_explorer"),
        "cloudwatch_metrics": probes.get("cloudwatch_metrics"),
        "cloudwatch_logs": probes.get("cloudwatch_logs"),
        "tags_policy": {
            "project": "s3-predictive-optimization",
            "managed_by": "terraform",
            "purpose": "research-eval",
            "data": "synthetic",
        },
        "limitations": [
            "Modeled monthly storage via SavingsEstimator; not CE-settled per-object bills",
            "Destroy-after required; Free-Tier-safe S3/CW/IAM stack",
        ],
        "destroy_after": True,
        "not_lite": True,
        "rebuilt_from_run_log": False,
        "complete_workloads": True,
        "n_listed_under_prefix": len(listing) if listing is not None else None,
    }

    summary_path = out_dir / "summary.json"
    raw_path = out_dir / "raw_costs.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    raw_path.write_text(json.dumps(raw_trials, indent=2) + "\n")
    print(
        json.dumps({"summary": str(summary_path), "raw": str(raw_path)}, indent=2),
        flush=True,
    )
    return summary


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--eval-id", type=int, required=True, help="1..5")
    p.add_argument("--n-trials", type=int, default=10)
    p.add_argument("--objects-per-trial", type=int, default=80)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args(argv)
    if args.eval_id < 1 or args.eval_id > 5:
        print("eval-id must be 1..5", file=sys.stderr)
        return 2
    run_evaluation(args.eval_id, args.n_trials, args.objects_per_trial, args.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
