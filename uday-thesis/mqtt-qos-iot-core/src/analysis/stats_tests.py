"""Pre-registered tests: two-proportion z, chi-square, Mann–Whitney U, Holm–Bonferroni."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy import stats


def holm(pvalues: dict[str, float]) -> dict[str, float]:
    items = sorted(pvalues.items(), key=lambda kv: kv[1])
    m = len(items)
    adjusted: dict[str, float] = {}
    running = 0.0
    for i, (name, p) in enumerate(items):
        adj = min(1.0, (m - i) * float(p))
        running = max(running, adj)
        adjusted[name] = running
    return adjusted


def two_proportion_z(
    count1: int,
    n1: int,
    count2: int,
    n2: int,
    alternative: str = "greater",
) -> dict[str, Any]:
    """z-test of H1: p1 ? p2. Returns degenerate result when SE is 0."""
    if n1 <= 0 or n2 <= 0:
        return {"z": float("nan"), "p": float("nan"), "note": "empty"}
    p1 = float(count1) / float(n1)
    p2 = float(count2) / float(n2)
    p = (float(count1) + float(count2)) / float(n1 + n2)
    se = math.sqrt(p * (1.0 - p) * (1.0 / n1 + 1.0 / n2))
    if se == 0.0:
        return {"z": 0.0, "p": 1.0, "p1": p1, "p2": p2, "note": "degenerate_se0"}
    z = (p1 - p2) / se
    if alternative == "greater":
        pval = float(stats.norm.sf(z))
    elif alternative == "less":
        pval = float(stats.norm.cdf(z))
    else:
        pval = float(2.0 * stats.norm.sf(abs(z)))
    return {"z": float(z), "p": pval, "p1": p1, "p2": p2}


def mannwhitney(
    a: list[float],
    b: list[float],
    alternative: str = "two-sided",
) -> dict[str, Any]:
    x = np.asarray([v for v in a if np.isfinite(v)], dtype=float)
    y = np.asarray([v for v in b if np.isfinite(v)], dtype=float)
    if x.size == 0 or y.size == 0:
        return {"u": float("nan"), "p": float("nan"), "rbc": float("nan"), "note": "empty"}
    res = stats.mannwhitneyu(x, y, alternative=alternative)
    n1, n2 = int(x.size), int(y.size)
    rbc = 1.0 - (2.0 * float(res.statistic)) / (n1 * n2)
    return {"u": float(res.statistic), "p": float(res.pvalue), "rbc": float(rbc)}


def chi2_loss_qos_by_disconnect(cells: list[dict[str, Any]]) -> dict[str, Any]:
    """8×2 table: (qos, disconnect) × (lost, delivered) pooled over rate."""
    buckets: dict[tuple[int, int], list[int]] = {}
    for row in cells:
        key = (int(row["qos"]), int(row["disconnect_s"]))
        lost = int(row.get("n_lost", 0))
        pub = int(row.get("n_published", 0))
        buckets.setdefault(key, [0, 0])
        buckets[key][0] += lost
        buckets[key][1] += max(0, pub - lost)

    labels = sorted(buckets.keys())
    if not labels:
        return {"chi2": float("nan"), "p": float("nan"), "dof": 0, "note": "empty"}
    table = np.asarray([buckets[k] for k in labels], dtype=float)
    if table.size == 0 or table.shape[0] < 2:
        return {"chi2": float("nan"), "p": float("nan"), "dof": 0, "note": "empty", "table": table.tolist()}
    chi2, p, dof, _ = stats.chi2_contingency(table)
    return {
        "chi2": float(chi2),
        "p": float(p),
        "dof": int(dof),
        "labels": [f"qos{q}_d{d}" for q, d in labels],
        "table": table.tolist(),
    }


def run_confirmatory(
    cells: list[dict[str, Any]],
    run_rows: list[dict[str, Any]],
    alpha: float = 0.05,
) -> dict[str, Any]:
    tests: list[dict[str, Any]] = []
    pmap: dict[str, float] = {}

    by_cell = {str(r["cell_id"]): r for r in cells}
    disconnects = sorted({int(c["disconnect_s"]) for c in cells})
    rates = sorted({str(c["rate_mode"]) for c in cells})

    for d in disconnects:
        for rate in rates:
            a = by_cell.get(f"qos0_d{d}_{rate}")
            b = by_cell.get(f"qos1_d{d}_{rate}")
            if not a or not b:
                continue
            name = f"loss_qos0_gt_qos1_d{d}_{rate}"
            z = two_proportion_z(
                int(a["n_lost"]),
                int(a["n_published"]),
                int(b["n_lost"]),
                int(b["n_published"]),
                alternative="greater",
            )
            tests.append(
                {
                    "name": name,
                    "family": "primary",
                    "metric": "loss_rate",
                    **z,
                }
            )
            if math.isfinite(z["p"]):
                pmap[name] = float(z["p"])

            dname = f"dup_qos1_gt_qos0_d{d}_{rate}"
            z2 = two_proportion_z(
                int(b["n_duplicate_ids"]),
                int(b["n_published"]),
                int(a["n_duplicate_ids"]),
                int(a["n_published"]),
                alternative="greater",
            )
            tests.append({"name": dname, "family": "secondary", "metric": "duplicate_id_rate", **z2})
            if math.isfinite(z2["p"]):
                pmap[dname] = float(z2["p"])

            l0 = list(a.get("latencies_ms") or [])
            l1 = list(b.get("latencies_ms") or [])
            # Fall back to run_rows latencies if cell rows were stripped.
            if not l0 or not l1:
                l0 = [
                    x
                    for r in run_rows
                    if int(r["qos"]) == 0 and int(r["disconnect_s"]) == d and r["rate_mode"] == rate
                    for x in (r.get("latencies_ms") or [])
                ]
                l1 = [
                    x
                    for r in run_rows
                    if int(r["qos"]) == 1 and int(r["disconnect_s"]) == d and r["rate_mode"] == rate
                    for x in (r.get("latencies_ms") or [])
                ]
            lname = f"latency_qos_diff_d{d}_{rate}"
            mw = mannwhitney(l0, l1, alternative="two-sided")
            tests.append({"name": lname, "family": "secondary", "metric": "e2e_latency_ms", **mw})
            if math.isfinite(mw["p"]):
                pmap[lname] = float(mw["p"])

    chi = chi2_loss_qos_by_disconnect(cells)
    tests.append({"name": "loss_qos_x_disconnect", "family": "primary", "metric": "loss_count", **chi})
    if math.isfinite(chi.get("p", float("nan"))):
        pmap["loss_qos_x_disconnect"] = float(chi["p"])

    adj = holm(pmap)
    for t in tests:
        p = t.get("p")
        if isinstance(p, float) and math.isfinite(p) and t["name"] in adj:
            t["p_adjusted"] = adj[t["name"]]
            t["decision"] = "reject H0" if adj[t["name"]] < alpha else "fail to reject H0"

    return {
        "alpha": alpha,
        "adjustment": "holm-bonferroni",
        "n_tests": len(pmap),
        "measurement_kind": "Mock or live according to measurement_kind. Mock results are not AWS evidence.",
        "confirmatory": tests,
        "p_adjusted": adj,
        "note": "Mock or live according to measurement_kind. Mock results are not AWS evidence.",
    }
