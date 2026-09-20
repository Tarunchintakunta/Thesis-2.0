#!/usr/bin/env python3
"""Generate corpus, run scanners + OPA + checklist, write metrics. No apply."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run(script: str) -> None:
    cmd = [sys.executable, str(SCRIPTS / script)]
    print("+", " ".join(cmd), flush=True)
    subprocess.check_call(cmd, cwd=str(ROOT))


def main() -> int:
    run("generate_corpus.py")
    run("run_checklist.py")
    run("run_checkov.py")
    run("run_tfsec.py")
    run("run_opa.py")
    run("evaluate.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
