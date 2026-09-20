#!/usr/bin/env python3
"""Live AWS IoT Core campaign — blocked this pass."""
from __future__ import annotations

import sys

print(
    "BLOCKED: live AWS IoT Core is not part of this pass.\n"
    "Use: python scripts/dry_run.py\n"
    "IaC is ready under terraform/ but must not be applied until a free-tier-safe live fold is authorised."
)
sys.exit(2)
