"""Zipfian key sampler for the workload profiles.

Rank r = 1..N is drawn with probability r^-s / H(N, s). Ranks are mapped to
order indexes through a fixed random permutation, so the hot orders are not
neighbours in the key space and not simply the first ones loaded. The exponent
s is calibrated so that about 90% of operations fall on the hottest 10% of keys
(master prompt 2.2) - uniform access is not allowed for primary runs.
"""
from __future__ import annotations

import numpy as np


def _cdf(n: int, s: float) -> np.ndarray:
    w = np.arange(1, n + 1, dtype=np.float64) ** -s
    c = np.cumsum(w)
    return c / c[-1]


def top_share(n: int, s: float, frac: float = 0.10) -> float:
    """Share of all operations that land on the hottest `frac` of the keys."""
    k = max(1, int(round(n * frac)))
    return float(_cdf(n, s)[k - 1])


def calibrate(n: int, frac: float = 0.10, target: float = 0.90, lo: float = 0.3, hi: float = 3.0,
              tol: float = 1e-6) -> float:
    """Exponent s so that the hottest `frac` of n keys get `target` of the traffic (bisection)."""
    for _ in range(100):
        mid = (lo + hi) / 2
        if top_share(n, mid, frac) < target:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return round((lo + hi) / 2, 6)


class Zipf:
    def __init__(self, n: int, s: float, perm_seed: int = 24205478):
        self.n = int(n)
        self.s = float(s)
        self.cdf = _cdf(self.n, self.s)
        # rank -> order index; fixed seed so the driver and the analysis agree on who is hot
        self.perm = np.random.default_rng(perm_seed).permutation(self.n)

    def ranks(self, rng: np.random.Generator, size: int) -> np.ndarray:
        """0-based ranks (0 = hottest key)."""
        return np.searchsorted(self.cdf, rng.random(size), side="left")

    def sample(self, rng: np.random.Generator, size: int) -> tuple[np.ndarray, np.ndarray]:
        r = self.ranks(rng, size)
        return self.perm[r], r

    def p(self, rank0: int) -> float:
        prev = self.cdf[rank0 - 1] if rank0 > 0 else 0.0
        return float(self.cdf[rank0] - prev)

    def top_share(self, frac: float = 0.10) -> float:
        return float(self.cdf[max(1, int(round(self.n * frac))) - 1])
