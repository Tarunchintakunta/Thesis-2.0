#!/usr/bin/env python3
"""Record pinned tool versions (rule catalogues change between releases)."""

from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def probe(name: str, args: list[str], extra: str | None = None) -> str:
    bin_path = shutil.which(name) or extra
    if not bin_path or not Path(bin_path).exists():
        return "NOT_FOUND"
    try:
        out = subprocess.check_output(
            [bin_path, *args], text=True, stderr=subprocess.STDOUT
        )
        return out.strip().splitlines()[0]
    except (OSError, subprocess.CalledProcessError) as exc:
        return f"error:{exc}"


def main() -> int:
    payload = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "terraform": probe("terraform", ["version"]),
        "checkov": probe(
            "checkov",
            ["--version"],
            str(Path.home() / "Library/Python/3.14/bin/checkov"),
        ),
        "tfsec": probe("tfsec", ["--version"], str(Path.home() / ".local/bin/tfsec")),
        "opa": probe("opa", ["version"], str(Path.home() / ".local/bin/opa")),
        "note": (
            "Shipped default rule sets. Unpinned versions would make recall "
            "non-repeatable (Verdet et al. 2025; formal CA2)."
        ),
    }
    out = ROOT / "results" / "tool_versions.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
