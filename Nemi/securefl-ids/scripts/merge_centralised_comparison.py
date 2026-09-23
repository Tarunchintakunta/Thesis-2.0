#!/usr/bin/env python3
"""Merge centralised comparator into results/comparison/results.json.

Reads computed metrics only from results/centralised/summary.json.
Does not invent or preserve synthetic FL numbers.
"""
import json
import os
import sys


def main():
    comparison_path = "results/comparison/results.json"
    central_path = "results/centralised/summary.json"

    if not os.path.exists(central_path):
        print(f"Missing {central_path}; run scripts/run_centralised.py first", file=sys.stderr)
        sys.exit(1)

    with open(central_path) as f:
        central = json.load(f)

    if os.path.exists(comparison_path):
        with open(comparison_path) as f:
            comparison = json.load(f)
    else:
        comparison = {}

    comparison["centralised"] = central

    os.makedirs(os.path.dirname(comparison_path), exist_ok=True)
    with open(comparison_path, "w") as f:
        json.dump(comparison, f, indent=2)

    print(f"Updated {comparison_path} with centralised arm:")
    print(
        f"  accuracy={central['accuracy']:.4f} "
        f"f1={central['f1_score']:.4f} "
        f"mode={central.get('mode')}"
    )


if __name__ == "__main__":
    main()
