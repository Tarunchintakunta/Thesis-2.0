#!/usr/bin/env python
"""Rebuild lite-round object metadata from committed JSON (no live AWS)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.metadata.collector import from_lite_round, inventory_summary, load_json  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--summary", default=str(ROOT / "results/live/live_lite_summary.json"))
    ap.add_argument("--raw", default=str(ROOT / "results/live/live_lite_raw.json"))
    ap.add_argument("--out", default=str(ROOT / "results/live/lite_metadata.json"))
    args = ap.parse_args(argv)
    summary = load_json(args.summary)
    raw = load_json(args.raw) if Path(args.raw).exists() else {}
    rows = from_lite_round(summary, raw)
    report = {
        "source": "lite_round_reconstructed",
        "live_inventory_job": False,
        "bucket_destroyed": True,
        "bucket": summary.get("bucket"),
        "summary": inventory_summary(rows),
        "objects": rows,
    }
    Path(args.out).write_text(json.dumps(report, indent=2) + "\n")
    print(args.out, inventory_summary(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
