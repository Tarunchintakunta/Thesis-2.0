#!/usr/bin/env python3
"""Evaluate OPA/Rego category policies on each labelled module. No terraform apply.

Policies are category-level (not per-module). Scoring uses the policy package
that matches the module's labelled category. Variable references are treated as
unknown and are not denied (documented residual-risk / FN case).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.io_util import POLICIES, RESULTS, load_labels, opa_input_for_module  # noqa: E402

PACKAGE_BY_CATEGORY = {
    "public_storage": "data.terraform.public_storage.deny",
    "overpermissive_access": "data.terraform.overpermissive_access.deny",
    "encryption_at_rest": "data.terraform.encryption_at_rest.deny",
    "weak_logging": "data.terraform.weak_logging.deny",
}


def find_opa() -> str:
    env = os.environ.get("OPA_BIN")
    if env:
        return env
    found = shutil.which("opa")
    if found:
        return found
    extra = Path.home() / ".local/bin/opa"
    if extra.exists():
        return str(extra)
    raise SystemExit("opa not found on PATH; set OPA_BIN")


def opa_version(bin_path: str) -> str:
    out = subprocess.check_output([bin_path, "version"], text=True)
    line = out.splitlines()[0]
    return line.replace("Version:", "").strip()


def eval_module(bin_path: str, query: str, inp: dict) -> tuple[list, float]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(inp, fh)
        tmp = fh.name
    try:
        cmd = [
            bin_path,
            "eval",
            "--format",
            "json",
            "-d",
            str(POLICIES),
            "-i",
            tmp,
            query,
        ]
        t0 = time.perf_counter()
        proc = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.perf_counter() - t0
        if proc.returncode != 0:
            return ([f"opa_error:{proc.stderr[:300]}"], elapsed)
        data = json.loads(proc.stdout) if proc.stdout.strip() else {}
        denials = []
        for result in data.get("result") or []:
            for expr in result.get("expressions") or []:
                val = expr.get("value")
                if isinstance(val, list):
                    denials.extend(val)
                elif isinstance(val, dict):
                    denials.extend(val.keys() if val else [])
                elif val:
                    denials.append(val)
        return (denials, elapsed)
    finally:
        Path(tmp).unlink(missing_ok=True)


def main() -> int:
    bin_path = find_opa()
    rows = load_labels()
    verdicts = []
    parse_errors = 0
    for r in rows:
        try:
            inp = opa_input_for_module(r)
        except Exception as exc:  # noqa: BLE001 — record parse failures as FN/unknown
            parse_errors += 1
            verdicts.append(
                {
                    "module_id": r["module_id"],
                    "category": r["category"],
                    "label": r["label"],
                    "predicted": 0,
                    "seconds": 0.0,
                    "denies": [f"hcl_parse_error:{exc}"],
                }
            )
            continue
        query = PACKAGE_BY_CATEGORY[r["category"]]
        denies, elapsed = eval_module(bin_path, query, inp)
        clean = [d for d in denies if not str(d).startswith("opa_error")]
        verdicts.append(
            {
                "module_id": r["module_id"],
                "category": r["category"],
                "label": r["label"],
                "predicted": 1 if clean else 0,
                "seconds": elapsed,
                "denies": [str(d) for d in denies[:12]],
            }
        )
    payload = {
        "tool": "opa",
        "version": opa_version(bin_path),
        "policy_scope": "category_package",
        "n_modules": len(rows),
        "parse_errors": parse_errors,
        "batch_seconds": sum(v["seconds"] for v in verdicts),
        "verdicts": verdicts,
        "sample_times": [
            {
                "module_id": v["module_id"],
                "category": v["category"],
                "label": v["label"],
                "seconds": v["seconds"],
            }
            for v in verdicts
        ],
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "opa_verdicts.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"opa {payload['version']} {payload['batch_seconds']:.1f}s "
        f"flagged {sum(v['predicted'] for v in verdicts)}/{len(verdicts)} "
        f"parse_errors={parse_errors}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
