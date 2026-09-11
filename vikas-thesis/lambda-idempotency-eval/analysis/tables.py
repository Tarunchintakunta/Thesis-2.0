"""Small helpers shared by the report writers (no tabulate dependency)."""
from __future__ import annotations

import math

import pandas as pd

SIGN = "Vikas Reddy Amanagantti"
SOURCE_LABEL = {
    "live": "live AWS measurement",
    "moto": "moto functional check - NOT an AWS measurement (capacity and latency are not AWS numbers)",
    "local": "local run - NOT an AWS measurement",
}


SHORT_LABEL = {"live": "live AWS", "moto": "moto functional check - not AWS data", "local": "local run - not AWS data"}


def source_label(source: str | None) -> str:
    return SOURCE_LABEL.get(source or "", f"{source} - NOT an AWS measurement")


def short_label(source: str | None) -> str:
    """For figure titles, where the long label does not fit."""
    return SHORT_LABEL.get(source or "", f"{source} - not AWS data")


def fmt(v, digits: int = 4) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        return "" if math.isnan(v) else f"{v:.{digits}g}"
    return str(v)


def md_table(df: pd.DataFrame, digits: int = 4) -> str:
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join(fmt(v, digits) for v in row) + " |")
    return "\n".join(lines)
