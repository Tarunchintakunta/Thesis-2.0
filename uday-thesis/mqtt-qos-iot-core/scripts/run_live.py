#!/usr/bin/env python3
"""Live AWS IoT Core campaign — lite/smoke only when READY_FOR_AWS gates pass.

Default scale is smoke. Always prefer destroy-after.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from analysis.metrics import cell_rows, run_metrics  # noqa: E402
from common.config import load_experiment, specs_from_cfg  # noqa: E402
from simulator.campaign import run_campaign  # noqa: E402

ALLOWED = frozenset({"smoke", "lite"})


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")


def _gates_pass() -> tuple[bool, dict]:
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_ready_for_aws.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    try:
        data = json.loads(r.stdout or "{}")
    except json.JSONDecodeError:
        data = {"raw": r.stdout, "stderr": r.stderr}
    return r.returncode == 0 and bool(data.get("READY_FOR_AWS")), data



def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scale", choices=sorted(ALLOWED), default="smoke")
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "live")
    ap.add_argument(
        "--dry-validate",
        action="store_true",
        help="Check ready gates + expand specs; do not publish to AWS.",
    )
    ap.add_argument(
        "--allow-without-status",
        action="store_true",
        help=argparse.SUPPRESS,  # internal test only
    )
    args = ap.parse_args(argv)

    if args.scale not in ALLOWED:
        print(f"BLOCKED: scale={args.scale} not in {sorted(ALLOWED)}", file=sys.stderr)
        return 2

    # Formal is never accepted even if someone bypasses argparse.
    if args.scale == "formal":
        print("BLOCKED: formal scale not enabled in this runner", file=sys.stderr)
        return 2


    ready, gate_report = _gates_pass()
    if not ready and not args.allow_without_status:
        print(
            "BLOCKED: READY_FOR_AWS gates failed.\n"
            f"{json.dumps(gate_report, indent=2)}\n"
            "Fix tags / destroy hook / cost plan / STATUS latch, then retry.",
            file=sys.stderr,
        )
        return 2

    cfg = load_experiment()
    specs = specs_from_cfg(cfg, scale=args.scale)
    if any(s.backend != "live" for s in specs):
        print("BLOCKED: scale backend is not live", file=sys.stderr)
        return 2

    if args.dry_validate:
        print(
            json.dumps(
                {
                    "dry_validate": True,
                    "READY_FOR_AWS": ready,
                    "scale": args.scale,
                    "n_specs": len(specs),
                    "n_devices": specs[0].n_devices if specs else 0,
                    "n_messages": specs[0].n_messages if specs else 0,
                    "gates": gate_report,
                    "note": "No AWS publish performed.",
                },
                indent=2,
            )
        )
        return 0

    # Live path requires applied stack meta.
    if not (ROOT / ".certs" / "stack_meta.json").is_file():
        print(
            "BLOCKED: missing .certs/stack_meta.json — terraform apply with "
            "enable_apply=true first (lite/smoke device_count).",
            file=sys.stderr,
        )
        return 2

    runs = run_campaign(specs)
    out = args.out
    (out / "manifests").mkdir(parents=True, exist_ok=True)
    (out / "device_log").mkdir(parents=True, exist_ok=True)
    (out / "delivered").mkdir(parents=True, exist_ok=True)

    run_rows = []
    for run in runs:
        rid = run.manifest.run_id
        (out / "manifests" / f"{rid}.json").write_text(
            json.dumps(run.manifest.to_dict(), indent=2, sort_keys=True) + "\n"
        )
        _write_jsonl(out / "device_log" / f"{rid}.jsonl", run.device_log)
        _write_jsonl(out / "delivered" / f"{rid}.jsonl", run.delivered)
        metrics = run_metrics(run)
        slim = {k: v for k, v in metrics.items() if k != "latencies_ms"}
        (out / "manifests" / f"{rid}.metrics.json").write_text(
            json.dumps(slim, indent=2, sort_keys=True) + "\n"
        )
        run_rows.append(metrics)

    cells = cell_rows(run_rows)
    evidence = {
        "scale": args.scale,
        "backend": "live",
        "measurement_kind": "AWS IoT Core rules → Lambda → DynamoDB (live)",
        "n_runs": len(runs),
        "n_cells": len(cells),
        "run_ids": [r.manifest.run_id for r in runs],
        "cells": [
            {k: v for k, v in c.items() if k != "latencies_ms"} for c in cells
        ],
        "gates": gate_report,
        "destroy_required": True,
        "destroy_hook": "scripts/destroy_stack.sh",
    }
    (out / "LIVE_EVIDENCE.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps({k: evidence[k] for k in (
        "scale", "n_runs", "n_cells", "destroy_required", "destroy_hook"
    )}, indent=2))
    print(f"Wrote {out / 'LIVE_EVIDENCE.json'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
