#!/usr/bin/env python3
"""Refuse a live campaign that would blow the IoT Core monthly free-tier envelope.

    python scripts/assert_free_tier_guard.py --mode dry_run
    python scripts/assert_free_tier_guard.py --mode lite
    python scripts/assert_free_tier_guard.py --mode smoke
    python scripts/assert_free_tier_guard.py --mode formal   # expected BLOCK
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analysis.cost import campaign_operations, load_pricing  # noqa: E402
from common.config import load_experiment, n_cells_for_scale  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--mode",
        choices=("dry_run", "formal", "live_full", "lite", "live_lite", "smoke"),
        default="dry_run",
    )
    args = p.parse_args(argv)
    cfg = load_experiment()
    pricing = load_pricing()
    ft = pricing["free_tier_monthly"]
    limit = int(ft["iot_messages"])

    if args.mode == "dry_run":
        print("cost guard ok: mock dry-run performs zero AWS operations")
        return 0

    scale = {
        "formal": "formal",
        "live_full": "formal",
        "lite": "lite",
        "live_lite": "lite",
        "smoke": "smoke",
    }[args.mode]

    if scale not in cfg:
        print(f"BLOCKED: missing scale '{scale}' in configs/experiment.yaml")
        return 1

    block = cfg[scale]
    n_cells = n_cells_for_scale(cfg, scale)
    ops = campaign_operations(
        int(block["n_devices"]),
        int(block["n_messages"]),
        n_cells,
        qos_share_1=0.5,
    )
    upper = float(ops["iot_messages_upper"])
    print(
        f"{args.mode} scale={scale} n_cells={n_cells} "
        f"iot_messages_upper={upper:.0f} free_tier={limit} "
        f"headroom={limit - upper:.0f} ({100.0 * (limit - upper) / limit:.1f}%)"
    )
    if upper > limit:
        print(f"BLOCKED: {scale} campaign exceeds monthly IoT message free tier")
        print("Do not terraform apply this campaign as-is.")
        return 1
    print(f"cost guard ok for {scale}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
