#!/usr/bin/env python3
"""Estimate campaign ops vs Free Tier monthly allowances (planning only).

Prints formal / lite / smoke reconciliation so operators can see headroom
before any terraform apply.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analysis.cost import campaign_operations, load_pricing  # noqa: E402
from common.config import load_experiment, n_cells_for_scale  # noqa: E402


def _block_ops(cfg: dict, scale: str) -> dict:
    block = cfg[scale]
    n_cells = n_cells_for_scale(cfg, scale)
    ops = campaign_operations(
        n_devices=int(block["n_devices"]),
        n_messages=int(block["n_messages"]),
        n_cells=n_cells,
        qos_share_1=0.5,
    )
    return {"n_cells": n_cells, "ops": ops, "block": {
        "n_devices": int(block["n_devices"]),
        "n_messages": int(block["n_messages"]),
        "replications": int(block["replications"]),
        "interval_s": float(block["interval_s"]),
    }}


def main() -> int:
    cfg = load_experiment()
    pricing = load_pricing()
    ft = pricing["free_tier_monthly"]
    limit = int(ft["iot_messages"])

    scales = {}
    for name in ("formal", "lite", "smoke"):
        if name not in cfg:
            continue
        packed = _block_ops(cfg, name)
        upper = float(packed["ops"]["iot_messages_upper"])
        headroom = limit - upper
        scales[name] = {
            **packed["block"],
            "n_cells": packed["n_cells"],
            "ops": packed["ops"],
            "iot_messages_upper": upper,
            "free_tier_iot_messages": limit,
            "exceeds_free_tier": upper > limit,
            "headroom_messages": headroom,
            "headroom_pct": round(100.0 * headroom / limit, 2) if limit else None,
            "usage_pct_of_free_tier": round(100.0 * upper / limit, 2) if limit else None,
        }

    print(
        json.dumps(
            {
                "free_tier_monthly": ft,
                "scales": scales,
                "reconciliation": {
                    "formal_blocked": scales.get("formal", {}).get("exceeds_free_tier", True),
                    "lite_free_tier_safe": not scales.get("lite", {}).get("exceeds_free_tier", True),
                    "smoke_inside_lite_envelope": (
                        scales.get("smoke", {}).get("iot_messages_upper", 0)
                        <= scales.get("lite", {}).get("iot_messages_upper", 0)
                    ),
                    "apply_allowed_scales": [
                        s
                        for s in ("smoke", "lite")
                        if s in scales and not scales[s]["exceeds_free_tier"]
                    ],
                    "note": (
                        "Upper-bound planning only (publishes + QoS1 pubacks). "
                        "Formal exceeds monthly IoT free tier; lite/smoke do not. "
                        "Live apply still requires READY_FOR_AWS gates + destroy-after."
                    ),
                },
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
