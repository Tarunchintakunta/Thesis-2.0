#!/usr/bin/env python3
"""READY_FOR_AWS gate checks for mqtt-qos-iot-core live path.

Gates (all must pass):
  1. Project tags present in terraform default_tags
  2. Destroy hook script exists and invokes terraform destroy

Exit 0 → READY_FOR_AWS gates pass.
Exit 1 → not ready (prints failing gates).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESTROY = ROOT / "scripts" / "destroy_stack.sh"
TF_MAIN = ROOT / "terraform" / "main.tf"
TF_OUT = ROOT / "terraform" / "outputs.tf"


def _tags_ok() -> tuple[bool, str]:
    main = TF_MAIN.read_text(encoding="utf-8") if TF_MAIN.is_file() else ""
    out = TF_OUT.read_text(encoding="utf-8") if TF_OUT.is_file() else ""
    required = ["Project", "Thesis", "Environment", "ManagedBy"]
    ok = all(t in main for t in required) and "default_tags" in main
    detail = "terraform default_tags present" if ok else "missing project default_tags"
    if "Campaign" not in main and "Campaign" not in out:
        ok = False
        detail = "missing Campaign tag"
    return ok, detail


def _destroy_hook_ok() -> tuple[bool, str]:
    if not DESTROY.is_file():
        return False, "scripts/destroy_stack.sh missing"
    text = DESTROY.read_text(encoding="utf-8")
    if "terraform destroy" not in text:
        return False, "destroy hook does not invoke terraform destroy"
    return True, "destroy_stack.sh present"


def main() -> int:
    checks = [
        ("tags", _tags_ok()),
        ("destroy_hook", _destroy_hook_ok()),
    ]
    failed = []
    report = {}
    for name, (ok, detail) in checks:
        report[name] = {"ok": ok, "detail": detail}
        if not ok:
            failed.append(name)

    ready = not failed
    print(
        json.dumps(
            {
                "READY_FOR_AWS": ready,
                "failed_gates": failed,
                "gates": report,
                "allowed_live_scales": ["smoke", "lite"] if ready else [],
            },
            indent=2,
        )
    )
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
