#!/usr/bin/env python3
"""READY_FOR_AWS gate checks for mqtt-qos-iot-core lite/smoke live path.

Gates (all must pass):
  1. Project tags present in terraform default_tags / outputs
  2. Destroy hook script exists and is executable-capable
  3. Free-tier cost plan: lite + smoke under monthly IoT message budget; formal blocked
  4. STATUS.md declares READY_FOR_AWS: YES (operator latch)

Exit 0 → READY_FOR_AWS gates pass.
Exit 1 → not ready (prints failing gates).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "STATUS.md"
DESTROY = ROOT / "scripts" / "destroy_stack.sh"
TF_MAIN = ROOT / "terraform" / "main.tf"
TF_OUT = ROOT / "terraform" / "outputs.tf"


def _status_ready() -> tuple[bool, str]:
    text = STATUS.read_text(encoding="utf-8") if STATUS.is_file() else ""
    # Accept **YES** or YES after READY_FOR_AWS
    m = re.search(r"READY_FOR_AWS[:\*]*\s*\**\s*(YES|NO)\**", text, re.I)
    if not m:
        return False, "STATUS.md missing READY_FOR_AWS line"
    val = m.group(1).upper()
    return val == "YES", f"STATUS READY_FOR_AWS={val}"


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


def _cost_plan_ok() -> tuple[bool, str]:
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "plan_free_tier.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    if r.returncode != 0:
        return False, f"plan_free_tier.py failed: {r.stderr.strip()}"
    data = json.loads(r.stdout)
    recon = data.get("reconciliation") or {}
    lite_ok = bool(recon.get("lite_free_tier_safe"))
    formal_blocked = bool(recon.get("formal_blocked"))
    smoke_ok = bool(recon.get("smoke_inside_lite_envelope"))
    if lite_ok and formal_blocked and smoke_ok:
        lite = (data.get("scales") or {}).get("lite") or {}
        return True, (
            f"lite upper={lite.get('iot_messages_upper')} "
            f"headroom_pct={lite.get('headroom_pct')} formal_blocked={formal_blocked}"
        )
    return False, f"cost reconciliation failed: {recon}"


def main() -> int:
    checks = [
        ("tags", _tags_ok()),
        ("destroy_hook", _destroy_hook_ok()),
        ("cost_plan", _cost_plan_ok()),
        ("status_latch", _status_ready()),
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
                "formal_live": "blocked (free tier)",
            },
            indent=2,
        )
    )
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
