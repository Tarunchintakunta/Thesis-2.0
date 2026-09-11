"""Pilot -> sample size and idle-gap check (docs/ANALYSIS_PLAN.md section 7)."""
from __future__ import annotations

import math
from itertools import combinations

import pandas as pd
from scipy.stats import norm

from . import stats

START, END = "<!-- pilot-power:start -->", "<!-- pilot-power:end -->"
RUNTIMES = ("python", "nodejs", "java")


def n_per_group(sd: float, delta: float, alpha: float, power: float, are: float = 1.0) -> int:
    """Two-sample, two-sided normal approximation, divided by the rank test's ARE."""
    if sd <= 0:
        return 2
    z = norm.ppf(1 - alpha / 2) + norm.ppf(power)
    return int(math.ceil(2 * (z * sd / delta) ** 2 / are))


def _bool(s: pd.Series) -> pd.Series:
    return s.astype(str).str.lower().eq("true")


def pilot_report(m: pd.DataFrame, plan: dict, cfg: dict) -> dict:
    m = m.copy()
    for c in ("cold", "error", "intended_cold"):
        m[c] = _bool(m[c])
    pw = plan["power"]
    alpha = plan["alpha"] / len(plan["confirmatory_family"])  # Bonferroni: conservative for sizing
    x = m[(m["phase"] == "pilot_cold") & (m["role"] == "measure") & m["intended_cold"] & ~m["error"]]
    cells, sd = [], {}
    for fn, g in x.groupby("function"):
        cold = g.loc[g["cold"], "init_ms"]
        if len(cold) > 1:
            sd[fn] = float(cold.std(ddof=1))
        cells.append({"function": fn, "intended": int(len(g)), "cold": int(g["cold"].sum()),
                      "init_median_ms": float(cold.median()) if len(cold) else None, "init_sd_ms": sd.get(fn)})

    def pair_n(a, b):
        if a not in sd or b not in sd:
            return None
        pooled = math.sqrt((sd[a] ** 2 + sd[b] ** 2) / 2)
        return n_per_group(pooled, pw["min_effect_ms"], alpha, pw["target_power"], pw["mwu_are"])

    comparisons = {}
    for a, b in combinations([f"{r}-optimised" for r in RUNTIMES], 2):
        comparisons[f"H1: {a} vs {b}"] = pair_n(a, b)
    for r in RUNTIMES:
        comparisons[f"H2_{r}: {r}-default vs {r}-optimised"] = pair_n(f"{r}-default", f"{r}-optimised")
    floor = int(pw["min_n_per_cell"])
    h1 = [v for k, v in comparisons.items() if k.startswith("H1") and v]
    h2 = [v for k, v in comparisons.items() if k.startswith("H2") and v]
    planned = {k: int(ph["reps"]) for k, ph in cfg["phases"].items() if ph.get("kind") == "cold"}
    recommended = {k: max(floor, v) for k, v in planned.items()}  # exploratory phases: keep plan, >= 30
    if "runtime_compare" in planned:
        recommended["runtime_compare"] = max([floor, *h1])
    if "package_size" in planned:
        recommended["package_size"] = max([floor, *h2])

    probe = m[(m["phase"] == "idle_probe") & (m["role"] == "measure") & ~m["error"]]
    gaps = []
    for gap, g in probe.groupby("idle_gap_min"):
        k, n = int(g["cold"].sum()), int(len(g))
        gaps.append({"idle_gap_min": float(gap), "n": n, "cold": k, "cold_fraction": k / n if n else None,
                     "ci95": list(stats.wilson(k, n))})
    ok_gaps = [g["idle_gap_min"] for g in gaps if g["cold_fraction"] is not None and g["cold_fraction"] >= 0.95]
    return {
        "data_mode": sorted(m["data_mode"].dropna().unique().tolist()),
        "alpha_for_sizing": alpha, "power": pw["target_power"], "min_effect_ms": pw["min_effect_ms"],
        "cells": cells, "comparisons": comparisons, "planned_reps": planned, "recommended": recommended,
        "update_env_cold": [int(x["cold"].sum()), int(len(x))],
        "idle_probe": gaps, "recommended_idle_gap_min": min(ok_gaps) if ok_gaps else None,
    }


def report_markdown(r: dict, when: str) -> str:
    mode = ",".join(r["data_mode"])
    lines = [f"### Pilot result ({mode} data, {when})", ""]
    if "mock" in r["data_mode"]:
        lines += ["**SYNTHETIC mock pilot - these numbers only test the script. Re-run with the live pilot.**", ""]
    lines += [f"Sizing: two-sided alpha {r['alpha_for_sizing']:.3f} (0.05 / 5), power {r['power']:.2f}, "
              f"smallest effect {r['min_effect_ms']} ms, pooled SD of the two cells, rank-test ARE 0.864, "
              "never below 30.", "",
              "| cell | intended cold | really cold | median Init (ms) | SD (ms) |", "|---|---|---|---|---|"]
    for c in r["cells"]:
        med = "-" if c["init_median_ms"] is None else f"{c['init_median_ms']:.0f}"
        sd = "-" if c["init_sd_ms"] is None else f"{c['init_sd_ms']:.1f}"
        lines.append(f"| {c['function']} | {c['intended']} | {c['cold']} | {med} | {sd} |")
    lines += ["", "| comparison | n needed per cell |", "|---|---|"]
    for k, v in r["comparisons"].items():
        lines.append(f"| {k} | {v if v is not None else '-'} |")
    lines += ["", "| phase | planned | recommended | |", "|---|---|---|---|"]
    for k, v in r["planned_reps"].items():
        rec = r["recommended"][k]
        lines.append(f"| {k} | {v} | {rec} | {'ok' if v >= rec else 'raise'} |")
    k, n = r["update_env_cold"]
    lines += ["", f"Forced cold by configuration update: {k} of {n} intended-cold calls were really cold.", "",
              "| idle gap (min) | n | cold | cold fraction | Wilson 95% CI |", "|---|---|---|---|---|"]
    for g in r["idle_probe"]:
        lines.append(f"| {g['idle_gap_min']:g} | {g['n']} | {g['cold']} | {g['cold_fraction']:.2f} | "
                     f"{g['ci95'][0]:.2f}-{g['ci95'][1]:.2f} |")
    gap = r["recommended_idle_gap_min"]
    lines += ["", "Shortest idle gap where at least 95% of the probes were cold: "
              + (f"**{gap:g} minutes** (small n - check the interval)." if gap is not None
                 else "**none of the tested gaps** - keep force_cold: update_env.")]
    return "\n".join(lines) + "\n"


def replace_section(text: str, section: str) -> str:
    if START not in text or END not in text:
        raise ValueError("pilot-power markers not found")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    return f"{head}{START}\n{section}{END}{tail}"
