import numpy as np
import pandas as pd

FEATURES = ["rtt", "cpu", "ram", "success_rate", "latency", "throughput"]

# Decision thresholds, matching Et-Tousy et al. (2026), "Adaptive QoS
# Management in OneM2M Standard": Preferable (Keep Local) if RTT < 2s with
# low resource usage and high success; Acceptable (Partial Offload) for
# RTT 2-4s; Critical (Full Offload) once RTT > 4s, success < 90%, or
# CPU/RAM > 80%.
def _label(rtt, cpu, ram, success_rate):
    if rtt > 4.0 or success_rate < 90.0 or cpu > 80.0 or ram > 80.0:
        return 2
    if rtt >= 2.0:
        return 1
    return 0


# Non-IID site regime mix: each site is dominated by one of the paper's
# three traffic scenarios (uniform / burst / real-time), which is what
# makes this a realistic federated learning setting -- no site sees a
# representative sample of the whole distribution on its own.
SITE_REGIMES = {
    "site_uniform_a": {"uniform": 0.8, "burst": 0.1, "realtime": 0.1},
    "site_uniform_b": {"uniform": 0.8, "burst": 0.1, "realtime": 0.1},
    "site_burst_a": {"uniform": 0.1, "burst": 0.8, "realtime": 0.1},
    "site_burst_b": {"uniform": 0.1, "burst": 0.8, "realtime": 0.1},
    "site_realtime_a": {"uniform": 0.1, "burst": 0.1, "realtime": 0.8},
    "site_realtime_b": {"uniform": 0.1, "burst": 0.1, "realtime": 0.8},
}


def _generate_regime(rng, regime, n):
    if regime == "uniform":
        rtt = np.clip(rng.normal(1.2, 0.5, n), 0.1, None)
        cpu = np.clip(rng.normal(40, 12, n), 1, 100)
        ram = np.clip(rng.normal(45, 12, n), 1, 100)
        success = np.clip(rng.normal(99, 1.5, n), 0, 100)
    elif regime == "burst":
        rtt = np.clip(rng.exponential(2.0, n) + 0.5, 0.1, None)
        cpu = np.clip(rng.normal(65, 20, n), 1, 100)
        ram = np.clip(rng.normal(60, 18, n), 1, 100)
        success = np.clip(rng.normal(92, 8, n), 0, 100)
    else:  # realtime
        rtt = np.clip(rng.normal(2.5, 1.8, n), 0.1, None)
        cpu = np.clip(rng.normal(55, 18, n), 1, 100)
        ram = np.clip(rng.normal(55, 15, n), 1, 100)
        success = np.clip(rng.normal(95, 6, n), 0, 100)

    latency = rtt * 250 + rng.normal(0, 30, n)
    throughput = np.clip(120 - rtt * 15 + rng.normal(0, 10, n), 1, None)
    return rtt, cpu, ram, success, latency, throughput


def generate_site_data(site_name, n_samples, seed):
    rng = np.random.RandomState(seed)
    regimes = SITE_REGIMES[site_name]
    names, weights = zip(*regimes.items())
    choices = rng.choice(names, size=n_samples, p=weights)

    rows = []
    for regime in ["uniform", "burst", "realtime"]:
        idx = np.where(choices == regime)[0]
        if len(idx) == 0:
            continue
        rtt, cpu, ram, success, latency, throughput = _generate_regime(rng, regime, len(idx))
        for i in range(len(idx)):
            label = _label(rtt[i], cpu[i], ram[i], success[i])
            rows.append((idx[i], rtt[i], cpu[i], ram[i], success[i], latency[i], throughput[i], label))

    rows.sort(key=lambda r: r[0])
    df = pd.DataFrame(rows, columns=["_order"] + FEATURES + ["label"]).drop(columns=["_order"])
    return df


def generate_all_sites(n_per_site=1500, seed=42):
    """Returns {site_name: DataFrame}. Each site's data never needs to be
    pooled with another site's to train a local model -- that separation is
    what makes the federated baseline in this project meaningful."""
    return {
        site: generate_site_data(site, n_per_site, seed=seed + i)
        for i, site in enumerate(SITE_REGIMES)
    }
