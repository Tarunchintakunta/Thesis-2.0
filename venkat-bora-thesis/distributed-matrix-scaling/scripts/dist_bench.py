#!/usr/bin/env python3
"""Instrumented multi-instance Dask matmul for Venkat live EC2.

Env: MATRIX_SIZE, SCHEDULER_URL, BENCH_TIMEOUT
Timeouts/failures recorded as status outcomes.
"""
from __future__ import annotations

import json
import os
import threading
import time

import numpy as np
import psutil


class _RssCpuMonitor:
    def __init__(self, interval: float = 0.05) -> None:
        self.interval = interval
        self.peak_rss_mb = 0.0
        self.cpu_samples: list[float] = []
        self._stop = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self.peak_rss_mb = 0.0
        self.cpu_samples = []
        self._stop = False
        psutil.cpu_percent(interval=None)
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> tuple[float, float]:
        self._stop = True
        if self._thread:
            self._thread.join(timeout=2.0)
        avg_cpu = float(np.mean(self.cpu_samples)) if self.cpu_samples else 0.0
        return self.peak_rss_mb, avg_cpu

    def _loop(self) -> None:
        proc = psutil.Process(os.getpid())
        while not self._stop:
            try:
                rss = proc.memory_info().rss / (1024 * 1024)
                self.peak_rss_mb = max(self.peak_rss_mb, rss)
                self.cpu_samples.append(psutil.cpu_percent(interval=None))
                time.sleep(self.interval)
            except Exception:
                break


def main() -> None:
    from dask.distributed import Client
    import dask.array as da

    size = int(os.environ.get("MATRIX_SIZE", "250"))
    sched = os.environ.get("SCHEDULER_URL", "tcp://127.0.0.1:8786")
    hard_timeout = float(os.environ.get("BENCH_TIMEOUT", "600"))

    print("connecting", sched, flush=True)
    client = Client(sched, timeout="60s")
    info = client.scheduler_info()
    nworkers = len(info.get("workers", {}))
    print("workers", nworkers, flush=True)
    futs = [client.submit(lambda x: x * x, i) for i in range(4)]
    smoke = [f.result(timeout=60) for f in futs]
    print("futures", smoke, flush=True)

    rng = np.random.default_rng(42)
    A = rng.random((size, size), dtype=np.float64)
    B = rng.random((size, size), dtype=np.float64)
    w = max(nworkers, 1)
    chunk = max(size // w, 1)
    a = da.from_array(A, chunks=(chunk, size))
    b = da.from_array(B, chunks=(size, chunk))

    mon = _RssCpuMonitor()
    mon.start()
    print("matmul_start", size, "chunk", chunk, flush=True)
    t0 = time.perf_counter()
    status = "ok"
    err = None
    checksum = None
    elapsed = None
    try:
        future = client.compute(a @ b)
        C = future.result(timeout=hard_timeout)
        elapsed = time.perf_counter() - t0
        checksum = float(C[0, 0])
        print("matmul_done", elapsed, flush=True)
    except Exception as e:  # noqa: BLE001
        elapsed = time.perf_counter() - t0
        name = type(e).__name__
        status = "timed_out" if "Timeout" in name or "timeout" in str(e).lower() else "failed"
        err = repr(e)
        print("matmul_outcome", status, err, flush=True)
    peak_rss_mb, avg_cpu_percent = mon.stop()

    payload = {
        "role": "scale-out",
        "mode": "dask_multi_instance",
        "size": size,
        "workers": nworkers,
        "status": status,
        "elapsed_s": elapsed,
        "peak_rss_mb": peak_rss_mb,
        "avg_cpu_percent": avg_cpu_percent,
        "checksum": checksum,
        "futures_smoke": smoke,
        "worker_addrs": list(info.get("workers", {}).keys()),
        "error": err,
        "hostname": os.uname().nodename,
    }
    print(json.dumps(payload), flush=True)
    client.close()


if __name__ == "__main__":
    main()
