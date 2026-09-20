#!/usr/bin/env python3
"""Download the minimum-viable Google Cluster Data 2011 subset.

Official source (same objects as gs://clusterdata-2011-2/):
  https://github.com/google/cluster-data
  https://storage.googleapis.com/clusterdata-2011-2/<table>/part-*-of-*.csv.gz

Idempotent: skips files that already exist with the expected size.
Does not start a second copy if a sibling fetch (gsutil .gstmp) is actively growing.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

BUCKET_HTTP = "https://storage.googleapis.com/clusterdata-2011-2"
CANONICAL_REPO = "https://github.com/google/cluster-data"
SCHEMA_DOC = (
    "https://github.com/google/cluster-data/blob/master/ClusterData2011_2.md"
)

# Minimum viable subset (DATA_GAPS.md): ≥1 task_events + ≥1 task_usage + machine_events.
OBJECTS = (
    "machine_events/part-00000-of-00001.csv.gz",
    "task_events/part-00000-of-00500.csv.gz",
    "task_events/part-00001-of-00500.csv.gz",
    "task_usage/part-00000-of-00500.csv.gz",
)

ROOT = Path(__file__).resolve().parents[1] / "data" / "gct" / "2011"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _head_length(url: str) -> int:
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return int(resp.headers["Content-Length"])


def _gstmp_active(dest: Path) -> bool:
    tmp = dest.parent / (dest.name + "_.gstmp")
    if not tmp.exists():
        return False
    size1 = tmp.stat().st_size
    time.sleep(2)
    size2 = tmp.stat().st_size
    return size2 > size1 or size2 > 0


def download_one(rel: str) -> dict:
    url = f"{BUCKET_HTTP}/{rel}"
    dest = ROOT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    expected = _head_length(url)
    rec = {
        "object": rel,
        "url": url,
        "path": str(dest),
        "expected_bytes": expected,
    }
    if dest.exists() and dest.stat().st_size == expected:
        rec["action"] = "skipped_exists"
        rec["sha256"] = _sha256(dest)
        rec["bytes"] = dest.stat().st_size
        return rec
    if _gstmp_active(dest):
        rec["action"] = "deferred_sibling_gsutil"
        return rec

    partial = dest.with_suffix(dest.suffix + ".partial")
    print(f"GET {url} -> {dest} ({expected} bytes)", flush=True)
    urllib.request.urlretrieve(url, partial)
    got = partial.stat().st_size
    if got != expected:
        partial.unlink(missing_ok=True)
        raise RuntimeError(f"size mismatch for {rel}: got {got} expected {expected}")
    partial.replace(dest)
    rec["action"] = "downloaded"
    rec["sha256"] = _sha256(dest)
    rec["bytes"] = got
    return rec


def main() -> int:
    ROOT.mkdir(parents=True, exist_ok=True)
    records = []
    for rel in OBJECTS:
        records.append(download_one(rel))
    manifest = {
        "canonical_repo": CANONICAL_REPO,
        "schema": SCHEMA_DOC,
        "bucket_gs": "gs://clusterdata-2011-2",
        "bucket_http": BUCKET_HTTP,
        "license": "CC-BY 4.0 (Google cluster-data)",
        "trace": "clusterdata-2011-2 (v2.1, ~29 days, May 2011 Borg cell)",
        "files": records,
    }
    prov = ROOT / "DOWNLOAD_PROVENANCE.json"
    prov.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    missing = [
        r["object"]
        for r in records
        if not Path(r["path"]).exists()
        or r.get("bytes", 0) != r.get("expected_bytes")
    ]
    if missing:
        print("INCOMPLETE:", missing, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
