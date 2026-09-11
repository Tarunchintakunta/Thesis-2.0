"""Loghub BGL (Blue Gene/L) sample as the labelled source (Zhu et al., 2023).

Loghub states the datasets are freely available for research / academic work.
The 2k sample is fetched by scripts/fetch_loghub.sh into
data/external/loghub/BGL_2k.log (not committed - see data/external/README.md).

BGL line format:  Label Timestamp Date Node Time NodeRepeat Type Component Level Content
The first field is "-" for a normal line and an alert tag (KERNDTLB, APPSEV ...)
for an anomalous one, so labels come with the data.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from logad.config import PROJECT_ROOT

BGL_PATH = PROJECT_ROOT / "data" / "external" / "loghub" / "BGL_2k.log"
BGL_SHA256 = "2a819ea540909db682005c9cf948387a40729b5c2e9f19d430e29ce704825496"


class SourceMissing(FileNotFoundError):
    pass


@dataclass
class BglLines:
    labels: np.ndarray      # True = alert line
    contents: list[str]


def read_bgl(path: Path = BGL_PATH) -> BglLines:
    if not Path(path).exists():
        raise SourceMissing(f"{path} not found - run scripts/fetch_loghub.sh first")
    labels, contents = [], []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            parts = line.rstrip("\n").split(maxsplit=9)
            if not parts:
                continue
            labels.append(parts[0] != "-")
            contents.append(parts[9] if len(parts) > 9 else "")
    return BglLines(np.asarray(labels, dtype=bool), contents)


def line_windows(n_lines: int, size: int, step: int) -> list[tuple[int, int]]:
    """Fixed-size sliding windows over line positions (BGL has no request structure)."""
    return [(s, s + size) for s in range(0, max(1, n_lines - size + 1), step)]


def window_line_index(n_lines: int, size: int, step: int) -> tuple[np.ndarray, np.ndarray]:
    """(line index, window index) pairs for building window x feature matrices."""
    rows, cols = [], []
    for w, (lo, hi) in enumerate(line_windows(n_lines, size, step)):
        rows.extend(range(lo, hi))
        cols.extend([w] * (hi - lo))
    return np.asarray(rows, dtype=int), np.asarray(cols, dtype=int)


def window_labels(labels, size: int, step: int) -> np.ndarray:
    """A window is anomalous if any of its lines is an alert line."""
    labels = np.asarray(labels, dtype=bool)
    return np.asarray([labels[lo:hi].any() for lo, hi in line_windows(len(labels), size, step)], dtype=bool)
