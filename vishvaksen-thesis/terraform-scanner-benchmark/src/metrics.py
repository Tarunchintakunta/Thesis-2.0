"""Precision / recall / F1 / FN-rate helpers."""

from __future__ import annotations

import math
from typing import Iterable


def confusion(y_true: Iterable[int], y_pred: Iterable[int]) -> dict[str, int]:
    tp = fp = tn = fn = 0
    for t, p in zip(y_true, y_pred, strict=True):
        if t == 1 and p == 1:
            tp += 1
        elif t == 0 and p == 1:
            fp += 1
        elif t == 0 and p == 0:
            tn += 1
        else:
            fn += 1
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "n": tp + fp + tn + fn}


def rates(c: dict[str, int]) -> dict[str, float]:
    tp, fp, fn = c["tp"], c["fp"], c["fn"]
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
    fnr = fn / (fn + tp) if (fn + tp) else 0.0
    return {
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "fn_rate": fnr,
        "identified_pct": rec * 100.0,
    }


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    phat = successes / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = phat + z2 / (2 * n)
    adj = z * math.sqrt((phat * (1 - phat) + z2 / (4 * n)) / n)
    lo = (centre - adj) / denom
    hi = (centre + adj) / denom
    return (max(0.0, lo), min(1.0, hi))


def mcnemar(b: int, c: int) -> dict[str, float]:
    """McNemar exact (binomial) two-sided p on discordant pairs b, c."""
    n = b + c
    if n == 0:
        return {"b": float(b), "c": float(c), "p_two_sided": 1.0}
    k = min(b, c)
    # P(X <= k) + P(X >= n-k) for X ~ Binom(n, 0.5)
    p_tail = 0.0
    for i in range(0, k + 1):
        p_tail += math.comb(n, i)
    p = min(1.0, 2.0 * p_tail / (2**n))
    return {"b": float(b), "c": float(c), "p_two_sided": p}


def holm_bonferroni(
    tests: list[dict], alpha: float = 0.05
) -> list[dict]:
    """Holm–Bonferroni step-down on pre-registered tests (α default 0.05).

    Each input dict must include ``p_two_sided``. Returns the same dicts
    annotated with holm_rank, holm_threshold, holm_adjusted_p, and
    holm_reject_alpha_0_05. Adjusted p uses the standard cumulative max of
    (m−j+1)·p_(j), capped at 1.
    """
    m = len(tests)
    if m == 0:
        return []
    order = sorted(range(m), key=lambda i: float(tests[i]["p_two_sided"]))
    out: list[dict | None] = [None] * m
    adj_run = 0.0
    still_rejecting = True
    for rank0, idx in enumerate(order):
        j = rank0 + 1
        raw = float(tests[idx]["p_two_sided"])
        thresh = alpha / (m - j + 1)
        adj = min(1.0, (m - j + 1) * raw)
        adj_run = max(adj_run, adj)
        reject = still_rejecting and raw <= thresh
        if not reject:
            still_rejecting = False
        out[idx] = {
            **tests[idx],
            "holm_rank": j,
            "holm_threshold": thresh,
            "holm_adjusted_p": adj_run,
            "holm_reject_alpha_0_05": reject,
        }
    return [r for r in out if r is not None]  # type: ignore[misc]
