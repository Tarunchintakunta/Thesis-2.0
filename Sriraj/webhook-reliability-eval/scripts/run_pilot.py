#!/usr/bin/env python3
"""CLI wrapper for local pilot."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sim.runner import run_pilot

if __name__ == "__main__":
    out = run_pilot(out_dir=Path(__file__).resolve().parents[1] / "results" / "local_sim")
    print(out.get("written"))
