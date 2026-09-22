#!/usr/bin/env python3
"""Instrumented scale-up / on-node bench for Venkat live EC2.

Reports completion time plus peak RSS (MB) and mean CPU %% so RQ limbs
(memory footprint, CPU efficiency) are measurable on the same software stack.
Env: MATRIX_SIZE, N_WORKERS, NODE_ROLE=scale-up|scale-out, RESULT_PATH
"""
from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path

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
    size = int(os.environ.get("MATRIX_SIZE", "250"))
    workers = int(os.environ.get("N_WORKERS", "2"))
    role = os.environ.get("NODE_ROLE", "scale-up")
    out = Path(os.environ.get("RESULT_PATH", "/opt/matrix-scale/result.json"))

    rng = np.random.default_rng(42)
    A = rng.random((size, size), dtype=np.float64)
    B = rng.random((size, size), dtype=np.float64)

    mon = _RssCpuMonitor()
    mon.start()
    t0 = time.perf_counter()
    status = "ok"
    err = None
    checksum = None
    try:
        if role == "scale-up":
            C = A @ B
            mode = "numpy_matmul"
        else:
            from dask.distributed import Client, LocalCluster
            import dask.array as da

            cluster = LocalCluster(
                n_workers=workers,
                threads_per_worker=1,
                processes=False,
                dashboard_address=None,
            )
            client = Client(cluster)
            a = da.from_array(A, chunks=(size // max(workers, 1), size))
            b = da.from_array(B, chunks=(size, size // max(workers, 1)))
            C = (a @ b).compute()
            client.close()
            cluster.close()
            mode = "dask_localcluster_on_node"
        checksum = float(C[0, 0])
    except Exception as e:  # noqa: BLE001
        status = "failed"
        mode = "error"
        err = repr(e)
    elapsed = time.perf_counter() - t0
    peak_rss_mb, avg_cpu_percent = mon.stop()

    payload = {
        "role": role,
        "mode": mode,
        "size": size,
        "workers": workers,
        "status": status,
        "elapsed_s": elapsed,
        "peak_rss_mb": peak_rss_mb,
        "avg_cpu_percent": avg_cpu_percent,
        "checksum": checksum,
        "hostname": os.uname().nodename,
        "error": err,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2) + "\n"
    out.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
