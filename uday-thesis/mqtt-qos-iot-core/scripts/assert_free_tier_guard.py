#!/usr/bin/env python3
"""Refuse a live campaign that would blow the IoT Core monthly free-tier envelope.

    python scripts/assert_free_tier_guard.py --mode dry_run
    python scripts/assert_free_tier_guard.py --mode formal
    python scripts/assert_free_tier_guard.py --mode live_full   # expected BLOCK
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analysis.cost import campaign_operations, load_pricing  # noqa: E402
from common.config import load_experiment  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("dry_run", "formal", "live_full", "live_lite"), default="dry_run")
    args = p.parse_args(argv)
    cfg = load_experiment()
    pricing = load_pricing()
    ft = pricing["free_tier_monthly"]

    if args.mode == "dry_run":
        print("cost guard ok: mock dry-run performs zero AWS operations")
        return 0

    if args.mode == "live_lite":
        # Suggested later fold: 1 rep, 50 msgs, full 16 cells, 5 devices.
        ops = campaign_operations(5, 50, 16, qos_share_1=0.5)
        print(f"live_lite iot_messages_upper={ops['iot_messages_upper']:.0f} (limit {ft['iot_messages']})")
        if ops["iot_messages_upper"] <= ft["iot_messages"]:
            print("cost guard ok for a *later* lite live fold — not executed this pass")
            return 0
        print("BLOCKED: lite plan still over free tier")
        return 1

    block = cfg["formal"]
    n_cells = 2 * 4 * 2 * int(block["replications"])
    ops = campaign_operations(int(block["devices"]), int(block["messages"]), n_cells, qos_share_1=0.5)
    print(f"{args.mode} iot_messages_upper={ops['iot_messages_upper']:.0f}  free_tier={ft['iot_messages']}")
    if ops["iot_messages_upper"] > ft["iot_messages"]:
        print("BLOCKED: formal 5×1000×16×5 live campaign exceeds monthly IoT message free tier")
        print("Do not terraform apply this campaign as-is.")
        return 1
    print("cost guard ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
