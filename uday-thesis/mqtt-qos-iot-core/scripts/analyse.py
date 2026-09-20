#!/usr/bin/env python3
"""Recompute metrics + Holm–Bonferroni tests from a results directory.

    python scripts/analyse.py --in results/mock --out results/mock/summary
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analysis.metrics import cell_rows  # noqa: E402
from analysis.plot_results import plot_cells  # noqa: E402
from analysis.stats_tests import run_confirmatory  # noqa: E402
from matching.matcher import match_logs  # noqa: E402


def _jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--in", dest="inp", default=str(ROOT / "results" / "mock"))
    p.add_argument("--out", default="")
    args = p.parse_args(argv)
    inp = Path(args.inp)
    out = Path(args.out) if args.out else inp / "summary"
    out.mkdir(parents=True, exist_ok=True)

    run_rows = []
    for man in sorted((inp / "manifests").glob("*.json")):
        if man.name.endswith(".metrics.json"):
            continue
        payload = json.loads(man.read_text())
        run_id = payload["run_id"]
        log = _jsonl(inp / "device_log" / f"{run_id}.jsonl")
        delivered = _jsonl(inp / "delivered" / f"{run_id}.jsonl")
        matched = match_logs(log, delivered)
        spec = payload["spec"]
        metrics_path = man.with_name(f"{run_id}.metrics.json")
        extra = json.loads(metrics_path.read_text()) if metrics_path.exists() else {}
        run_rows.append(
            {
                "run_id": run_id,
                "backend": payload["backend"],
                "measurement_kind": payload["measurement_kind"],
                "qos": spec["qos"],
                "disconnect_s": spec["disconnect_s"],
                "rate_mode": spec["rate_mode"],
                "replication": spec["replication"],
                "cell_id": spec["cell_id"],
                "n_published": matched.n_published,
                "n_lost": matched.n_lost,
                "n_duplicate_ids": matched.n_duplicate_ids,
                "loss_rate": matched.loss_rate,
                "duplicate_id_rate": matched.duplicate_id_rate,
                "latency_mean_ms": matched.latency_mean_ms,
                "latency_p95_ms": matched.latency_p95_ms,
                "latency_p99_ms": matched.latency_p99_ms,
                "latencies_ms": matched.latencies_ms,
                "reconnect_time_ms": extra.get("reconnect_time_ms", 0),
                "backlog_queued": extra.get("backlog_queued", 0),
                "backlog_survived": extra.get("backlog_survived", 0),
                "usd_est": extra.get("usd_est", 0),
            }
        )
    cells = cell_rows(run_rows)
    stats = run_confirmatory(cells, run_rows)
    (out / "stats.json").write_text(json.dumps(stats, indent=2) + "\n")
    if cells:
        with (out / "cells.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(cells[0].keys()))
            w.writeheader()
            w.writerows(cells)
        plot_cells(cells, inp / "figures")
    print(f"analysed {len(run_rows)} runs -> {out}")
    print("If backend=mock, this is not AWS evidence.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
