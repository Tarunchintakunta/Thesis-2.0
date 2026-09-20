"""S3 object metadata collection.

Live path uses Boto3 ListObjectsV2 (optional Inventory CSV). Offline path
rebuilds the destroyed lite-round object table from committed live_lite JSON.
A live Inventory *job* was never enabled; do not claim it was.
"""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


FEATURE_FIELDS = (
    "key", "size_bytes", "size_kb", "size_mb", "storage_class",
    "age_days", "last_access_days", "access_frequency", "current_storage_class",
)


def _size_fields(size_bytes: int) -> dict:
    size_bytes = int(size_bytes)
    return {
        "size_bytes": size_bytes,
        "size_kb": round(size_bytes / 1024, 4),
        "size_mb": round(size_bytes / (1024 * 1024), 6),
    }


def from_inventory_csv(text: str, collected_at: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """Parse an S3 Inventory CSV (bucket,key,size,last_modified_date,storage_class, …)."""
    now = collected_at or datetime.now(timezone.utc)
    rows = []
    reader = csv.DictReader(io.StringIO(text))
    for r in reader:
        key = r.get("key") or r.get("Key") or r.get("object_key")
        if not key:
            continue
        size = int(float(r.get("size") or r.get("Size") or 0))
        storage = (r.get("storage_class") or r.get("StorageClass") or "STANDARD").upper()
        last_mod = r.get("last_modified_date") or r.get("LastModifiedDate") or ""
        age_days = 0
        if last_mod:
            try:
                ts = datetime.fromisoformat(last_mod.replace("Z", "+00:00"))
                age_days = max(0, int((now - ts).total_seconds() // 86400))
            except ValueError:
                age_days = 0
        rec = {
            "key": key,
            "storage_class": storage,
            "current_storage_class": storage,
            "age_days": age_days,
            "last_access_days": age_days,
            "access_frequency": 0,
            "source": "inventory_csv",
            **_size_fields(size),
        }
        rows.append(rec)
    return rows


def from_list_objects(client, bucket: str, prefix: str = "") -> List[Dict[str, Any]]:
    """Live ListObjectsV2. Not executed in the committed lite round after destroy."""
    paginator = client.get_paginator("list_objects_v2")
    now = datetime.now(timezone.utc)
    rows = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents") or []:
            last = obj["LastModified"]
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            age_days = max(0, int((now - last).total_seconds() // 86400))
            storage = str(obj.get("StorageClass") or "STANDARD").upper()
            rows.append({
                "key": obj["Key"],
                "storage_class": storage,
                "current_storage_class": storage,
                "age_days": age_days,
                "last_access_days": age_days,
                "access_frequency": 0,
                "etag": obj.get("ETag"),
                "source": "list_objects_v2",
                **_size_fields(int(obj["Size"])),
            })
    return rows


def from_lite_round(summary: dict, raw: Optional[dict] = None) -> List[Dict[str, Any]]:
    """Rebuild the 48-object lite table from committed live_lite JSON (bucket destroyed)."""
    s3 = summary.get("s3") or {}
    n = int(s3.get("objects_per_arm") or 0)
    size = int(s3.get("object_bytes") or 0)
    prefix = s3.get("prefix") or ""
    collected = summary.get("collected_at")
    samples = (s3.get("sample_objects") or []) + ((raw or {}).get("sample_objects") or [])
    by_idx: dict[int, dict] = {}
    for samp in samples:
        for kind, field in (("std", "key_standard"), ("ia", "key_ia")):
            key = samp.get(field)
            if not key:
                continue
            try:
                idx = int(Path(key).stem.split("-")[-1])
            except ValueError:
                continue
            by_idx.setdefault(idx, {})[kind] = samp
    rows = []
    for i in range(n):
        samp = by_idx.get(i, {})
        std_s = samp.get("std") or {}
        ia_s = samp.get("ia") or {}
        std_key = std_s.get("key_standard") or f"{prefix}std/obj-{i:03d}.bin"
        ia_key = ia_s.get("key_ia") or f"{prefix}ia/obj-{i:03d}.bin"
        std_size = int(std_s.get("size_bytes") or size)
        ia_size = int(ia_s.get("size_bytes") or size)
        rows.append({
            "key": std_key,
            "storage_class": "STANDARD",
            "current_storage_class": "STANDARD",
            "age_days": 0,
            "last_access_days": 0,
            "access_frequency": 0,
            "source": "lite_round_reconstructed",
            "collected_at": collected,
            **_size_fields(std_size),
        })
        rows.append({
            "key": ia_key,
            "storage_class": "STANDARD_IA",
            "current_storage_class": "STANDARD_IA",
            "age_days": 0,
            "last_access_days": 0,
            "access_frequency": 0,
            "source": "lite_round_reconstructed",
            "collected_at": collected,
            **_size_fields(ia_size),
        })
    return rows


def inventory_summary(rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(rows)
    dist: dict[str, int] = {}
    bytes_by: dict[str, int] = {}
    for r in rows:
        sc = r.get("storage_class") or "STANDARD"
        dist[sc] = dist.get(sc, 0) + 1
        bytes_by[sc] = bytes_by.get(sc, 0) + int(r.get("size_bytes") or 0)
    return {
        "n_objects": len(rows),
        "storage_class_counts": dist,
        "bytes_by_class": bytes_by,
        "total_bytes": sum(bytes_by.values()),
        "sources": sorted({r.get("source") for r in rows if r.get("source")}),
    }


def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())
