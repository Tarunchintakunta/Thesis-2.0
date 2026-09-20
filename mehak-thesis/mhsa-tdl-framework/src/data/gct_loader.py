"""Google Cluster Trace loader (formal CA2).

Does **not** invent data. Raises FileNotFoundError with an exact checklist when
the required GCT files are absent. Synthetic telemetry remains a separate path
(`telemetry_simulator.py`) and must not be used as a silent fallback here.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

# Expected layout documented in mehak-thesis/DATA_GAPS.md
DEFAULT_RELATIVE_ROOT = Path(__file__).resolve().parents[2] / "data" / "gct"

# 2011 Google Cluster Data — minimum parts for a formal join
GCT_2011_REQUIRED_GLOBS = (
    "2011/task_events/part-*-of-*.csv.gz",
    "2011/task_usage/part-*-of-*.csv.gz",
)

GCT_2011_OPTIONAL_GLOBS = (
    "2011/machine_events/part-*-of-*.csv.gz",
    "2011/machine_attributes/part-*-of-*.csv.gz",
    "2011/job_events/part-*-of-*.csv.gz",
)

# 2019 Borg — at least one cell with usage + events
GCT_2019_REQUIRED_GLOBS = (
    "2019/*/instance_usage/*",
    "2019/*/instance_events/*",
)


def resolve_gct_root(explicit: Optional[str] = None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    env = os.environ.get("MHSA_GCT_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return DEFAULT_RELATIVE_ROOT.resolve()


def _expand(root: Path, patterns: Iterable[str]) -> List[Path]:
    found: List[Path] = []
    for pattern in patterns:
        found.extend(sorted(root.glob(pattern)))
    return found


def inventory(root: Optional[Path] = None) -> dict:
    """Return present/missing file inventory for both GCT families."""
    root = root or resolve_gct_root()
    inv = {
        "root": str(root),
        "root_exists": root.is_dir(),
        "2011_required": {p: [str(x) for x in _expand(root, [p])] for p in GCT_2011_REQUIRED_GLOBS},
        "2011_optional": {p: [str(x) for x in _expand(root, [p])] for p in GCT_2011_OPTIONAL_GLOBS},
        "2019_required": {p: [str(x) for x in _expand(root, [p])] for p in GCT_2019_REQUIRED_GLOBS},
    }
    inv["2011_ready"] = all(inv["2011_required"][p] for p in GCT_2011_REQUIRED_GLOBS)
    inv["2019_ready"] = all(inv["2019_required"][p] for p in GCT_2019_REQUIRED_GLOBS)
    inv["any_ready"] = bool(inv["2011_ready"] or inv["2019_ready"])
    return inv


def missing_checklist(root: Optional[Path] = None) -> str:
    inv = inventory(root)
    lines = [
        "Google Cluster Trace data is missing for formal CA2 evaluation.",
        f"Looked under: {inv['root']}",
        "See mehak-thesis/DATA_GAPS.md for canonical download locations.",
        "",
        "Required (either family):",
    ]
    if not inv["2011_ready"]:
        lines.append("  [2011] missing:")
        for pattern, hits in inv["2011_required"].items():
            if not hits:
                lines.append(f"    - {pattern}")
    if not inv["2019_ready"]:
        lines.append("  [2019] missing:")
        for pattern, hits in inv["2019_required"].items():
            if not hits:
                lines.append(f"    - {pattern}")
    return "\n".join(lines)


def require_gct(root: Optional[str] = None) -> Path:
    """Raise if no usable GCT subset is present. Returns resolved root when ready."""
    resolved = resolve_gct_root(root)
    inv = inventory(resolved)
    if not inv["any_ready"]:
        raise FileNotFoundError(missing_checklist(resolved))
    return resolved


def load_gct_windows(
    root: Optional[str] = None,
    seq_length: int = 10,
    horizon: int = 5,
) -> Tuple:
    """Load GCT → (X, y, meta).

    Not implemented until DATA_GAPS files are present. Calling this without data
    always raises FileNotFoundError (never fabricates windows).
    """
    resolved = require_gct(root)
    inv = inventory(resolved)
    # Plumbing only: refuse to invent feature/label tensors even if files exist
    # until a reviewed join/label script is added. Presence check is the gate.
    raise NotImplementedError(
        "GCT files detected under "
        f"{resolved} (2011_ready={inv['2011_ready']}, 2019_ready={inv['2019_ready']}), "
        "but windowing/label join is not yet implemented. "
        "Do not substitute synthetic labels. Extend this loader with an evidence-reviewed "
        "task_usage↔task_events (or 2019 instance_usage↔instance_events) join before training."
    )


if __name__ == "__main__":
    try:
        require_gct()
        print("GCT present; window loader still TODO.")
    except FileNotFoundError as exc:
        print(exc)
        raise SystemExit(2)
