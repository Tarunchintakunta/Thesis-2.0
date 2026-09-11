#!/usr/bin/env python
"""Whole-study budget estimate from list prices, before any run.

    python scripts/budget_estimate.py            # campaign N = provisional 1000
    python scripts/budget_estimate.py --n 2431   # e.g. the budget cap from the pilot rule

Counts invocations, billed Lambda time and DynamoDB write units for the pilot,
the campaign, the sensitivity phase and the warm-up calls, and prices them with
config/prices.yaml. Assumptions are the constants below. Not included:
CloudWatch Logs ingestion, stream reads, the driver machine and the free tier -
check the Billing console after the pilot.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from driver.schedule import build  # noqa: E402

OK_BILLED_MS = 200     # a delivery that does not time out (assumed; the pilot shows the real value)
REINIT_MS = 500        # a timeout resets the environment, so the next delivery pays INIT again (assumed)
WORKERS = 16           # warm-up waves are rounds x workers per phase


def write_units(path: str, m: int, inject: str) -> float:
    """Write request units of one request delivered m times (items <= 1 KB: one unit per write)."""
    if path in ("P1", "P2"):
        return float(m)                  # P1 writes every time; P2 writes once + (m-1) billed failed conditions
    if inject == "p3_between":
        return 2.0 * (m - 1) + 3         # claim + business write before each crash, the full path at the end
    return 3.0 + (m - 1)                 # claim, business write, complete + (m-1) failed claims


def phase_counts(cfg: dict, phase: str, n: int | None = None) -> dict:
    reqs = build(cfg, phase, n)
    inv = sum(r["multiplicity"] for r in reqs)
    tmo = sum(r["injected_retries"] for r in reqs)
    wru = sum(write_units(r["path"], r["multiplicity"], r["inject_mode"]) for r in reqs)
    return {"phase": phase, "requests": len(reqs), "invocations": inv, "timeouts": tmo, "wru": wru}


def estimate(cfg: dict, n: int) -> tuple[list[dict], float]:
    prices = yaml.safe_load(open(ROOT / "config/prices.yaml"))
    versions = yaml.safe_load(open(ROOT / "config/versions.yaml"))
    gb = versions["lambda"]["memory_mb"] / 1024
    timeout_s = versions["lambda"]["timeout_s"]
    rows = [phase_counts(cfg, "pilot"), phase_counts(cfg, "campaign", n), phase_counts(cfg, "sensitivity")]
    warm = 3 * cfg.get("warmup_rounds", 0) * WORKERS
    rows.append({"phase": "warm-up", "requests": 0, "invocations": warm, "timeouts": 0, "wru": 0.0})
    total = 0.0
    for r in rows:
        ok = r["invocations"] - r["timeouts"]
        r["gb_s"] = gb * (r["timeouts"] * timeout_s + ok * OK_BILLED_MS / 1000 + r["timeouts"] * REINIT_MS / 1000)
        r["usd"] = (r["invocations"] * prices["lambda_request"] + r["gb_s"] * prices["lambda_arm_gb_second"]
                    + r["wru"] * prices["dynamodb_write_request_unit"])
        total += r["usd"]
    return rows, total


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, help="campaign requests per cell (default: provisional N)")
    args = ap.parse_args(argv)
    cfg = yaml.safe_load(open(ROOT / "config/experiment.yaml"))
    rows, total = estimate(cfg, args.n or cfg["campaign"]["provisional_requests_per_cell"])
    print(f"{'phase':12s} {'requests':>9s} {'invocations':>12s} {'timeouts':>9s} {'write units':>12s} "
          f"{'GB-s':>9s} {'USD':>8s}")
    for r in rows:
        print(f"{r['phase']:12s} {r['requests']:9d} {r['invocations']:12d} {r['timeouts']:9d} {r['wru']:12.0f} "
              f"{r['gb_s']:9.0f} {r['usd']:8.3f}")
    inv = sum(r["invocations"] for r in rows)
    print(f"total USD {total:.2f} for {inv} invocations (cap {cfg['budget']['max_invocations']}, "
          f"daily budget USD {cfg['budget']['daily_usd']}); logs, stream reads and free tier not included")
    return 0 if inv <= cfg["budget"]["max_invocations"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
