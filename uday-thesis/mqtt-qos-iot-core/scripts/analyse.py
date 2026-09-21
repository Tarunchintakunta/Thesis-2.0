#!/usr/bin/env python3
"""Analyse loss / dup / latency / cost surface / Holm tests from saved run artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from analysis.metrics import cell_rows  # noqa: E402
from analysis.plot_results import plot_cells  # noqa: E402
from analysis.stats_tests import run_confirmatory  # noqa: E402


def _load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", type=Path, default=ROOT / "results" / "mock")
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "analysis")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--plots", action="store_true")
    args = ap.parse_args()

    manifests = sorted((args.results / "manifests").glob("*.metrics.json"))
    if not manifests:
        # Rebuild metrics from raw logs if only manifests exist.
        raw = sorted(
            p for p in (args.results / "manifests").glob("*.json") if not p.name.endswith(".metrics.json")
        )
        if not raw:
            print("No metrics/manifests found", file=sys.stderr)
            return 1
        sys.path.insert(0, str(SRC))
        from analysis.metrics import run_metrics  # noqa: E402
        from common.models import ReconnectStats  # noqa: E402
        from simulator.campaign import SpecRun  # noqa: E402
        from common.models import RunManifest  # noqa: E402

        run_rows = []
        for mpath in raw:
            man = json.loads(mpath.read_text())
            rid = man["run_id"]
            device_log = _load_jsonl(args.results / "device_log" / f"{rid}.jsonl")
            delivered = _load_jsonl(args.results / "delivered" / f"{rid}.jsonl")
            metrics_path = args.results / "manifests" / f"{rid}.metrics.json"
            if metrics_path.exists():
                row = json.loads(metrics_path.read_text())
                # reattach latencies via matcher
                from matching.matcher import match_logs

                matched = match_logs(device_log, delivered)
                row["latencies_ms"] = matched.latencies_ms
                run_rows.append(row)
            else:
                run = SpecRun(
                    manifest=RunManifest(**{k: man[k] for k in RunManifest.__dataclass_fields__ if k in man}),
                    device_log=device_log,
                    delivered=delivered,
                    reconnect=ReconnectStats(),
                    counters={},
                )
                run_rows.append(run_metrics(run))
    else:
        run_rows = []
        for mp in manifests:
            row = json.loads(mp.read_text())
            rid = row["run_id"]
            device_log = _load_jsonl(args.results / "device_log" / f"{rid}.jsonl")
            delivered = _load_jsonl(args.results / "delivered" / f"{rid}.jsonl")
            from matching.matcher import match_logs

            matched = match_logs(device_log, delivered)
            row["latencies_ms"] = matched.latencies_ms
            if "n_lost" not in row:
                row.update(
                    {
                        "n_published": matched.n_published,
                        "n_lost": matched.n_lost,
                        "n_duplicate_ids": matched.n_duplicate_ids,
                        "loss_rate": matched.loss_rate,
                        "duplicate_id_rate": matched.duplicate_id_rate,
                    }
                )
            run_rows.append(row)

    cells = cell_rows(run_rows)
    args.out.mkdir(parents=True, exist_ok=True)
    cells_out = [{k: v for k, v in c.items() if k != "latencies_ms"} for c in cells]
    (args.out / "cells.json").write_text(json.dumps(cells_out, indent=2) + "\n")
    conf = run_confirmatory(cells, run_rows, alpha=args.alpha)
    (args.out / "confirmatory.json").write_text(json.dumps(conf, indent=2) + "\n")

    if args.plots:
        plot_cells(cells, args.out / "figures", backend=str(run_rows[0].get("backend", "mock")))

    summary = {
        "n_runs": len(run_rows),
        "n_cells": len(cells),
        "adjustment": conf["adjustment"],
        "n_tests": conf["n_tests"],
        "alpha": args.alpha,
        "note": conf["note"],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
