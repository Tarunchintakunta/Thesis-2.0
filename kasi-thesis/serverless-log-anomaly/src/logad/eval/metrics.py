"""Detection metrics on 60 s windows.

* precision / recall / F1 against the injected ground truth (window level)
* per-category F1: that category's anomalous windows + all normal windows
  (false alarms are shared, so categories differ through recall)
* injection level: detected at all? detection delay (first flagged window
  start - injection start, at least 0)
* false-alarm rate on windows known to be normal (phase C = elasticity FAR)
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def prf(pred, label) -> dict:
    pred = np.asarray(pred, dtype=bool)
    label = np.asarray(label, dtype=bool)
    tp = int((pred & label).sum())
    fp = int((pred & ~label).sum())
    fn = int((~pred & label).sum())
    tn = int((~pred & ~label).sum())
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": precision, "recall": recall, "f1": f1}


def false_alarm_rate(pred) -> float:
    pred = np.asarray(pred, dtype=bool)
    return float(pred.mean()) if pred.size else float("nan")


def per_category(pred, label, category) -> dict[str, dict]:
    pred = np.asarray(pred, dtype=bool)
    label = np.asarray(label, dtype=bool)
    category = np.asarray(category, dtype=object)
    out = {}
    for cat in sorted(set(category[label])):
        keep = (~label) | (category == cat)
        out[cat] = prf(pred[keep], label[keep])
    return out


def injection_table(pred, starts, window_s: float, schedule) -> pd.DataFrame:
    """One row per injection: detected, delay_s."""
    pred = np.asarray(pred, dtype=bool)
    starts = np.asarray(starts, dtype=float)
    rows = []
    for inj in schedule:
        lo = int(max(0, np.floor((inj.start - starts[0]) / window_s)))
        hi = int(min(len(starts), np.ceil((inj.end - starts[0]) / window_s)))
        flagged = np.flatnonzero(pred[lo:hi])
        detected = flagged.size > 0
        delay = max(0.0, float(starts[lo + flagged[0]] - inj.start)) if detected else np.nan
        rows.append({"injection_id": inj.injection_id, "block": inj.block, "category": inj.category,
                     "detected": detected, "delay_s": delay})
    return pd.DataFrame(rows)


def window_blocks(starts, schedule) -> np.ndarray:
    """Block of every window: the block of the next injection that has not ended yet
    (gap windows belong to the injection they lead up to); tail -> last block."""
    ends = np.array([inj.end for inj in schedule])
    blocks = np.array([inj.block for inj in schedule])
    pos = np.searchsorted(ends, np.asarray(starts, dtype=float), side="right")
    pos = np.clip(pos, 0, len(schedule) - 1)
    return blocks[pos]


def block_scores(df: pd.DataFrame, pred_col: str) -> pd.DataFrame:
    """F1 (+ per-category F1) per (seed, block) for one detector."""
    rows = []
    for (seed, block), g in df.groupby(["seed", "block"]):
        row = {"seed": seed, "block": block, **{k: v for k, v in prf(g[pred_col], g["label"]).items()
                                                 if k in ("precision", "recall", "f1")}}
        for cat, res in per_category(g[pred_col], g["label"], g["category"]).items():
            row[f"f1_{cat}"] = res["f1"]
        rows.append(row)
    return pd.DataFrame(rows)


def far_blocks(df: pd.DataFrame, pred_col: str, block_s: float = 1800.0) -> pd.DataFrame:
    """Phase C false-alarm rate per (seed, 30 min block)."""
    rows = []
    for seed, g in df.groupby("seed"):
        rel = g["start"] - g["start"].min()
        for blk, gg in g.groupby((rel // block_s).astype(int)):
            rows.append({"seed": seed, "block": int(blk), "far": false_alarm_rate(gg[pred_col])})
    return pd.DataFrame(rows)
