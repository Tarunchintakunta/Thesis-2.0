"""Boto3 per-object metadata collector (CA2 Table 1 module 1).

Client is injected so unit tests can use moto without live AWS. Default
construction uses boto3 only when the caller asks. This module never
creates buckets or writes objects.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _iso(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    return str(value)


def list_object_metadata(
    s3_client: Any,
    bucket: str,
    prefix: str = "",
    max_keys: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """List object metadata via ListObjectsV2 (paginated).

    Returns per-object size, storage class, last-modified, ETag, key.
    Does not fetch body bytes.
    """
    kwargs: Dict[str, Any] = {"Bucket": bucket}
    if prefix:
        kwargs["Prefix"] = prefix
    rows: List[Dict[str, Any]] = []
    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(**kwargs):
        for obj in page.get("Contents") or []:
            rows.append(
                {
                    "key": obj.get("Key"),
                    "size": int(obj.get("Size") or 0),
                    "storage_class": obj.get("StorageClass") or "STANDARD",
                    "last_modified": _iso(obj.get("LastModified")),
                    "etag": (obj.get("ETag") or "").strip('"'),
                    "source": "boto3.list_objects_v2",
                }
            )
            if max_keys is not None and len(rows) >= max_keys:
                return rows
    return rows


def metadata_report_from_listing(
    rows: List[Dict[str, Any]],
    *,
    bucket: str,
    region: Optional[str] = None,
) -> Dict[str, Any]:
    by_class: Dict[str, int] = {}
    total = 0
    for r in rows:
        sc = str(r.get("storage_class") or "STANDARD")
        by_class[sc] = by_class.get(sc, 0) + 1
        total += int(r.get("size") or 0)
    return {
        "bucket": bucket,
        "region": region,
        "n_objects": len(rows),
        "total_bytes": total,
        "by_storage_class": by_class,
        "objects": rows,
        "disclaimer": (
            "ListObjectsV2 metadata only. Not S3 Inventory CSV and not "
            "Cost-Explorer settled savings."
        ),
    }
