"""Parse AWS S3 Inventory CSV ( Table 1 metadata source).

This is a local parser for already-exported Inventory files. It does not
create an Inventory configuration or call AWS. Live Inventory jobs remain
optional fuller FinOps fields when present."""

from __future__ import annotations

import csv
import io
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

# Canonical destination-report columns (S3 Inventory, ORC/CSV schema subset).
INVENTORY_FIELDS = (
    "bucket",
    "key",
    "version_id",
    "is_latest",
    "is_delete_marker",
    "size",
    "last_modified_date",
    "e_tag",
    "storage_class",
    "is_multipart_uploaded",
    "replication_status",
    "encryption_status",
    "intelligent_tiering_access_tier",
)


def _norm_header(name: str) -> str:
    s = name.strip().lstrip("\ufeff")
    s = re.sub(r"[\s\-]+", "_", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


def parse_inventory_csv(
    source: Union[str, Path],
    *,
    text: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Parse an S3 Inventory CSV from a path or in-memory ``text``.

    Unknown extra columns are retained under their normalised header.
    """
    if text is None:
        raw = Path(source).read_text(encoding="utf-8")
    else:
        raw = text
    reader = csv.DictReader(io.StringIO(raw))
    if reader.fieldnames is None:
        return []
    fieldmap = {_norm_header(h): h for h in reader.fieldnames if h}
    rows: List[Dict[str, Any]] = []
    for rec in reader:
        out: Dict[str, Any] = {"source": "s3_inventory_csv"}
        for canon in INVENTORY_FIELDS:
            orig = fieldmap.get(canon)
            if orig is None:
                continue
            val = rec.get(orig, "")
            if canon == "size" and val not in ("", None):
                try:
                    out[canon] = int(val)
                except ValueError:
                    out[canon] = val
            else:
                out[canon] = val
        for orig in reader.fieldnames:
            if orig is None:
                continue
            key = _norm_header(orig)
            if key not in out:
                out[key] = rec.get(orig, "")
        rows.append(out)
    return rows


def inventory_summary(rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(rows)
    by_class: Dict[str, int] = {}
    total_bytes = 0
    for r in rows:
        sc = str(r.get("storage_class") or "UNKNOWN")
        by_class[sc] = by_class.get(sc, 0) + 1
        size = r.get("size") or 0
        try:
            total_bytes += int(size)
        except (TypeError, ValueError):
            pass
    return {
        "n_objects": len(rows),
        "total_bytes": total_bytes,
        "by_storage_class": by_class,
        "disclaimer": (
            "Parsed Inventory CSV only — not a live S3 Inventory *job* result."
        ),
    }
