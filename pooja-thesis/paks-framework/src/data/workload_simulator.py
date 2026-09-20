"""PROXY: synthetic sine + spikes. Not GCT/Alibaba. Not binding CA2 evidence.

Formal path: ``src/data/trace_loader.py`` + ``data/traces/PROVENANCE.md``.
"""
import numpy as np

POD_CAPACITY = 100.0  # requests per second per pod
MIN_PODS = 1
MAX_PODS = 100


def generate_workload(steps, seed):
    """Synthetic cyclical workload (requests/sec) with occasional spikes,
    matching the shape of the original PAKS simulator: a sine-wave base
    load, periodic traffic spikes, and small Gaussian noise."""
    rng = np.random.RandomState(seed)
    time = np.arange(steps)

    base = 1000 + 600 * np.sin(2 * np.pi * time / 50)

    spikes = np.zeros(steps)
    for idx in range(50, steps - 10, 80):
        spikes[idx:idx + 5] += rng.randint(800, 1500)

    noise = rng.normal(0, 100, steps)
    return np.clip(base + spikes + noise, 100, 10000)


def calculate_desired_pods(load, target_util, capacity=POD_CAPACITY):
    required = np.ceil(np.asarray(load) / (capacity * target_util))
    return np.clip(required, MIN_PODS, MAX_PODS)
