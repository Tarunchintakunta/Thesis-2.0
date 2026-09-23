#!/usr/bin/env python3
"""Download the public GCT v1 (2010) 7-hour sample and/or re-aggregate derived series.

Does not fetch the multi-GB GCT 2011 / 2019 or Alibaba dumps.
Does not deploy AWS. License: CC-BY 4.0 (see data/traces/PROVENANCE.md).
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = FRAMEWORK_ROOT / "data" / "raw"
TRACES_DIR = FRAMEWORK_ROOT / "data" / "traces"

GCT_V1_URL = "http://commondatastorage.googleapis.com/clusterdata-misc/google-cluster-data-1.csv.gz"
GCT_V1_SHA1 = "98c87f059aa1cc37f1e9523ac691ee0fd5629188"
GCT_V1_NAME = "google-cluster-data-1.csv.gz"
MIN_JOB_BINS = 12


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def download_gct_v1(dest: Path, timeout: int = 120) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and sha1_file(dest) == GCT_V1_SHA1:
        print(f"already present and SHA1-verified: {dest}")
        return dest
    print(f"GET {GCT_V1_URL}")
    req = urllib.request.Request(GCT_V1_URL, headers={"User-Agent": "paks-slice/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp, dest.open("wb") as out:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            out.write(chunk)
    digest = sha1_file(dest)
    if digest != GCT_V1_SHA1:
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"SHA1 mismatch: got {digest} expected {GCT_V1_SHA1}")
    print(f"verified SHA1 {digest} ({dest.stat().st_size} bytes)")
    return dest


def aggregate(raw: Path, traces: Path) -> None:
    traces.mkdir(parents=True, exist_ok=True)
    cluster = defaultdict(lambda: {"cores": 0.0, "mem": 0.0, "tasks": 0})
    job_time = defaultdict(lambda: defaultdict(float))
    with gzip.open(raw, "rt") as g:
        header = g.readline()
        if "NrmlTaskCores" not in header:
            raise ValueError(f"unexpected GCT v1 header: {header!r}")
        for line in g:
            parts = line.split()
            if len(parts) < 6:
                continue
            t = int(parts[0])
            job = parts[1]
            cores = float(parts[4])
            mem = float(parts[5])
            c = cluster[t]
            c["cores"] += cores
            c["mem"] += mem
            c["tasks"] += 1
            job_time[job][t] += cores
    cluster_path = traces / "gct2010_cluster_cpu.csv"
    with cluster_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time_s", "cpu_cores_sum", "mem_sum", "n_tasks"])
        for t in sorted(cluster):
            a = cluster[t]
            w.writerow([t, f"{a['cores']:.8f}", f"{a['mem']:.8f}", a["tasks"]])
    jobs_path = traces / "gct2010_job_cpu_series.csv.gz"
    n_rows = 0
    with gzip.open(jobs_path, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["job_id", "time_s", "cpu_cores_sum"])
        for job, series in job_time.items():
            if len(series) < MIN_JOB_BINS:
                continue
            for t in sorted(series):
                w.writerow([job, t, f"{series[t]:.8f}"])
                n_rows += 1
    print(f"wrote {cluster_path} ({len(cluster)} bins)")
    print(f"wrote {jobs_path} ({n_rows} job-time rows, min_bins={MIN_JOB_BINS})")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--skip-download", action="store_true")
    p.add_argument("--aggregate-only", action="store_true")
    args = p.parse_args()
    raw = RAW_DIR / GCT_V1_NAME
    if args.aggregate_only or args.skip_download:
        if not raw.is_file():
            print(f"raw gzip missing: {raw}", file=sys.stderr)
            return 2
        if sha1_file(raw) != GCT_V1_SHA1:
            print("raw gzip SHA1 mismatch; re-download without --skip-download", file=sys.stderr)
            return 2
    else:
        download_gct_v1(raw)
    aggregate(raw, TRACES_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
