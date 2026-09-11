#!/usr/bin/env python
"""Write iac/terraform.tfvars.json from config/experiment.yaml and the capacity plan.

    python scripts/render_tfvars.py

Keeps the provisioned-capacity numbers in one place (analysis/design_checks.py
works them out) instead of copying them by hand into Terraform.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.design_checks import capacity_plan, load_config  # noqa: E402


def render(cfg: dict) -> dict:
    cap = capacity_plan(cfg)
    return {
        "region": cfg["region"],
        "table_prefix": cfg["table_prefix"],
        "target_utilisation": cfg["provisioned"]["target_utilisation"],
        "lambda_memory": cfg["driver"]["memory_mb"],
        "provisioned_capacity": {
            row.key_design: {"read_min": int(row.read_min), "read_max": int(row.read_max),
                             "write_min": int(row.write_min), "write_max": int(row.write_max)}
            for row in cap.itertuples()
        },
    }


def main() -> int:
    out = ROOT / "iac/terraform.tfvars.json"
    out.write_text(json.dumps(render(load_config()), indent=2) + "\n")
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
