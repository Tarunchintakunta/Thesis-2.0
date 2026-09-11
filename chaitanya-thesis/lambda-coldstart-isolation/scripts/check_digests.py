#!/usr/bin/env python
"""Runtime gate: every built variant returns the same digest for payloads/fixed_payload.json.

    python scripts/check_digests.py                         # check whatever is built
    python scripts/check_digests.py --require python,nodejs,java
    python scripts/check_digests.py --write-expected        # refresh payloads/expected_output.json

The reference is the Python optimised handler run in-process. Exit 1 if a
built variant disagrees or a required runtime is missing.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coldstart import localbench  # noqa: E402

EXPECTED = ROOT / "payloads" / "expected_output.json"


def reference_output() -> dict:
    spec = importlib.util.spec_from_file_location("ref_handler", ROOT / "functions/python/optimised/handler.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.lambda_handler(json.loads(localbench.PAYLOAD.read_text()))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--require", default="")
    ap.add_argument("--write-expected", action="store_true")
    args = ap.parse_args(argv)

    ref = reference_output()
    if args.write_expected:
        EXPECTED.write_text(json.dumps(ref, indent=2) + "\n")
        print("wrote", EXPECTED.relative_to(ROOT))
    expected = json.loads(EXPECTED.read_text())
    if ref != expected:
        print("reference handler no longer matches expected_output.json", file=sys.stderr)
        return 1

    required = {r for r in args.require.split(",") if r}
    bad = 0
    for runtime, variant in localbench.VARIANTS:
        name = f"{runtime}-{variant}"
        if not localbench.is_built(runtime, variant):
            status = "MISSING (required)" if runtime in required else "skipped (not built)"
            bad += runtime in required
            print(f"{name:18s} {status}")
            continue
        row = localbench.run_once(runtime, variant)
        same = row.get("ok") and row["digest"] == expected["digest"] and row["items_total"] == expected["items_total"]
        bad += not same
        print(f"{name:18s} {'OK' if same else 'DIFFERENT'}  {row.get('digest', row.get('error', ''))[:64]}")
    print("runtime gate:", "PASS" if bad == 0 else "FAIL")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
