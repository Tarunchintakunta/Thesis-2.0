#!/usr/bin/env python3
"""Download free GCT 2011 part-00000 and an Alibaba v2018 machine_usage range sample.

Does not fetch the full multi-GB Alibaba machine_usage tarball or all 500 GCT
2011 parts. Does not deploy AWS. Records SHA256 provenance sidecars.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import sys
import tarfile
import urllib.request
from collections import defaultdict
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]
GCT2011_DIR = FRAMEWORK_ROOT / "data" / "gct" / "2011" / "task_usage"
ALI_DIR = FRAMEWORK_ROOT / "data" / "alibaba" / "v2018"
TRACES_DIR = FRAMEWORK_ROOT / "data" / "traces"

GCT2011_PART = "part-00000-of-00500.csv.gz"
GCT2011_URL = f"https://storage.googleapis.com/clusterdata-2011-2/task_usage/{GCT2011_PART}"
GCT2011_SHA256 = "841254d3bc4199c26c82890dcd6bc87fcfb1ff23d75be8e39f0337f0ed1c6e28"

ALI_META_URL = "http://aliopentrace.oss-cn-beijing.aliyuncs.com/v2018Traces/machine_meta.tar.gz"
ALI_META_SHA256 = "b5b1b786b22cd413a3674b8f2ebfb2f02fac991c95df537f363ef2797c8f6d55"
ALI_USAGE_URL = "http://aliopentrace.oss-cn-beijing.aliyuncs.com/v2018Traces/machine_usage.tar.gz"
ALI_PARTIAL_NAME = "machine_usage.tar.gz.partial64m"
ALI_PARTIAL_BYTES = 64 * 1024 * 1024
ALI_PARTIAL_SHA256 = "49396e44de5d6bdee04b99bfdea19adafaeee891e3c1bd40117e2ece1192f378"
ALI_FULL_OBJECT_BYTES = 1_774_523_160

BIN_US = 300_000_000
MIN_JOB_BINS = 12


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path, expected_sha256: str | None = None, timeout: int = 300) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and expected_sha256 and sha256_file(dest) == expected_sha256:
        print(f"already present and SHA256-verified: {dest}")
        return dest
    print(f"GET {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "paks-sample/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp, dest.open("wb") as out:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            out.write(chunk)
    digest = sha256_file(dest)
    if expected_sha256 and digest != expected_sha256:
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"SHA256 mismatch for {dest}: got {digest}")
    print(f"verified SHA256 {digest} ({dest.stat().st_size} bytes)")
    (dest.parent / f"{dest.name}.sha256").write_text(f"{digest}  {dest.name}\n")
    return dest


def download_range(url: str, dest: Path, nbytes: int, expected_sha256: str | None = None, timeout: int = 600) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and expected_sha256 and sha256_file(dest) == expected_sha256:
        print(f"already present and SHA256-verified: {dest}")
        return dest
    print(f"GET {url} Range bytes=0-{nbytes - 1}")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "paks-sample/1.0", "Range": f"bytes=0-{nbytes - 1}"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp, dest.open("wb") as out:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            out.write(chunk)
    digest = sha256_file(dest)
    if expected_sha256 and digest != expected_sha256:
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"SHA256 mismatch for {dest}: got {digest}")
    print(f"verified SHA256 {digest} ({dest.stat().st_size} bytes; RANGE sample of {ALI_FULL_OBJECT_BYTES})")
    (dest.parent / f"{dest.name}.sha256").write_text(
        f"{digest}  {dest.name}  range=0-{nbytes - 1}/{ALI_FULL_OBJECT_BYTES}\n"
    )
    return dest


def aggregate_gct2011(part: Path, traces: Path) -> None:
    traces.mkdir(parents=True, exist_ok=True)
    cluster = defaultdict(lambda: {"cpu": 0.0, "mem": 0.0, "n": 0})
    job_time = defaultdict(lambda: defaultdict(float))
    with gzip.open(part, "rt") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 7:
                continue
            start = int(parts[0])
            job = parts[2]
            cpu = float(parts[5])
            mem = float(parts[6])
            t_s = (start // BIN_US) * 300
            cluster[t_s]["cpu"] += cpu
            cluster[t_s]["mem"] += mem
            cluster[t_s]["n"] += 1
            job_time[job][t_s] += cpu
    cluster_path = traces / "gct2011_part00000_cluster_cpu.csv"
    with cluster_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time_s", "cpu_cores_sum", "mem_sum", "n_tasks", "source_part"])
        for t in sorted(cluster):
            a = cluster[t]
            w.writerow([t, f"{a['cpu']:.8f}", f"{a['mem']:.8f}", a["n"], GCT2011_PART])
    jobs_path = traces / "gct2011_part00000_job_cpu_series.csv.gz"
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
    print(f"wrote {cluster_path} ({len(cluster)} × 300s bins)")
    print(f"wrote {jobs_path} ({n_rows} job-time rows, min_bins={MIN_JOB_BINS})")


def aggregate_alibaba(partial: Path, traces: Path, decompress_cap: int = 45_000_000, csv_cap: int = 25_000_000) -> None:
    traces.mkdir(parents=True, exist_ok=True)
    with gzip.open(partial, "rb") as g:
        data = g.read(decompress_cap)
    bio = io.BytesIO(data)
    with tarfile.open(fileobj=bio, mode="r:") as tf:
        member = tf.next()
        if member is None:
            raise RuntimeError("empty tar in Alibaba partial sample")
        handle = tf.extractfile(member)
        if handle is None:
            raise RuntimeError("could not extract machine_usage.csv from partial tar")
        raw = handle.read(csv_cap)
    last = raw.rfind(b"\n")
    if last < 0:
        raise RuntimeError("no complete CSV lines in Alibaba sample")
    raw = raw[: last + 1]
    by_t = defaultdict(lambda: {"cpu": 0.0, "mem": 0.0, "n": 0})
    for line in raw.splitlines():
        cols = line.decode("ascii", "ignore").split(",")
        if len(cols) < 4:
            continue
        try:
            ts = int(cols[1])
            cpu = float(cols[2]) if cols[2] else 0.0
            mem = float(cols[3]) if cols[3] else 0.0
        except ValueError:
            continue
        by_t[ts]["cpu"] += cpu
        by_t[ts]["mem"] += mem
        by_t[ts]["n"] += 1
    # Resample to 300s mean (Alibaba native spacing is ~10s).
    bins = defaultdict(lambda: {"cpu": 0.0, "mem": 0.0, "n": 0, "nm": 0.0})
    for ts, a in by_t.items():
        b = (ts // 300) * 300
        nm = max(1, a["n"])
        bins[b]["cpu"] += a["cpu"] / nm
        bins[b]["mem"] += a["mem"] / nm
        bins[b]["n"] += 1
        bins[b]["nm"] += nm
    out = traces / "alibaba_v2018_machine_usage_sample_cluster_cpu.csv"
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time_s", "cpu_cores_sum", "mem_sum", "n_machines_mean", "sample_note"])
        for t in sorted(bins):
            a = bins[t]
            n = max(1, a["n"])
            w.writerow(
                [
                    t,
                    f"{a['cpu'] / n:.6f}",
                    f"{a['mem'] / n:.6f}",
                    f"{a['nm'] / n:.2f}",
                    "RANGE_64MiB_partial_tar_gz;resampled_300s_mean",
                ]
            )
    print(f"wrote {out} ({len(bins)} × 300s bins from RANGE sample)")


def write_sha_index(traces: Path) -> None:
    lines = [
        f"gct2011 {GCT2011_PART} sha256={GCT2011_SHA256} bytes=91723415 url={GCT2011_URL}",
        f"alibaba machine_meta.tar.gz sha256={ALI_META_SHA256} url={ALI_META_URL}",
        (
            f"alibaba {ALI_PARTIAL_NAME} sha256={ALI_PARTIAL_SHA256} "
            f"bytes={ALI_PARTIAL_BYTES} full_object_bytes={ALI_FULL_OBJECT_BYTES} url={ALI_USAGE_URL}"
        ),
        "",
    ]
    path = traces / "SAMPLE_SHA256.txt"
    path.write_text("\n".join(lines))
    print(f"wrote {path}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--skip-download", action="store_true")
    p.add_argument("--aggregate-only", action="store_true")
    args = p.parse_args()

    part = GCT2011_DIR / GCT2011_PART
    meta = ALI_DIR / "machine_meta.tar.gz"
    partial = ALI_DIR / ALI_PARTIAL_NAME

    if not (args.aggregate_only or args.skip_download):
        download(GCT2011_URL, part, GCT2011_SHA256)
        download(ALI_META_URL, meta, ALI_META_SHA256, timeout=60)
        download_range(ALI_USAGE_URL, partial, ALI_PARTIAL_BYTES, ALI_PARTIAL_SHA256)
    else:
        for path, digest in ((part, GCT2011_SHA256), (partial, ALI_PARTIAL_SHA256)):
            if not path.is_file():
                print(f"missing {path}", file=sys.stderr)
                return 2
            if sha256_file(path) != digest:
                print(f"SHA256 mismatch: {path}", file=sys.stderr)
                return 2

    aggregate_gct2011(part, TRACES_DIR)
    aggregate_alibaba(partial, TRACES_DIR)
    write_sha_index(TRACES_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
