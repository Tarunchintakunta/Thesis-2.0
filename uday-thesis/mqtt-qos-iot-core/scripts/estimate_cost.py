#!/usr/bin/env python3
"""Estimate campaign cost from published unit prices (not a bill).

    python scripts/estimate_cost.py --mode dry_run
    python scripts/estimate_cost.py --mode formal
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analysis.cost import campaign_operations, estimate_usd, load_pricing  # noqa: E402
from common.config import load_experiment  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("dry_run", "formal"), default="formal")
    args = p.parse_args(argv)
    cfg = load_experiment()
    block = cfg[args.mode]
    qos = list(block["qos"])
    n_cells = len(qos) * len(block["disconnect_s"]) * len(block["rate"]) * int(block["replications"])
    qos1_share = (1.0 / len(qos)) if qos else 0.5
    ops = campaign_operations(int(block["devices"]), int(block["messages"]), n_cells, qos_share_1=qos1_share)
    duration_s = int(block["messages"]) * float(block["interval_s"]) * n_cells
    counters = {
        "publishes_attempted_connected": ops["publishes"],
        "pubacks": ops["pubacks"],
        "rule_invocations": ops["rules_upper"],
        "ddb_puts": ops["ddb_puts_upper"],
    }
    est = estimate_usd(counters, duration_s=duration_s, n_devices=int(block["devices"]))
    pricing = load_pricing()
    ft = pricing["free_tier_monthly"]
    print(f"mode={args.mode}  cells×reps={n_cells}  devices={block['devices']}  msgs={block['messages']}")
    print(f"iot_messages_upper={ops['iot_messages_upper']:.0f}  free_tier_monthly={ft['iot_messages']}")
    print(f"usd_raw={est['usd_raw']:.6f}  usd_with_safety={est['usd_with_safety']:.6f}")
    print("Estimated from published unit prices × counted ops. Not a bill. Free tier ignored in USD.")
    if args.mode == "formal" and ops["iot_messages_upper"] > ft["iot_messages"]:
        print("WARNING: formal live campaign exceeds monthly IoT message free-tier allowance.")
        print("Split across months or run a lite live fold. This pass does not apply AWS.")
    if args.mode == "dry_run":
        print("dry_run is local mock: live AWS cost is $0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
