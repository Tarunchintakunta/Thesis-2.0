"""Live mode: drive the deployed Orders API in real time (LocalStack / own account).

    python -m logad.collect.live_traffic --config configs/live.yaml --api-url http://... \
        --function kasireddy-orders --role <FunctionRoleName> --table kasireddy-orders --out data/raw/live

Runs phase A (clean), phase B (with the fault schedule, switched through
``logad.inject.live.LiveFaultSwitch``) and phase C (bursts, no faults) one
after the other, in real time, then pulls the function's logs from CloudWatch
Logs. It writes the same files as the emulator (phase_*.log, metrics_*.csv,
bursts_*.csv, ground_truth.csv, meta.json), so the pipeline runs unchanged.

The per-request metrics are observed from the client side (HTTP status and
latency) - an approximation of the CloudWatch metrics the emulator produces.

Not executed in this repository against a real endpoint.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import time
import urllib.error
import urllib.request
from dataclasses import asdict
from pathlib import Path

from logad.collect.cloudwatch import fetch_events, write_log
from logad.collect.workload import arrivals, make_event, pick_route, regular_bursts
from logad.config import dict_hash, load_experiment
from logad.inject.live import LiveFaultSwitch
from logad.inject.schedule import active_at, build_schedule, schedule_end, write_ground_truth

FIELDS = ["t", "route", "throttled", "status", "error", "duration_ms", "cold", "timeout", "killed"]


def send(api_url: str, event: dict, timeout_s: float = 10.0) -> tuple[int, float]:
    method, path = event["routeKey"].split(" ", 1)
    if "{id}" in path:
        path = path.replace("{id}", event["pathParameters"]["id"])
    data = event.get("body", "").encode() if method == "POST" else None
    req = urllib.request.Request(api_url.rstrip("/") + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            status = resp.status
    except urllib.error.HTTPError as err:
        status = err.code
    except (urllib.error.URLError, TimeoutError):
        status = 599
    return status, (time.time() - t0) * 1000.0


def run_phase(api_url, t0, t1, cfg, bursts, rng, switch=None, schedule=None, settle_s=20.0) -> list[dict]:
    wl = cfg["workload"]
    order_ids: list[str] = []
    rows = []
    for t in arrivals(t0, t1, wl["base_rate"], wl["diurnal_amplitude"], bursts, rng):
        wait = t - time.time()
        if wait > 0:
            time.sleep(wait)
        if switch is not None:
            inj = active_at(schedule, t)
            wanted = inj.category if inj else None
            if wanted != switch.active:
                switch.off()
                if wanted:
                    switch.on(wanted)
        status, ms = send(api_url, make_event(pick_route(wl["route_mix"], rng), rng, order_ids))
        rows.append({"t": t, "route": "", "throttled": status == 429, "status": status,
                     "error": status in (502, 503), "duration_ms": ms, "cold": False,
                     "timeout": status == 503, "killed": status == 502})
    if switch is not None:
        switch.off()
    return rows


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default="configs/live.yaml")
    p.add_argument("--api-url", required=True)
    p.add_argument("--function", default="kasireddy-orders")
    p.add_argument("--role", required=True)
    p.add_argument("--table", default="kasireddy-orders")
    p.add_argument("--out", default="data/raw/live")
    args = p.parse_args(argv)

    import boto3

    endpoint = os.environ.get("AWS_ENDPOINT_URL") or None
    cfg = load_experiment(args.config)
    seed = cfg["seeds"][0]
    rng = random.Random(seed)
    out = Path(args.out) / f"seed_{seed}"
    out.mkdir(parents=True, exist_ok=True)
    switch = LiveFaultSwitch(boto3.client("lambda", endpoint_url=endpoint), boto3.client("iam", endpoint_url=endpoint),
                             args.function, args.role, args.table)
    logs = boto3.client("logs", endpoint_url=endpoint)
    phases = cfg["phases"]
    meta = {"seed": seed, "config": cfg["name"], "config_hash": dict_hash(cfg), "mode": "live", "phases": {}}

    now = time.time() + 5
    bounds = {}
    a0, a1 = now, now + phases["A"]["hours"] * 3600
    schedule = build_schedule(a1, phases["B"]["injections_per_category"], phases["B"]["block_size"],
                              tuple(phases["B"]["gap_s"]), tuple(phases["B"]["duration_s"]), rng)
    b1 = schedule_end(schedule, phases["B"]["tail_s"])
    c1 = b1 + phases["C"]["hours"] * 3600
    bounds = {"A": (a0, a1), "B": (a1, b1), "C": (b1, c1)}
    write_ground_truth(schedule, out / "ground_truth.csv")

    for ph, (t0, t1) in bounds.items():
        b = phases[ph]["bursts"]
        bursts = regular_bursts(t0, t1, b["every_s"], b["len_s"], b["factor"], rng)
        rows = run_phase(args.api_url, t0, t1, cfg, bursts, rng,
                         switch if ph == "B" else None, schedule if ph == "B" else None)
        with open(out / f"metrics_{ph}.csv", "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        with open(out / f"bursts_{ph}.csv", "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=["start", "length", "factor"])
            writer.writeheader()
            writer.writerows(asdict(x) for x in bursts)
        time.sleep(30)  # let CloudWatch Logs catch up
        events = fetch_events(logs, cfg["live"]["log_group"], int(t0 * 1000), int(t1 * 1000))
        write_log(events, out / f"phase_{ph}.log")
        meta["phases"][ph] = {"start": t0, "end": t1, "lines": len(events), "requests": len(rows)}
    (out / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta["phases"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
