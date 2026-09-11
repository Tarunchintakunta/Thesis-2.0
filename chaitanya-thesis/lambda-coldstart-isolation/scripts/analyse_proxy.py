#!/usr/bin/env python
"""Analyse a local init-proxy benchmark run (scripts/local_init_bench.py output).

    python scripts/analyse_proxy.py --in data/proxy/github --out figures/proxy reports/paper/tables/proxy
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coldstart.proxy_analysis import analyse_proxy  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True, help="folder with runs.csv and run_info.json")
    ap.add_argument("--out", nargs=2, required=True, metavar=("FIGURES_DIR", "TABLES_DIR"))
    args = ap.parse_args(argv)
    src = Path(args.inp)
    runs = pd.read_csv(src / "runs.csv")
    info = json.loads((src / "run_info.json").read_text())
    res = analyse_proxy(runs, info, *args.out)
    print(res["label"])
    for k, t in res["tests"].items():
        print(f"  {k:18s} {t['test']:16s} p={t['p']:.3g} p_holm={t['p_holm']:.3g} {t['effect_name']}={t['effect']:.2f}")
    print("figures:", ", ".join(res["figures"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
