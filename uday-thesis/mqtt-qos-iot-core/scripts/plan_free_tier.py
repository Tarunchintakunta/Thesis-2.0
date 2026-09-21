#!/usr/bin/env python3
"""Estimate formal campaign ops vs Free Tier monthly allowances (planning only)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analysis.cost import campaign_operations, load_pricing  # noqa: E402
from common.config import load_experiment  # noqa: E402


def main() -> int:
    cfg = load_experiment()
    formal = cfg["formal"]
    n_cells = 2 * 4 * 2 * int(formal["replications"])
    ops = campaign_operations(
        n_devices=int(formal["n_devices"]),
        n_messages=int(formal["n_messages"]),
        n_cells=n_cells,
        qos_share_1=0.5,
    )
    pricing = load_pricing()
    ft = pricing["free_tier_monthly"]
    print(
        json.dumps(
            {
                "n_cells": n_cells,
                "ops": ops,
                "free_tier_monthly": ft,
                "iot_messages_exceed_free_tier": ops["iot_messages_upper"] > ft["iot_messages"],
                "note": "Upper-bound planning only; live AWS still blocked.",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
