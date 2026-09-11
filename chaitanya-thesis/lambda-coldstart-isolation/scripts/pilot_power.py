#!/usr/bin/env python
"""Size the main campaign from the pilot and check the idle gap.

    python scripts/pilot_power.py --in data/pilot/live/ --out docs/ANALYSIS_PLAN.md
    python scripts/pilot_power.py --in data/pilot/mock/ --out data/pilot/mock/pilot_power.md

--in is the pilot folder with metrics.csv (make pilot). If --out already has the
pilot-power markers (ANALYSIS_PLAN.md) only that section is replaced. Mock pilot
numbers are never written into the plan unless --allow-mock is given.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coldstart.analysis import load_plan  # noqa: E402
from coldstart.config import load_config  # noqa: E402
from coldstart.power import END, START, pilot_report, replace_section, report_markdown  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", default="configs/experiment.yaml")
    ap.add_argument("--allow-mock", action="store_true")
    args = ap.parse_args(argv)
    src = Path(args.inp)
    src = src / "metrics.csv" if src.is_dir() else src
    m = pd.read_csv(src)
    rep = pilot_report(m, load_plan(), load_config(args.config))
    when = dt.date.today().isoformat()
    section = report_markdown(rep, when)
    out = Path(args.out)
    existing = out.read_text() if out.exists() else ""
    if START in existing and END in existing:
        if "mock" in rep["data_mode"] and not args.allow_mock:
            print("refusing to write a mock pilot into the analysis plan (use another --out)", file=sys.stderr)
            return 2
        out.write_text(replace_section(existing, section))
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("# Pilot power check\n\n" + section)
    (src.parent / "power.json").write_text(json.dumps(rep, indent=2) + "\n")
    print(section)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
