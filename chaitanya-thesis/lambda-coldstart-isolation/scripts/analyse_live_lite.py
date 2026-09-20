#!/usr/bin/env python
"""Run the pre-registered Holm family on live-lite costs (no new AWS).

    python scripts/analyse_live_lite.py

Maps campaign phase names, drops python-bytecode from H2 when it has no valid
Init samples, and writes figures/tables under figures/live_lite/ and
reports/paper/tables/live_lite/. Lite n and underpowered H3 are disclosed in
hypotheses.json notes — this is not the power-plan n≥30 campaign.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coldstart.analysis import analyse  # noqa: E402
from coldstart.config import load_config  # noqa: E402
from coldstart.live_lite_map import load_live_lite  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in", dest="inp", default="data/processed/live")
    ap.add_argument("--out", nargs=2, metavar=("FIGURES_DIR", "TABLES_DIR"),
                    default=["figures/live_lite", "reports/paper/tables/live_lite"])
    ap.add_argument("--config", default="configs/experiment.yaml")
    args = ap.parse_args(argv)
    costs = load_live_lite(args.inp)
    res = analyse(costs, load_config(args.config), *args.out)
    print(res["label"])
    for k, t in res["tests"].items():
        extra = f"p_holm={t['p_holm']:.4g} reject={t['reject']}" if "p_holm" in t else ""
        print(f"  {k:32s} {t.get('test', ''):22s} p={t.get('p', float('nan')):.4g} {extra}")
    for n in res["notes"]:
        print("  note:", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
