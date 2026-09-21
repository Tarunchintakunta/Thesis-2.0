#!/usr/bin/env python3
"""Live AWS IoT Core campaign entrypoint — intentionally BLOCKED this pass."""

from __future__ import annotations

import sys


def main() -> int:
    print(
        "BLOCKED: live AWS IoT Core campaign is not enabled in this pass.\n"
        "Formal CA2 requires AWS, but STATUS.md states live AWS has not been applied yet.\n"
        "Use scripts/run_dry_run.py for the local mock harness (no AWS credentials needed).\n"
        "Unblock only after READY_FOR_AWS and an explicit operator decision.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
