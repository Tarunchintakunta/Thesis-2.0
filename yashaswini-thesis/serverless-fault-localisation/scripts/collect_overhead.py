#!/usr/bin/env python
"""Measure one telemetry condition after its load run, then summarise all of them.

    python scripts/collect_overhead.py --run data/runs/live --condition full     # after each overhead phase
    python scripts/collect_overhead.py --run data/runs/live --summarise          # after all three

Logs: CloudWatch AWS/Logs IncomingBytes (Sum) of the four log groups over the
phase window (+2 min for late delivery). X-Ray: the number of traces recorded in
the window and the mean size of the segment documents of up to 200 of them.
The summary writes results/live/overhead.json with volume per 1000 requests,
the reduction of the policy against full, the latency test (tracing on vs off),
the cost per million requests and the learned arm's lower bound.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def log_bytes(cw, groups: list[str], start: dt.datetime, end: dt.datetime) -> float:
    total = 0.0
    for g in groups:
        resp = cw.get_metric_statistics(Namespace="AWS/Logs", MetricName="IncomingBytes", StartTime=start,
                                        EndTime=end, Period=300, Statistics=["Sum"],
                                        Dimensions=[{"Name": "LogGroupName", "Value": g}])
        total += sum(p["Sum"] for p in resp["Datapoints"])
    return total


def trace_volume(xr, start: dt.datetime, end: dt.datetime, sample: int = 200) -> tuple[int, float]:
    from detector import xray

    ids = xray.trace_ids(xr, start, end)
    traces = xray.fetch_traces(xr, ids[:sample])
    sizes = [sum(len(s["Document"]) for s in t.get("Segments", [])) for t in traces]
    return len(ids), (sum(sizes) / len(sizes) if sizes else 0.0)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", default="data/runs/live")
    ap.add_argument("--condition", choices=["full", "policy", "off"])
    ap.add_argument("--summarise", action="store_true")
    ap.add_argument("--stack", default="faultlab")
    ap.add_argument("--region", default="eu-west-1")
    ap.add_argument("--config", default="configs/experiment.yaml",
                    help="experiment yaml (use configs/experiment_lite_overhead.yaml for lite Leg 3)")
    args = ap.parse_args(argv)
    cfg = Path(args.config)
    if not cfg.is_absolute():
        cfg = ROOT / cfg
    exp = yaml.safe_load(open(cfg))
    run = Path(args.run)
    if args.summarise:
        from eval import overhead

        prices = yaml.safe_load(open(ROOT / "configs/prices.yaml"))
        conds = {c: json.loads((run / f"overhead_{c}.json").read_text()) for c in ("full", "policy", "off")}
        report = {"conditions": conds, "reduction_policy_vs_full": overhead.reduction(conds["policy"], conds["full"]),
                  "expected_reduction": exp["expectations"]["telemetry_reduction"],
                  "latency_tracing_on_vs_off": overhead.latency_effect(run / "requests_overhead-policy.csv",
                                                                       run / "requests_overhead-off.csv"),
                  "cost_per_million_requests": {c: overhead.cost_per_million(v, prices) for c, v in conds.items()
                                                if c != "off"},
                  "learned_lower_bound_bytes_per_1000_requests":
                      float(overhead.learned_lower_bound(ROOT / "data/rcaeval")["bytes_per_1000_requests"].median()),
                  "asymmetry": "the learned baselines run offline; their overhead is a lower bound from their inputs, "
                               "not a measurement on this service"}
        print(overhead.write(ROOT / "results/live", report))
        return 0
    import boto3

    windows = json.loads((run / "windows.json").read_text())
    t0, t1 = windows[f"overhead-{args.condition}"]
    utc = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc)  # noqa: E731
    groups = [f"/aws/lambda/{args.stack}-{s.replace('_', '-')}" for s in exp["services"]]
    lb = log_bytes(boto3.client("cloudwatch", region_name=args.region), groups, utc(t0), utc(t1 + 120))
    n, mean = trace_volume(boto3.client("xray", region_name=args.region), utc(t0), utc(t1))
    from eval import overhead

    cond = overhead.condition(run / f"requests_overhead-{args.condition}.csv", lb, n, mean,
                              policy=exp["tracing"][args.condition])
    (run / f"overhead_{args.condition}.json").write_text(json.dumps(cond, indent=2) + "\n")
    print(json.dumps(cond, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
