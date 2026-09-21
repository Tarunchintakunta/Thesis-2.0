#!/usr/bin/env python3
"""Local dry-run campaign: mock broker + in-memory DynamoDB. No AWS calls."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from analysis.metrics import cell_rows, run_metrics  # noqa: E402
from analysis.plot_results import plot_cells  # noqa: E402
from analysis.stats_tests import run_confirmatory  # noqa: E402
from common.config import load_experiment, mock_params, specs_from_cfg  # noqa: E402
from simulator.campaign import run_campaign  # noqa: E402


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scale", default="dry_run", choices=["dry_run"])
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "mock")
    ap.add_argument("--plots", action="store_true")
    args = ap.parse_args()

    cfg = load_experiment()
    specs = specs_from_cfg(cfg, scale=args.scale)
    params = mock_params(cfg)
    runs = run_campaign(specs, params=params)

    out = args.out
    (out / "manifests").mkdir(parents=True, exist_ok=True)
    (out / "device_log").mkdir(parents=True, exist_ok=True)
    (out / "delivered").mkdir(parents=True, exist_ok=True)

    run_rows = []
    for run in runs:
        rid = run.manifest.run_id
        (out / "manifests" / f"{rid}.json").write_text(
            json.dumps(run.manifest.to_dict(), indent=2, sort_keys=True) + "\n"
        )
        _write_jsonl(out / "device_log" / f"{rid}.jsonl", run.device_log)
        _write_jsonl(out / "delivered" / f"{rid}.jsonl", run.delivered)
        metrics = run_metrics(run)
        slim = {k: v for k, v in metrics.items() if k != "latencies_ms"}
        (out / "manifests" / f"{rid}.metrics.json").write_text(
            json.dumps(slim, indent=2, sort_keys=True) + "\n"
        )
        run_rows.append(metrics)

    cells = cell_rows(run_rows)
    analysis_dir = ROOT / "results" / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    cells_out = []
    for c in cells:
        slim = {k: v for k, v in c.items() if k != "latencies_ms"}
        cells_out.append(slim)
    (analysis_dir / "cells_mock.json").write_text(json.dumps(cells_out, indent=2) + "\n")

    conf = run_confirmatory(cells, run_rows, alpha=float(cfg.get("stats", {}).get("alpha", 0.05)))
    (analysis_dir / "confirmatory_mock.json").write_text(json.dumps(conf, indent=2) + "\n")

    if args.plots:
        plot_cells(cells, analysis_dir / "figures", backend="mock")

    print(
        json.dumps(
            {
                "scale": args.scale,
                "n_runs": len(runs),
                "n_cells": len(cells),
                "adjustment": conf["adjustment"],
                "n_tests": conf["n_tests"],
                "out": str(out),
                "note": "MOCK ONLY — not an AWS measurement",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
