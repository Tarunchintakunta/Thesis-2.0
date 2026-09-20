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
        running = max(running, min(1.0, (m - i) * p))
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
        return {"z": float("nan"), "p": float("nan"), "p1": float("nan"), "p2": float("nan"), "note": "empty"}
    p1 = count1 / n1
    p2 = count2 / n2
    p = (count1 + count2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return {"z": 0.0, "p": 1.0, "p1": p1, "p2": p2, "note": "degenerate_se0"}
    z = (p1 - p2) / se
    if alternative == "greater":
        pval = float(stats.norm.sf(z))
    elif alternative == "less":
        pval = float(stats.norm.cdf(z))
    else:
        pval = float(2 * stats.norm.sf(abs(z)))
    return {"z": float(z), "p": pval, "p1": p1, "p2": p2, "n1": n1, "n2": n2, "c1": count1, "c2": count2, "note": ""}


def mannwhitney(a: list[float], b: list[float], alternative: str = "two-sided") -> dict[str, Any]:
    x = np.asarray(a, dtype=float)
    y = np.asarray(b, dtype=float)
    x = x[np.isfinite(x)]
    y = y[np.isfinite(y)]
    if x.size == 0 or y.size == 0:
        return {"u": float("nan"), "p": float("nan"), "rbc": float("nan"), "note": "empty"}
    res = stats.mannwhitneyu(x, y, alternative=alternative)
    n1, n2 = x.size, y.size
    rbc = 1.0 - (2.0 * float(res.statistic)) / (n1 * n2)
    return {
        "u": float(res.statistic),
        "p": float(res.pvalue),
        "rbc": float(rbc),
        "n1": int(n1),
        "n2": int(n2),
        "note": "",
    }


def chi2_loss_qos_by_disconnect(cells: list[dict[str, Any]]) -> dict[str, Any]:
    """8×2 table: (qos, disconnect) × (lost, delivered) pooled over rate."""
    buckets: dict[tuple[int, int], list[int]] = {}
    for row in cells:
        key = (int(row["qos"]), int(row["disconnect_s"]))
        lost, pub = buckets.get(key, [0, 0])
        lost += int(row["n_lost"])
        pub += int(row["n_published"])
        buckets[key] = [lost, pub]
    table = []
    labels = []
    for key in sorted(buckets):
        lost, pub = buckets[key]
        table.append([lost, max(0, pub - lost)])
        labels.append(f"qos{key[0]}_d{key[1]}")
    arr = np.asarray(table, dtype=float)
    if arr.size == 0 or arr.shape[0] < 2:
        return {"chi2": float("nan"), "p": float("nan"), "dof": 0, "labels": labels, "note": "empty"}
    chi2, p, dof, _ = stats.chi2_contingency(arr)
    return {"chi2": float(chi2), "p": float(p), "dof": int(dof), "labels": labels, "note": "", "table": table}


def run_confirmatory(cells: list[dict[str, Any]], run_rows: list[dict[str, Any]], alpha: float = 0.05) -> dict[str, Any]:
    tests: list[dict[str, Any]] = []
    pmap: dict[str, float] = {}

    by_cell = {r["cell_id"]: r for r in cells}
    disconnects = sorted({int(r["disconnect_s"]) for r in cells})
    rates = sorted({str(r["rate_mode"]) for r in cells})

    for d in disconnects:
        for rate in rates:
            a = by_cell.get(f"qos0_d{d}_{rate}")
            b = by_cell.get(f"qos1_d{d}_{rate}")
            if not a or not b:
                continue
            name = f"loss_qos0_gt_qos1_d{d}_{rate}"
            z = two_proportion_z(a["n_lost"], a["n_published"], b["n_lost"], b["n_published"], alternative="greater")
            tests.append({"name": name, "family": "primary", "dv": "loss_rate", **z})
            if math.isfinite(z["p"]):
                pmap[name] = z["p"]

            dname = f"dup_qos1_gt_qos0_d{d}_{rate}"
            z2 = two_proportion_z(b["n_duplicate_ids"], b["n_published"], a["n_duplicate_ids"], a["n_published"], alternative="greater")
            tests.append({"name": dname, "family": "secondary", "dv": "duplicate_id_rate", **z2})
            if math.isfinite(z2["p"]):
                pmap[dname] = z2["p"]

            l0 = [x for r in run_rows if r["qos"] == 0 and r["disconnect_s"] == d and r["rate_mode"] == rate for x in r.get("latencies_ms", [])]
            l1 = [x for r in run_rows if r["qos"] == 1 and r["disconnect_s"] == d and r["rate_mode"] == rate for x in r.get("latencies_ms", [])]
            lname = f"latency_qos_diff_d{d}_{rate}"
            mw = mannwhitney(l0, l1, alternative="two-sided")
            tests.append({"name": lname, "family": "secondary", "dv": "e2e_latency_ms", **mw})
            if math.isfinite(mw["p"]):
                pmap[lname] = mw["p"]

    chi = chi2_loss_qos_by_disconnect(cells)
    tests.append({"name": "loss_qos_x_disconnect", "family": "primary", "dv": "loss_count", **chi})
    if math.isfinite(chi["p"]):
        pmap["loss_qos_x_disconnect"] = chi["p"]

    adj = holm(pmap)
    for t in tests:
        t["p_adjusted"] = adj.get(t["name"], t.get("p"))
        p = t.get("p_adjusted")
        t["decision"] = "reject H0" if isinstance(p, (int, float)) and math.isfinite(p) and p < alpha else "fail to reject H0"
        t["alpha"] = alpha

    return {
        "alpha": alpha,
        "adjustment": "holm-bonferroni",
        "n_tests": len(tests),
        "measurement_kind": run_rows[0]["measurement_kind"] if run_rows else "",
        "confirmatory": tests,
        "note": "Mock or live according to measurement_kind. Mock results are not AWS evidence.",
    }
