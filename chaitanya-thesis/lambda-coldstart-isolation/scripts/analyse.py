#!/usr/bin/env python
"""Run the pre-registered analysis and write figures, tables and the decision matrix.

    python scripts/analyse.py --in data/processed/mock/ --out figures/mock/ reports/paper/tables/mock/
    python scripts/analyse.py --in data/processed/live/costs.csv --out figures/live/ reports/paper/tables/live/

--in is costs.csv (or a folder that has it). Refuses to mix live and mock rows.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coldstart.analysis import analyse  # noqa: E402
from coldstart.config import load_config  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", nargs=2, required=True, metavar=("FIGURES_DIR", "TABLES_DIR"))
    ap.add_argument("--config", default="configs/experiment.yaml")
    args = ap.parse_args(argv)
    src = Path(args.inp)
    if src.is_dir():
        src = src / "costs.csv"
    if not src.exists():
        print(f"{src} not found - run scripts/cost_model.py first", file=sys.stderr)
        return 2
    res = analyse(pd.read_csv(src), load_config(args.config), *args.out)
    print(res["label"])
    for k, t in res["tests"].items():
        extra = f"p_holm={t['p_holm']:.4g} reject={t['reject']}" if "p_holm" in t else ""
        print(f"  {k:26s} {t.get('test', ''):22s} p={t['p']:.4g} {extra}")
    for n in res["notes"]:
        print("  note:", n)
    print(f"figures: {', '.join(res['figures'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
