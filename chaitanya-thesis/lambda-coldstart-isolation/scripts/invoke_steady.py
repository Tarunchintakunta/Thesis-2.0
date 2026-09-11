#!/usr/bin/env python
"""Warm phases: baseline (Phase A, Bluemke-style duration + cost) and warming (H3).

    DATA_MODE=mock python scripts/invoke_steady.py --out data/raw/mock/
    python scripts/invoke_steady.py --phase baseline --memories 128,512,1024,3008 \\
        --runtime python --variant default --reps 40 --out data/raw/phaseA/
    python scripts/invoke_steady.py --phase warming --warming on,off --duration 2h --out data/raw/phaseB/warming/

The warming phase sends the same Poisson arrivals to warm-target (EventBridge
rule switched on for the run) and warm-control (no rule).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coldstart.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(__doc__, {"warm", "warming"}))
