#!/usr/bin/env python
"""Join invocation records and REPORT lines into the processed dataset.

    python scripts/parse_report_metrics.py --in data/raw/mock/ --out data/processed/mock/metrics.csv

--in is the raw folder (one sub-folder per phase + logs_collected/events.jsonl).
Output: metrics.csv (or .parquet if the name ends with .parquet and pyarrow is
installed) and discarded_intended_colds.csv next to it. Schema: docs/DATASET.md.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coldstart.config import load_config  # noqa: E402
from coldstart.logs import read_events  # noqa: E402
from coldstart.metrics import (  # noqa: E402
    build_metrics,
    discarded_intended_colds,
    load_invocations,
    reports_frame,
)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", default="configs/experiment.yaml")
    args = ap.parse_args(argv)
    raw = Path(args.inp)
    cfg = load_config(args.config)

    inv = load_invocations(raw)
    if inv.empty:
        print(f"no invocations.jsonl under {raw}", file=sys.stderr)
        return 2
    events_path = raw / "logs_collected" / "events.jsonl"
    events = read_events([events_path]) if events_path.exists() else []
    if not events:
        print("no collected logs - using the REPORT lines from the invoke log tail only")
    m = build_metrics(inv, reports_frame(events, cfg["stack_name"]))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix == ".parquet":
        m.to_parquet(out, index=False)
    else:
        m.to_csv(out, index=False)
    disc = discarded_intended_colds(m)
    disc.to_csv(out.parent / "discarded_intended_colds.csv", index=False)
    modes = sorted(m["data_mode"].dropna().unique())
    print(f"{len(m)} rows ({(m['role'] == 'measure').sum()} measure, "
          f"{(m['role'] == 'warmer_ping').sum()} warmer pings) data_mode={modes} -> {out}")
    print(f"report source: {m['report_source'].value_counts().to_dict()}")
    print(f"intended-cold calls that came back warm: {int(disc['came_back_warm'].sum())} "
          f"of {int(disc['intended_cold'].sum())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
