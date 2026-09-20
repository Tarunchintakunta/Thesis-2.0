"""Map lite campaign phase names onto the pre-registered analysis phases.

Live lite used campaign folder names (`live_python_init`, …). The analysis
plan expects `package_size`, `runtime_compare`, `memory`, and `warming`.
python-bytecode rows stay in the frame but have errors / no Init Duration.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

INIT_PHASES = ("live_python_init", "live_nodejs_init", "live_java_init")
MEMORY_PHASES = ("live_python_memory",)


def _boolish(s: pd.Series) -> pd.Series:
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def map_live_lite(costs: pd.DataFrame, h3: pd.DataFrame | None = None) -> pd.DataFrame:
    """Return a copy with analysis-plan phase names; H1 uses optimised@1024 only."""
    frames = []
    init = costs[costs["phase"].isin(INIT_PHASES)].copy()
    if len(init):
        pkg = init.copy()
        pkg["phase"] = "package_size"
        frames.append(pkg)
        h1 = init[(init["variant"] == "optimised") & (init["memory_mb"].astype(int) == 1024)].copy()
        h1["phase"] = "runtime_compare"
        frames.append(h1)
    mem = costs[costs["phase"].isin(MEMORY_PHASES)].copy()
    if len(mem):
        mem["phase"] = "memory"
        frames.append(mem)
    other = costs[~costs["phase"].isin(INIT_PHASES + MEMORY_PHASES)]
    if len(other):
        frames.append(other)
    if h3 is not None and len(h3):
        frames.append(h3.copy())
    if not frames:
        raise ValueError("no live-lite rows to map")
    out = pd.concat(frames, ignore_index=True)
    for col in ("cold", "error", "intended_cold"):
        if col in out.columns:
            out[col] = _boolish(out[col])
    return out


def load_live_lite(processed: str | Path) -> pd.DataFrame:
    processed = Path(processed)
    costs = pd.read_csv(processed / "costs.csv")
    h3_path = processed / "h3_costs.csv"
    h3 = pd.read_csv(h3_path) if h3_path.exists() else None
    return map_live_lite(costs, h3)
