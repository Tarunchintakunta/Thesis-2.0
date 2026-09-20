#!/usr/bin/env python3
"""Local mock dry-run of the MQTT QoS factorial (no AWS).

    python scripts/dry_run.py
    python scripts/dry_run.py --out results/mock --scale dry_run
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analysis.metrics import cell_rows, run_metrics  # noqa: E402
from analysis.plot_results import plot_cells  # noqa: E402
from analysis.stats_tests import run_confirmatory  # noqa: E402
from common.config import load_experiment, mock_params, specs_from_cfg  # noqa: E402
from simulator.campaign import run_campaign  # noqa: E402


BANNER = (
    "MOCK DRY-RUN — not AWS IoT Core evidence. "
    "Device-side ID log + in-memory DynamoDB matcher only."
)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default=str(ROOT / "results" / "mock"))
    p.add_argument("--scale", choices=("dry_run", "formal"), default="dry_run")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args(argv)

    cfg = load_experiment()
    specs = specs_from_cfg(cfg, args.scale)
    params = mock_params(cfg)
    out = Path(args.out)
    (out / "manifests").mkdir(parents=True, exist_ok=True)
    if not args.quiet:
        print(BANNER)
        print(f"cells×reps={len(specs)}  devices={specs[0].n_devices}  msgs={specs[0].n_messages}  backend=mock")

    runs = run_campaign(specs, params=params)
    run_rows = []
    for run in runs:
        mid = run.manifest.run_id
        (out / "manifests" / f"{mid}.json").write_text(json.dumps(run.manifest.to_dict(), indent=2) + "\n")
        _write_jsonl(out / "device_log" / f"{mid}.jsonl", run.device_log)
        _write_jsonl(out / "delivered" / f"{mid}.jsonl", run.delivered)
        metrics = run_metrics(run)
        slim = {k: v for k, v in metrics.items() if k not in ("latencies_ms", "counters")}
        slim["counters"] = run.counters
        run_rows.append(metrics)
        (out / "manifests" / f"{mid}.metrics.json").write_text(json.dumps(slim, indent=2) + "\n")

    cells = cell_rows(run_rows)
    import csv

    def _write_csv(path: Path, rows: list[dict], drop: tuple[str, ...] = ()) -> None:
        if not rows:
            return
        keys = [k for k in rows[0] if k not in drop]
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            for row in rows:
                w.writerow({k: row.get(k) for k in keys})

    _write_csv(out / "runs.csv", run_rows, drop=("latencies_ms", "counters"))
    _write_csv(out / "cells.csv", cells)

    stats = run_confirmatory(cells, run_rows, alpha=0.05)
    summary_dir = out / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    (summary_dir / "stats.json").write_text(json.dumps(stats, indent=2) + "\n")
    figs = plot_cells(cells, out / "figures")

    (out / "HARNESS_PROOF.json").write_text(
        json.dumps(
            {
                "measurement_kind": BANNER,
                "n_runs": len(runs),
                "n_cells": len(cells),
                "n_published_total": sum(r["n_published"] for r in run_rows),
                "figures": [str(p.relative_to(out)) for p in figs],
                "aws_applied": False,
            },
            indent=2,
        )
        + "\n"
    )
    if not args.quiet:
        print(f"wrote {out}")
        print(f"published={sum(r['n_published'] for r in run_rows)}  lost={sum(r['n_lost'] for r in run_rows)}")
        print("NOT live AWS. See results/README.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
