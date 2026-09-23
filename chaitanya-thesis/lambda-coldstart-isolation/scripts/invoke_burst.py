#!/usr/bin/env python
"""Burst phase: N concurrent calls from a quiet state, per runtime.

    DATA_MODE=mock python scripts/invoke_burst.py --out data/raw/mock/
    DATA_MODE=live python scripts/invoke_burst.py --phase burst --out data/raw/phaseB/burst/

Concurrency stays at 20 so the run is far below the default account limit
.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coldstart.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(__doc__, {"burst"}))
