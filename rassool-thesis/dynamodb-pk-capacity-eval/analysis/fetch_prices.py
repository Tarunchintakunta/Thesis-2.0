#!/usr/bin/env python
"""Refresh config/prices.yaml from the AWS Price List API (no credentials needed).

    python analysis/fetch_prices.py --region eu-west-1

Picks the Standard-table-class request-unit and capacity-unit-hour prices (the
tiers beyond the free tier) and writes them with the offer file's publication date.
"""
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/{region}/index.json"
WANT = {"ReadRequestUnits": "read_request_unit", "WriteRequestUnits": "write_request_unit",
        "ReadCapacityUnit-Hrs": "rcu_hour", "WriteCapacityUnit-Hrs": "wcu_hour"}


def extract(offer: dict) -> dict:
    found = {}
    for sku, prod in offer["products"].items():
        usage = prod.get("attributes", {}).get("usagetype", "")
        suffix = usage.split("-", 1)[1] if "-" in usage else usage
        if suffix not in WANT:  # skips IA table class, replicated units, etc.
            continue
        for term in offer["terms"]["OnDemand"].get(sku, {}).values():
            for dim in term["priceDimensions"].values():
                price = float(dim["pricePerUnit"]["USD"])
                if price > 0:  # the $0 line is the free tier
                    found[WANT[suffix]] = price
    missing = set(WANT.values()) - set(found)
    if missing:
        raise ValueError(f"prices not found in offer file: {sorted(missing)}")
    return found


def render(region: str, publication: str, p: dict) -> str:
    return f"""# Published DynamoDB unit prices used by analysis/cost_model.py.
# Source: AWS Price List API, offer file
#   {URL.format(region=region)}
# publicationDate {publication}, table class Standard.
# Refresh with: python analysis/fetch_prices.py --region {region}
# Cost per 10k ops leaves out storage, backups and data transfer on purpose
# (master prompt 2.3) - only the request path the configuration controls.
region: {region}
source: AWS Price List API (AmazonDynamoDB offer file)
publication_date: "{publication}"
currency: USD

on_demand:
  read_request_unit: {p['read_request_unit']:.10f}
  write_request_unit: {p['write_request_unit']:.10f}

provisioned:
  rcu_hour: {p['rcu_hour']:.9f}
  wcu_hour: {p['wcu_hour']:.9f}

free_tier_ignored: true
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--region", default="eu-west-1")
    ap.add_argument("--out", default=str(ROOT / "config/prices.yaml"))
    args = ap.parse_args(argv)
    with urllib.request.urlopen(URL.format(region=args.region), timeout=60) as r:
        offer = json.load(r)
    text = render(args.region, offer["publicationDate"], extract(offer))
    Path(args.out).write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
