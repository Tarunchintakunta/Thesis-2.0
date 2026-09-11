#!/usr/bin/env python
"""Print synthetic Lambda log lines (START / END / REPORT) for pipeline testing.

    DATA_MODE=mock python scripts/mock_cloudwatch.py --function java-default --memory 512 --n 10
    DATA_MODE=mock python scripts/mock_cloudwatch.py --function python-optimised --n 20 --cold-every 5

*** SYNTHETIC - NOT MEASURED *** The numbers come from configs/mock_model.yaml
placeholders. The script refuses to run with DATA_MODE=live so mock lines can
never be mixed into a live log folder by accident.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coldstart.backends import FUNCTIONS, data_mode  # noqa: E402
from coldstart.mock import MockLambda, VirtualClock  # noqa: E402


def lines(function: str, memory: int, n: int, cold_every: int, seed: int) -> list[str]:
    lam = MockLambda(FUNCTIONS, clock=VirtualClock(), seed=seed)
    lam.set_memory(function, memory)
    out = []
    for i in range(n):
        if cold_every and i % cold_every == 0:
            lam.force_cold(function)
        lam.invoke(function, {"seed": "mock", "iterations": 1})
        lam.clock.advance(5.0)  # long enough for a slow cold start to finish, so the next call can reuse it
    for e in lam.logs:
        out.append(e["message"])
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--function", default="python-optimised", choices=sorted(FUNCTIONS))
    ap.add_argument("--memory", type=int, default=1024)
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--cold-every", type=int, default=0, help="force a cold start every k calls (0 = only the first)")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)
    if data_mode() == "live":
        print("mock_cloudwatch.py only runs with DATA_MODE=mock", file=sys.stderr)
        return 2
    print("# SYNTHETIC mock log lines - not measured")
    for line in lines(args.function, args.memory, args.n, args.cold_every, args.seed):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
