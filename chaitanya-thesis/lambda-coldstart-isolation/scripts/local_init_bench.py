#!/usr/bin/env python
"""Run the local process-start (init proxy) benchmark over every built variant.

    python scripts/local_init_bench.py --reps 30 --out data/proxy/local
    python scripts/local_init_bench.py --reps 3 --only python --out /tmp/bench_smoke

Needs `bash scripts/package_all.sh` first. Writes runs.csv + run_info.json.
This is a PROXY measurement (see src/coldstart/localbench.py), never a Lambda Init Duration.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coldstart import localbench  # noqa: E402
from coldstart.packaging import build_manifest  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--warmup", type=int, default=2)
    ap.add_argument("--only", default="", help="comma list of runtimes, e.g. python,nodejs")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    only = {r for r in args.only.split(",") if r}
    variants = [v for v in localbench.VARIANTS if localbench.is_built(*v) and (not only or v[0] in only)]
    if not variants:
        print("nothing built - run bash scripts/package_all.sh first", file=sys.stderr)
        return 2
    print("variants:", ", ".join(f"{r}-{v}" for r, v in variants))

    started = dt.datetime.now(dt.timezone.utc)
    total = args.reps * len(variants)

    def progress(seq, row):
        if (seq + 1) % max(1, total // 10) == 0 or seq + 1 == total:
            print(f"  {seq + 1}/{total}")

    rows = localbench.run_benchmark(args.reps, variants, seed=args.seed, warmup=args.warmup, progress=progress)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out / "runs.csv", index=False)

    manifest = build_manifest(localbench.BUILD)
    info = {
        "what": "local process-start benchmark (init PROXY) - not AWS Lambda, not an Init Duration",
        "started_utc": started.isoformat(timespec="seconds"),
        "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "reps": args.reps, "seed": args.seed, "warmup_rounds": args.warmup,
        "variants": [f"{r}-{v}" for r, v in variants],
        "failed_runs": int((~df["ok"]).sum()),
        "machine": localbench.machine_info(),
        "packages": manifest["variants"],
    }
    (out / "run_info.json").write_text(json.dumps(info, indent=2) + "\n")
    ok = df[df["ok"] & ~df["warmup"]]
    print(ok.groupby(["runtime", "variant"])[["init_proxy_ms", "handler_ms"]].median().round(1).to_string())
    return 0 if info["failed_runs"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
