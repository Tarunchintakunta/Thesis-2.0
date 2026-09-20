#!/usr/bin/env python3
"""
Download and prepare UNSW-NB15 dataset.

Preference order:
1. Existing local CSV at data/UNSW_NB15_training-set.csv
2. Public mirror of the official training partition (real UNSW-NB15)
3. Synthetic fallback (explicit --synthetic only, or when download fails)

Provenance of any successful real download is written to data/DATA_PROVENANCE.json.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Public mirrors of the official UNSW-NB15 training partition (~175k rows).
# Primary source remains: https://research.unsw.edu.au/projects/unsw-nb15-dataset
REAL_UNSW_URLS = [
    (
        "https://raw.githubusercontent.com/Nir-J/ML-Projects/master/"
        "UNSW-Network_Packet_Classification/UNSW_NB15_training-set.csv"
    ),
    (
        "https://raw.githubusercontent.com/rifezacharyd/data-science/main/"
        "MATH211L34660499/MATH211_Rife_Portfolio/data/UNSW_NB15_training-set.csv"
    ),
]

OUTPUT_FILE = os.path.join("data", "UNSW_NB15_training-set.csv")
PROVENANCE_FILE = os.path.join("data", "DATA_PROVENANCE.json")


def _write_provenance(payload: dict) -> None:
    os.makedirs("data", exist_ok=True)
    with open(PROVENANCE_FILE, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Provenance written: {PROVENANCE_FILE}")


def _validate_real_unsw(path: str) -> dict:
    """Basic schema checks for the official training partition."""
    df = pd.read_csv(path, nrows=5)
    cols = set(df.columns.str.lower())
    required = {"label"}
    if not required.issubset(cols):
        raise ValueError(f"Missing required columns; got {sorted(df.columns)}")
    # Full file row count (streaming)
    n_rows = sum(1 for _ in open(path)) - 1
    n_cols = len(df.columns)
    if n_rows < 10000:
        raise ValueError(f"Too few rows for real partition: {n_rows}")
    # Synthetic generator uses 21 columns (20 feats + label); real has ~45
    if n_cols < 30:
        raise ValueError(
            f"Too few columns for real UNSW partition: {n_cols} "
            "(synthetic has ~21)"
        )
    return {
        "n_rows": n_rows,
        "n_cols": n_cols,
        "columns_sample": list(df.columns[:12]),
    }


def download_real_unsw(force: bool = False) -> str:
    """Fetch real UNSW-NB15 training partition from a public mirror."""
    os.makedirs("data", exist_ok=True)

    if os.path.exists(OUTPUT_FILE) and not force:
        try:
            meta = _validate_real_unsw(OUTPUT_FILE)
            print(f"Real UNSW-NB15 already present at {OUTPUT_FILE}")
            print(f"  rows≈{meta['n_rows']}, cols={meta['n_cols']}")
            return OUTPUT_FILE
        except ValueError as exc:
            print(f"Existing file is not a real partition ({exc}); re-downloading...")

    last_error = None
    for url in REAL_UNSW_URLS:
        print(f"Downloading real UNSW-NB15 training partition...\n  {url}")
        try:
            with requests.get(url, stream=True, timeout=120) as resp:
                resp.raise_for_status()
                tmp = OUTPUT_FILE + ".partial"
                with open(tmp, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=1 << 20):
                        if chunk:
                            f.write(chunk)
            meta = _validate_real_unsw(tmp)
            os.replace(tmp, OUTPUT_FILE)
            provenance = {
                "dataset": "UNSW-NB15 training partition",
                "kind": "real",
                "source_url": url,
                "official_project": (
                    "https://research.unsw.edu.au/projects/unsw-nb15-dataset"
                ),
                "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
                "local_path": OUTPUT_FILE,
                "n_rows": meta["n_rows"],
                "n_cols": meta["n_cols"],
                "note": (
                    "Public mirror of the official training-set CSV. "
                    "Not the full 2.5M-flow corpus; still a real UNSW partition."
                ),
            }
            _write_provenance(provenance)
            print(f"Saved real dataset: {OUTPUT_FILE}")
            print(f"  rows≈{meta['n_rows']}, cols={meta['n_cols']}")
            return OUTPUT_FILE
        except Exception as exc:  # noqa: BLE001 — try next mirror
            last_error = exc
            print(f"  failed: {exc}")
            if os.path.exists(OUTPUT_FILE + ".partial"):
                os.remove(OUTPUT_FILE + ".partial")

    raise RuntimeError(f"All real UNSW mirrors failed; last error: {last_error}")


def create_synthetic_unsw(sample: bool = False) -> str:
    """Create synthetic UNSW-NB15-derived sample (fallback / explicit)."""
    os.makedirs("data", exist_ok=True)
    num_samples = 5000 if sample else 50000
    num_features = 20
    np.random.seed(42)

    data = {
        "dur": np.random.exponential(scale=10, size=num_samples),
        "proto": np.random.choice(["tcp", "udp", "icmp"], size=num_samples),
        "state": np.random.choice(["FIN", "INT", "CON", "REQ"], size=num_samples),
        "spkts": np.random.poisson(lam=50, size=num_samples),
        "dpkts": np.random.poisson(lam=40, size=num_samples),
        "sbytes": np.random.exponential(scale=1000, size=num_samples),
        "dbytes": np.random.exponential(scale=800, size=num_samples),
        "rate": np.random.uniform(0, 1000, size=num_samples),
        "sttl": np.random.randint(0, 255, size=num_samples),
        "dttl": np.random.randint(0, 255, size=num_samples),
        "sload": np.random.uniform(0, 1e6, size=num_samples),
        "dload": np.random.uniform(0, 1e6, size=num_samples),
        "sinpkt": np.random.exponential(scale=100, size=num_samples),
        "dinpkt": np.random.exponential(scale=100, size=num_samples),
        "swin": np.random.randint(0, 65535, size=num_samples),
        "dwin": np.random.randint(0, 65535, size=num_samples),
        "tcprtt": np.random.exponential(scale=50, size=num_samples),
        "synack": np.random.exponential(scale=20, size=num_samples),
        "ackdat": np.random.exponential(scale=20, size=num_samples),
        "ct_srv_src": np.random.randint(0, 100, size=num_samples),
    }

    labels = np.zeros(num_samples, dtype=int)
    labels[int(num_samples * 0.8) :] = 1
    shuffle_idx = np.random.permutation(num_samples)
    for key in data:
        data[key] = data[key][shuffle_idx]
    labels = labels[shuffle_idx]
    data["label"] = labels

    df = pd.DataFrame(data)
    df["proto"] = df["proto"].map({"tcp": 0, "udp": 1, "icmp": 2})
    df["state"] = df["state"].map({"FIN": 0, "INT": 1, "CON": 2, "REQ": 3})
    df.to_csv(OUTPUT_FILE, index=False)

    provenance = {
        "dataset": "UNSW-NB15-derived synthetic",
        "kind": "synthetic",
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "local_path": OUTPUT_FILE,
        "n_rows": len(df),
        "n_cols": len(df.columns),
        "note": (
            "Synthetic 20-feature sample for offline PoC when real CSV unavailable."
        ),
    }
    _write_provenance(provenance)
    print(f"Synthetic dataset created: {OUTPUT_FILE}")
    print(f"Samples: {len(df)}, Features: {len(df.columns) - 1}")
    return OUTPUT_FILE


def main():
    parser = argparse.ArgumentParser(description="Download UNSW-NB15 dataset")
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Synthetic only: small 5K sample (ignored when downloading real)",
    )
    parser.add_argument(
        "--synthetic",
        action="store_true",
        help="Force synthetic generation (skip real download)",
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Require real UNSW-NB15 download (fail if mirrors unavailable)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if a local CSV exists",
    )
    args = parser.parse_args()

    if args.synthetic or args.sample:
        create_synthetic_unsw(sample=args.sample)
        print("\nDataset ready (synthetic).")
        return

    try:
        download_real_unsw(force=args.force)
        print("\nDataset ready (real UNSW-NB15 training partition).")
    except Exception as exc:  # noqa: BLE001
        if args.real:
            raise
        print(f"\nReal download failed ({exc}); falling back to synthetic.")
        create_synthetic_unsw(sample=False)
        print("\nDataset ready (synthetic fallback).")


if __name__ == "__main__":
    main()
