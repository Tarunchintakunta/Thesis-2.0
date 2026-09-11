#!/usr/bin/env python
"""Cold-start phases: runtime_compare (H1), package_size (H2), memory (H4), combined, and the pilot.

    DATA_MODE=mock python scripts/invoke_idle.py --out data/raw/mock/
    DATA_MODE=live python scripts/invoke_idle.py --phase runtime_compare --reps 50 --out data/raw/live/
    python scripts/invoke_idle.py --config configs/pilot.yaml --out data/pilot/mock/

Each intended-cold call is prepared with a configuration update (force_cold:
update_env) or an idle wait (force_cold: idle), see docs/ASSUMPTIONS.md M2.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coldstart.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(__doc__, {"cold", "idle_probe"}))
