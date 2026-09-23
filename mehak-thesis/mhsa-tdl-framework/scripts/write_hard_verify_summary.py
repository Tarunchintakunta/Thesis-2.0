#!/usr/bin/env python3
"""Write hard_verify_summary.json from results_summary.csv (or run.log fallback).

Usage:
  python3 scripts/write_hard_verify_summary.py results/gct/hard_verify_1
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

METRICS = ("Accuracy", "Precision", "Recall", "Macro-F1", "ROC-AUC", "Fail-F1")


def _from_csv(path: Path) -> dict[str, dict[str, float]]:
    s = pd.read_csv(path, index_col=0, header=[0, 1])

    def m(model: str, col: str) -> float:
        return float(s.loc[model, (col, "mean")])

    out: dict[str, dict[str, float]] = {}
    for model in ("MHSA-Fused", "Aldomi GRU-RF", "RF (classical)"):
        out[model] = {col: m(model, col) for col in METRICS}
    return out


def _from_run_log(path: Path) -> dict[str, dict[str, float]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    idx = text.rfind("Summary across seeds")
    if idx < 0:
        raise SystemExit(f"no Summary across seeds in {path}")
    block = text[idx:]
    end = block.find("Results saved")
    if end > 0:
        block = block[:end]
    rows: dict[str, dict[str, float]] = {}
    pat = re.compile(
        r"^(Aldomi GRU-KNN|Aldomi GRU-RF|KNN \(classical\)|MHSA-Fused|"
        r"MHSA-PerHead|RF \(classical\)|SVM \(classical\)|Threshold Baseline)\s+(.*)$"
    )
    for line in block.splitlines():
        m = pat.match(line.rstrip())
        if not m:
            continue
        name = m.group(1)
        nums: list[float] = []
        for tok in m.group(2).split():
            try:
                nums.append(float(tok))
            except ValueError:
                pass
        if len(nums) < 18:
            continue
        rows[name] = {
            "Accuracy": nums[0],
            "Precision": nums[2],
            "Recall": nums[4],
            "Macro-F1": nums[6],
            "ROC-AUC": nums[8],
            "Fail-F1": nums[16],
        }
    need = ("MHSA-Fused", "Aldomi GRU-RF", "RF (classical)")
    missing = [n for n in need if n not in rows]
    if missing:
        raise SystemExit(f"run.log missing models {missing}")
    return {n: rows[n] for n in need}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    out = Path(sys.argv[1])
    csv_path = out / "results_summary.csv"
    if csv_path.exists():
        models = _from_csv(csv_path)
        source = "results_summary.csv"
    else:
        models = _from_run_log(out / "run.log")
        source = "run.log"
    mhsa = models["MHSA-Fused"]
    ald = models["Aldomi GRU-RF"]
    rf = models["RF (classical)"]
    payload = {
        "round": out.name,
        "mhsa_fused": mhsa,
        "aldomi_gru_rf": ald,
        "rf": rf,
        "mhsa_beats_aldomi_acc": bool(mhsa["Accuracy"] > ald["Accuracy"]),
        "mhsa_beats_rf_acc": bool(mhsa["Accuracy"] > rf["Accuracy"]),
        "same_metrics_present": all(mhsa.get(k) is not None for k in METRICS[:5]),
        "source": source,
    }
    (out / "hard_verify_summary.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
