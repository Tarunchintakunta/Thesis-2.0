"""Metadata collection: live-lite JSON + Inventory CSV + Boto3 listing.

Formal CA2 Table 1 names Boto3 + S3 Inventory + CloudWatch. This package
implements those *modules* against committed evidence or injected clients.
It does not invent Inventory-job output or CE-settled campaign savings.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .boto3_collector import list_object_metadata, metadata_report_from_listing
from .inventory_csv import inventory_summary, parse_inventory_csv

DEFAULT_SUMMARY = (
    Path(__file__).resolve().parents[2]
    / "results"
    / "live"
    / "live_lite_summary.json"
)
DEFAULT_RAW = (
    Path(__file__).resolve().parents[2] / "results" / "live" / "live_lite_raw.json"
)


def load_lite_summary(path: Optional[Path] = None) -> Dict[str, Any]:
    p = Path(path) if path else DEFAULT_SUMMARY
    with open(p) as f:
        return json.load(f)


def load_lite_raw(path: Optional[Path] = None) -> Any:
    p = Path(path) if path else DEFAULT_RAW
    with open(p) as f:
        return json.load(f)


def inventory_from_lite(summary: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Object-level inventory view derived from lite sample_objects (not S3 Inventory)."""
    summary = summary or load_lite_summary()
    samples = (summary.get("s3") or {}).get("sample_objects") or []
    rows: List[Dict[str, Any]] = []
    for s in samples:
        rows.append(
            {
                "key_standard": s.get("key_standard"),
                "key_ia": s.get("key_ia"),
                "size_bytes": s.get("size_bytes"),
                "storage_class_standard": s.get("storage_class_standard"),
                "storage_class_ia": s.get("storage_class_ia"),
                "source": "live_lite_summary.sample_objects",
                "note": "Not AWS S3 Inventory CSV — lite probe objects only",
            }
        )
    return rows


def metadata_report(summary: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    summary = summary or load_lite_summary()
    s3 = summary.get("s3") or {}
    return {
        "round": summary.get("round"),
        "region": summary.get("region"),
        "bucket": summary.get("bucket"),
        "objects_per_arm": s3.get("objects_per_arm"),
        "listed_key_count": s3.get("listed_key_count"),
        "inventory_rows": len(inventory_from_lite(summary)),
        "wilcoxon": summary.get("wilcoxon") or summary.get("stats"),
        "cost_explorer_probe": summary.get("cost_explorer") or summary.get("ce"),
        "cloudwatch": summary.get("cloudwatch") or summary.get("cw"),
        "disclaimer": (
            "Parses live-lite evidence only. Inventory CSV / Boto3 listing "
            "are separate helpers; they do not close CE-settled campaign savings."
        ),
    }


__all__ = [
    "inventory_from_lite",
    "inventory_summary",
    "list_object_metadata",
    "load_lite_raw",
    "load_lite_summary",
    "metadata_report",
    "metadata_report_from_listing",
    "parse_inventory_csv",
]


if __name__ == "__main__":
    print(json.dumps(metadata_report(), indent=2, default=str))
