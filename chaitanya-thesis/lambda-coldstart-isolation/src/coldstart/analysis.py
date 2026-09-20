"""Hypothesis tests, tables, figures and the decision matrix (docs/ANALYSIS_PLAN.md).

Input is the processed dataset with costs (scripts/cost_model.py). Live and
mock rows are never mixed - the analysis refuses. Mock output is stamped
SYNTHETIC on every figure and table so it cannot be mistaken for a result.
"""
from __future__ import annotations

import json
import math
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from . import stats  # noqa: E402
from .config import ROOT  # noqa: E402

RUNTIMES = ["python", "nodejs", "java"]
COLOURS = {"python": "#3572A5", "nodejs": "#3c873a", "java": "#b07219"}
LABELS = {"mock": "SYNTHETIC mock data - NOT measured (pipeline test only)",
          "live": "measured on AWS Lambda, eu-west-1, arm64"}
BAND_COLOURS = {"adopt": "#b7e1b0", "situational": "#ffe29a", "avoid": "#f4b6b6", "not tested": "#e6e6e6"}
NAN = float("nan")


def load_plan(path: str | Path = ROOT / "configs/analysis_plan.yaml") -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _med(x) -> float:
    x = pd.Series(x, dtype=float).dropna()
    return float(x.median()) if len(x) else NAN


def _mean(x) -> float:
    x = pd.Series(x, dtype=float).dropna()
    return float(x.mean()) if len(x) else NAN


def _nan(v) -> bool:
    return v is None or (isinstance(v, float) and math.isnan(v))


def band(sig, effect, threshold, dcost, max_free) -> str:
    if sig is None or _nan(effect):
        return "not tested"
    if not sig or effect < threshold:
        return "avoid"
    return "adopt" if (not _nan(dcost) and dcost <= max_free) else "situational"


class Analysis:
    def __init__(self, costs: pd.DataFrame, plan: dict, cfg: dict):
        modes = set(costs["data_mode"].dropna())
        if len(modes) != 1:
            raise ValueError(f"expected one data mode, found {sorted(modes)} - never mix live and mock rows")
        self.mode = modes.pop()
        self.label = LABELS.get(self.mode, self.mode)
        m = costs.copy()
        for col in ("cold", "error"):
            m[col] = m[col].astype(str).str.lower().eq("true")
        m["intended_cold"] = m["intended_cold"].astype(str).str.lower().eq("true")
        self.m = m
        self.plan = plan
        self.cfg = cfg
        self.alpha = float(plan["alpha"])
        self.tests: dict[str, dict] = {}
        self.notes: list[str] = []

    # ---- row selection ------------------------------------------------------------------
    def sel(self, phase, roles=("measure",), **eq) -> pd.DataFrame:
        x = self.m[(self.m["phase"] == phase) & self.m["role"].isin(roles) & ~self.m["error"]]
        for k, v in eq.items():
            x = x[x[k] == v]
        return x

    def colds(self, phase, **eq) -> pd.DataFrame:
        x = self.sel(phase, ("measure",), **eq)
        return x[x["cold"] & x["intended_cold"]]

    def warms(self, phase, **eq) -> pd.DataFrame:
        x = self.sel(phase, ("measure", "follow_up"), **eq)
        return x[~x["cold"]]

    # ---- descriptive --------------------------------------------------------------------
    def phase_a(self) -> pd.DataFrame:
        x = self.sel("baseline")
        x = x[~x["cold"]]
        rows = []
        for mem, g in x.groupby("memory_mb"):
            d = stats.describe(g["duration_ms"])
            rows.append({"memory_mb": int(mem), "n": d["n"], "duration_p50_ms": d["p50"],
                         "duration_p95_ms": d["p95"], "duration_p99_ms": d["p99"],
                         "billed_p50_ms": _med(g["effective_billed_ms"]),
                         "cost_per_1k_usd": _mean(g["cost_usd"]) * 1000})
        return pd.DataFrame(rows)

    def summary_by_cell(self) -> pd.DataFrame:
        rows = []
        x = self.m[self.m["role"].isin(["measure", "follow_up"])]
        for (phase, fn, mem), g in x.groupby(["phase", "function", "memory_mb"]):
            ok = g[~g["error"]]
            cold = ok[ok["cold"] & ok["intended_cold"] & (ok["role"] == "measure")]
            warm = ok[~ok["cold"]]
            ic = ok[(ok["role"] == "measure") & ok["intended_cold"]]
            di, dr = stats.describe(cold["init_ms"]), stats.describe(ok["rtt_ms"])
            rows.append({
                "phase": phase, "function": fn, "memory_mb": int(mem), "calls": len(g),
                "error_rate": float(g["error"].mean()),
                "cold_n": di["n"], "init_p50_ms": di.get("p50", NAN), "init_p95_ms": di.get("p95", NAN),
                "init_p99_ms": di.get("p99", NAN),
                "cold_duration_p50_ms": _med(cold["duration_ms"]),
                "warm_duration_p50_ms": _med(warm["duration_ms"]),
                "rtt_p50_ms": dr.get("p50", NAN), "rtt_p95_ms": dr.get("p95", NAN), "rtt_p99_ms": dr.get("p99", NAN),
                "cold_fraction": float(ok["cold"].mean()) if len(ok) else NAN,
                "intended_cold_came_back_warm": int((~ic["cold"]).sum()),
                "cost_per_1k_usd": _mean(ok["cost_usd"]) * 1000,
            })
        return pd.DataFrame(rows)

    # ---- hypothesis tests ---------------------------------------------------------------
    def run_tests(self) -> dict:
        t = self.tests
        x = self.colds("runtime_compare")
        groups = {r: x.loc[x["runtime"] == r, "init_ms"].to_numpy() for r in RUNTIMES
                  if (x["runtime"] == r).sum() >= 3}
        if len(groups) >= 2:
            t["H1"] = stats.compare_many(groups)
        for r in RUNTIMES:
            dft = self.colds("package_size", runtime=r, variant="default")["init_ms"]
            opt = self.colds("package_size", runtime=r, variant="optimised")["init_ms"]
            if len(dft) >= 3 and len(opt) >= 3:
                t[f"H2_{r}"] = stats.compare_two(dft, opt)
            if r == "python":
                bc = self.colds("package_size", runtime=r, variant="bytecode")["init_ms"]
                if len(bc) >= 3:
                    if len(dft) >= 3:
                        t["H2_python_default_to_bytecode"] = stats.compare_two(dft, bc)
                    if len(opt) >= 3:
                        t["H2_python_bytecode_to_optimised"] = stats.compare_two(bc, opt)
                else:
                    self.notes.append(
                        "python-bytecode dropped from H2 (valid Init n<3; Unhandled on live lite)"
                    )
        w = self.sel("warming")
        if len(w) and {"on", "off"} <= set(w["warming"]):
            per = w.groupby(["block", "warming"])["cold"].mean().unstack("warming").dropna()
            if len(per) >= 3:
                t["H3"] = {**stats.compare_paired(per["on"], per["off"]), "blocks": int(len(per)),
                           "mean_cold_fraction_on": float(per["on"].mean()),
                           "mean_cold_fraction_off": float(per["off"].mean())}
            on, off = w[w["warming"] == "on"], w[w["warming"] == "off"]
            t["H3_fisher"] = {**stats.fisher_2x2(int(on["cold"].sum()), len(on), int(off["cold"].sum()), len(off)),
                              "family": "descriptive"}
        for r in RUNTIMES:
            x = self.colds("memory", runtime=r)
            g = {int(k): v["init_ms"].to_numpy() for k, v in x.groupby("memory_mb") if len(v) >= 3}
            if len(g) >= 2:
                t[f"H4_{r}"] = stats.compare_many(g)
        for r in RUNTIMES:
            a = self.colds("combined", runtime=r, variant="default", memory_mb=128)["init_ms"]
            b = self.colds("combined", runtime=r, variant="optimised", memory_mb=1024)["init_ms"]
            if len(a) >= 3 and len(b) >= 3:
                t[f"combined_{r}"] = stats.compare_two(a, b)
        self._holm(self.plan["confirmatory_family"], "confirmatory")
        for fam, members in self.plan["exploratory_families"].items():
            self._holm(members, f"exploratory:{fam}")
        if t.get("H1", {}).get("reject"):
            x = self.colds("runtime_compare")
            pairs = {}
            for a, b in combinations([r for r in RUNTIMES if r in t["H1"]["groups"]], 2):
                pairs[f"H1_posthoc_{a}_vs_{b}"] = stats.compare_two(
                    x.loc[x["runtime"] == a, "init_ms"], x.loc[x["runtime"] == b, "init_ms"])
            t.update(pairs)
            self._holm(list(pairs), "posthoc:H1")
        return t

    def _holm(self, members, family) -> None:
        present = {k: self.tests[k]["p"] for k in members if k in self.tests}
        missing = [k for k in members if k not in self.tests]
        if missing:
            self.notes.append(f"{family}: no data for {', '.join(missing)} (family size shrinks to {len(present)})")
        for k, p_adj in stats.holm(present).items():
            self.tests[k].update(family=family, p_holm=p_adj, reject=bool(p_adj < self.alpha))

    # ---- decision matrix ----------------------------------------------------------------
    def _mix(self, dc, dw, f) -> float:
        if _nan(dc):
            return NAN
        return 1000 * (f * dc + (1 - f) * (0.0 if _nan(dw) else dw))

    def decision_matrix(self) -> pd.DataFrame:
        pr = self.plan["practical"]
        thr, drop_thr, free = pr["min_init_saving_ms"], pr["min_cold_fraction_drop"], pr["max_free_cost_usd_per_1k"]
        off = self.sel("warming", warming="off")
        f = float(off["cold"].mean()) if len(off) else NAN
        if _nan(f):
            self.notes.append("no warming data: per-1k cost treats every invocation as cold (f = 1)")
            f = 1.0
        self.cold_fraction_used = f
        rows = []

        def test_of(key):
            tt = self.tests.get(key)
            return (tt.get("reject"), tt.get("p_holm", NAN)) if tt else (None, NAN)

        x = self.colds("runtime_compare")
        med = x.groupby("runtime")["init_ms"].median()
        if len(med) >= 2:
            slow, fast = med.idxmax(), med.idxmin()
            saving = float(med[slow] - med[fast])
            dc = _mean(self.colds("runtime_compare", runtime=fast)["cost_usd"]) - _mean(
                self.colds("runtime_compare", runtime=slow)["cost_usd"])
            dw = _mean(self.warms("runtime_compare", runtime=fast)["cost_usd"]) - _mean(
                self.warms("runtime_compare", runtime=slow)["cost_usd"])
            sig, p = test_of("H1")
            dcost = self._mix(dc, dw, f)
            rows.append({"control": "Switch runtime", "scope": f"{slow} -> {fast}", "init_delta_ms": saving,
                         "cold_freq_delta": 0.0, "ms_saved_per_invocation": saving * f,
                         "delta_cost_per_1k_usd": dcost, "test": "H1", "p_holm": p,
                         "band": band(sig, saving, thr, dcost, free),
                         "when_to_use": "new functions where the team is free to pick the language"})
        for r in RUNTIMES:
            d, o = self.colds("package_size", runtime=r, variant="default"), self.colds(
                "package_size", runtime=r, variant="optimised")
            if len(d) and len(o):
                saving = _med(d["init_ms"]) - _med(o["init_ms"])
                dc = _mean(o["cost_usd"]) - _mean(d["cost_usd"])
                dw = _mean(self.warms("package_size", runtime=r, variant="optimised")["cost_usd"]) - _mean(
                    self.warms("package_size", runtime=r, variant="default")["cost_usd"])
                sig, p = test_of(f"H2_{r}")
                dcost = self._mix(dc, dw, f)
                rows.append({"control": "Prune package", "scope": f"{r} default->optimised", "init_delta_ms": saving,
                             "cold_freq_delta": 0.0,
                             "ms_saved_per_invocation": saving * f, "delta_cost_per_1k_usd": dcost,
                             "test": f"H2_{r}", "p_holm": p, "band": band(sig, saving, thr, dcost, free),
                             "when_to_use": "see thesis notes"})
        lo, hi = self.plan["memory_contrast"]
        for r in RUNTIMES:
            a, b = self.colds("memory", runtime=r, memory_mb=lo), self.colds("memory", runtime=r, memory_mb=hi)
            if len(a) and len(b):
                saving = _med(a["init_ms"]) - _med(b["init_ms"])
                dc = _mean(b["cost_usd"]) - _mean(a["cost_usd"])
                dw = _mean(self.warms("memory", runtime=r, memory_mb=hi)["cost_usd"]) - _mean(
                    self.warms("memory", runtime=r, memory_mb=lo)["cost_usd"])
                sig, p = test_of(f"H4_{r}")
                dcost = self._mix(dc, dw, f)
                rows.append({"control": "Raise memory (exploratory)", "scope": f"{r} {lo}->{hi} MB",
                             "init_delta_ms": saving, "cold_freq_delta": 0.0,
                             "ms_saved_per_invocation": saving * f, "delta_cost_per_1k_usd": dcost,
                             "test": f"H4_{r}", "p_holm": p, "band": band(sig, saving, thr, dcost, free),
                             "when_to_use": "when cold p95 matters more than the price per GB-s"})
        w = self.sel("warming")
        if len(w) and {"on", "off"} <= set(w["warming"]):
            on, off = w[w["warming"] == "on"], w[w["warming"] == "off"]
            f_on, f_off = float(on["cold"].mean()), float(off["cold"].mean())
            med_off = _med(off.loc[off["cold"], "init_ms"])
            ph = self.cfg["phases"]["warming"]
            pings = self.m[self.m["role"] == "warmer_ping"]
            ping_cost = _mean(pings["cost_usd"])
            pings_per_h = 60.0 / float(ph["warmer_rate_min"])
            calls_per_h = 3600.0 / float(ph["mean_gap_s"])
            ping_per_1k = 1000 * pings_per_h / calls_per_h * (0.0 if _nan(ping_cost) else ping_cost)
            extra_cold_cost = _mean(w.loc[w["cold"], "cost_usd"]) - _mean(w.loc[~w["cold"], "cost_usd"])
            saved_per_1k = 1000 * (f_off - f_on) * (0.0 if _nan(extra_cold_cost) else extra_cold_cost)
            dcost = ping_per_1k - saved_per_1k
            sig, p = test_of("H3")
            drop = f_off - f_on
            init_delta = _med(off.loc[off["cold"], "init_ms"]) - _med(on.loc[on["cold"], "init_ms"])
            rows.append({"control": "Low-frequency warming", "scope": f"EventBridge rate({ph['warmer_rate_min']} min)",
                         "init_delta_ms": init_delta, "cold_freq_delta": f_on - f_off,
                         "ms_saved_per_invocation": drop * med_off if not _nan(med_off) else NAN,
                         "delta_cost_per_1k_usd": dcost, "test": "H3", "p_holm": p,
                         "band": band(sig, drop, drop_thr, dcost, free),
                         "when_to_use": "sparse, latency-sensitive traffic; one ping keeps one environment, so bursts still go cold"})
        for r in RUNTIMES:
            a = self.colds("combined", runtime=r, variant="default", memory_mb=128)
            b = self.colds("combined", runtime=r, variant="optimised", memory_mb=1024)
            if len(a) and len(b):
                saving = _med(a["init_ms"]) - _med(b["init_ms"])
                dc = _mean(b["cost_usd"]) - _mean(a["cost_usd"])
                dw = _mean(self.warms("combined", runtime=r, variant="optimised", memory_mb=1024)["cost_usd"]) - _mean(
                    self.warms("combined", runtime=r, variant="default", memory_mb=128)["cost_usd"])
                sig, p = test_of(f"combined_{r}")
                dcost = self._mix(dc, dw, f)
                rows.append({"control": "Combined free controls", "scope": f"{r}: default@128 -> optimised@1024",
                             "init_delta_ms": saving, "cold_freq_delta": 0.0,
                             "ms_saved_per_invocation": saving * f, "delta_cost_per_1k_usd": dcost,
                             "test": f"combined_{r}", "p_holm": p, "band": band(sig, saving, thr, dcost, free),
                             "when_to_use": "default starting point for a new function"})
        rows.append({"control": "(Future) Provisioned concurrency", "scope": "not measured", "init_delta_ms": NAN,
                     "cold_freq_delta": NAN, "ms_saved_per_invocation": NAN, "delta_cost_per_1k_usd": NAN,
                     "test": "-", "p_holm": NAN, "band": "not tested",
                     "when_to_use": "paid feature, out of the primary scope (future work)"})
        return pd.DataFrame(rows)

    # ---- figures ------------------------------------------------------------------------
    def _stamp(self, fig) -> None:
        fig.text(0.01, 0.005, self.label, fontsize=7, color="#555555")
        if self.mode != "live":
            fig.text(0.5, 0.5, "SYNTHETIC - NOT MEASURED", fontsize=34, color="red", alpha=0.15,
                     rotation=25, ha="center", va="center")

    def _save(self, fig, path: Path) -> None:
        self._stamp(fig)
        fig.tight_layout(rect=(0, 0.03, 1, 1))
        fig.savefig(path, dpi=130)
        plt.close(fig)

    def figures(self, out: Path, dm: pd.DataFrame) -> list[str]:
        out.mkdir(parents=True, exist_ok=True)
        made = []
        pa = self.phase_a()
        if len(pa):
            fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.6))
            a1.errorbar(pa["memory_mb"], pa["duration_p50_ms"],
                        yerr=[np.zeros(len(pa)), pa["duration_p95_ms"] - pa["duration_p50_ms"]], marker="o", capsize=3)
            a1.set(xscale="log", xlabel="memory (MB)", ylabel="warm Duration p50 (ms), bar to p95",
                   title="Phase A: duration vs memory")
            a2.plot(pa["memory_mb"], pa["cost_per_1k_usd"], marker="s", color="#aa5500")
            a2.set(xscale="log", xlabel="memory (MB)", ylabel="USD per 1,000 invocations", title="Phase A: cost vs memory")
            for a in (a1, a2):
                a.set_xticks(pa["memory_mb"], [str(v) for v in pa["memory_mb"]])
            self._save(fig, out / "baseline_style_duration_cost.png")
            made.append("baseline_style_duration_cost.png")
        x = self.colds("runtime_compare")
        if len(x):
            fig, ax = plt.subplots(figsize=(6, 3.8))
            data = [x.loc[x["runtime"] == r, "init_ms"] for r in RUNTIMES]
            ax.boxplot(data, tick_labels=RUNTIMES, showfliers=False)
            for i, (r, d) in enumerate(zip(RUNTIMES, data, strict=True), start=1):
                ax.scatter(np.random.default_rng(i).normal(i, 0.05, len(d)), d, s=6, alpha=0.4, color=COLOURS[r])
            ax.set(ylabel="Init Duration (ms)", title="Init Duration by runtime (optimised, 1024 MB, cold only)")
            self._save(fig, out / "init_by_runtime.png")
            made.append("init_by_runtime.png")
        x = self.colds("package_size")
        if len(x):
            fig, ax = plt.subplots(figsize=(7, 3.8))
            pos, data, labels = [], [], []
            for i, r in enumerate(RUNTIMES):
                variants_to_check = ["default", "bytecode", "optimised"] if r == "python" else ["default", "optimised"]
                for j, v in enumerate(variants_to_check):
                    data.append(x.loc[(x["runtime"] == r) & (x["variant"] == v), "init_ms"])
                    pos.append(i * 4 + j)
                    labels.append(f"{r}\n{v}")
            ax.boxplot(data, positions=pos, tick_labels=labels, showfliers=False)
            ax.set(ylabel="Init Duration (ms)", title="Package size: default vs optimised (1024 MB, cold only)")
            self._save(fig, out / "package_size_effect.png")
            made.append("package_size_effect.png")
        x = self.colds("memory")
        if len(x):
            fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.6))
            for r in RUNTIMES:
                g = x[x["runtime"] == r].groupby("memory_mb")["init_ms"]
                if len(g):
                    a1.plot(g.median().index, g.median().values, marker="o", color=COLOURS[r], label=r)
                wm = self.warms("memory", runtime=r).groupby("memory_mb")["duration_ms"].median()
                if len(wm):
                    a2.plot(wm.index, wm.values, marker="o", color=COLOURS[r], label=r)
            a1.set(xscale="log", xlabel="memory (MB)", ylabel="Init Duration p50 (ms)", title="Memory vs Init (exploratory)")
            a2.set(xscale="log", yscale="log", xlabel="memory (MB)", ylabel="warm Duration p50 (ms)",
                   title="Memory vs warm Duration")
            a1.legend()
            self._save(fig, out / "memory_effect.png")
            made.append("memory_effect.png")
        w = self.sel("warming")
        if len(w) and {"on", "off"} <= set(w["warming"]):
            fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.6))
            arms = ["off", "on"]
            k = [int(w.loc[w["warming"] == a, "cold"].sum()) for a in arms]
            n = [int((w["warming"] == a).sum()) for a in arms]
            fr = [ki / ni for ki, ni in zip(k, n, strict=True)]
            ci = [stats.wilson(ki, ni) for ki, ni in zip(k, n, strict=True)]
            a1.bar(arms, fr, yerr=[[f_ - c[0] for f_, c in zip(fr, ci, strict=True)],
                                   [c[1] - f_ for f_, c in zip(fr, ci, strict=True)]], capsize=4,
                   color=["#999999", "#4c9a2a"])
            a1.set(ylabel="cold-start fraction", title="Warming off vs on (Wilson 95% CI)", ylim=(0, 1))
            per = w.groupby(["block", "warming"])["cold"].mean().unstack("warming").dropna()
            for _, row in per.iterrows():
                a2.plot([0, 1], [row["off"], row["on"]], color="#777777", alpha=0.4)
            a2.set(xticks=[0, 1], xticklabels=arms, ylabel="cold fraction per block", title="Paired 20-minute blocks")
            self._save(fig, out / "warming_frequency.png")
            made.append("warming_frequency.png")
        b = self.sel("burst")
        if len(b):
            fig, ax = plt.subplots(figsize=(6, 3.6))
            for i, r in enumerate(RUNTIMES):
                rt = b.loc[b["runtime"] == r, "rtt_ms"]
                if len(rt):
                    for j, val in enumerate(np.percentile(rt, [50, 95, 99])):
                        ax.bar(i * 4 + j, val, color=COLOURS[r], alpha=0.45 + 0.25 * j)
            ax.set_xticks([i * 4 + 1 for i in range(3)], RUNTIMES)
            ax.set(ylabel="client round trip (ms)", title="Burst of 20 from quiet: p50 / p95 / p99")
            self._save(fig, out / "burst_latency.png")
            made.append("burst_latency.png")
        if len(dm):
            fig, ax = plt.subplots(figsize=(11, 0.45 * len(dm) + 1.2))
            ax.axis("off")
            cells = [[r["control"], r["scope"], _fmt(r["init_delta_ms"], "{:.0f}"), _fmt(r["cold_freq_delta"], "{:+.2f}"),
                      _fmt(r["delta_cost_per_1k_usd"], "{:+.5f}"), _fmt(r["p_holm"], "{:.3g}"), r["band"]]
                     for _, r in dm.iterrows()]
            colours = [["white"] * 6 + [BAND_COLOURS.get(r["band"], "white")] for _, r in dm.iterrows()]
            tbl = ax.table(cellText=cells, cellColours=colours, loc="center",
                           colLabels=["control", "scope", "Init saved (ms)", "cold-freq delta", "delta $ / 1k", "p (Holm)", "band"])
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(8)
            tbl.auto_set_column_width(list(range(7)))
            ax.set_title("Decision matrix")
            self._save(fig, out / "decision_matrix.png")
            made.append("decision_matrix.png")
        return made


def _fmt(v, spec) -> str:
    return "-" if _nan(v) else spec.format(v)


def matrix_markdown(dm: pd.DataFrame, label: str, f_used: float) -> str:
    lines = [f"<!-- generated by scripts/analyse.py - {label} -->", "",
             f"**Data: {label}.**", "",
             "| Control | Scope | Typical Init delta (ms) | Cold-frequency delta | Delta cost / 1k (USD) | p (Holm) | Band | When to use |",
             "|---|---|---|---|---|---|---|---|"]
    for _, r in dm.iterrows():
        lines.append(f"| {r['control']} | {r['scope']} | {_fmt(r['init_delta_ms'], '{:.0f}')} | "
                     f"{_fmt(r['cold_freq_delta'], '{:+.2f}')} | {_fmt(r['delta_cost_per_1k_usd'], '{:+.5f}')} | "
                     f"{_fmt(r['p_holm'], '{:.3g}')} | {r['band']} | {r['when_to_use']} |")
    lines += ["", f"Cost per 1k assumes a cold fraction f = {f_used:.2f} (warm-control arm of the warming phase).",
              "Bands follow docs/ANALYSIS_PLAN.md section 6. Memory and combined rows are exploratory."]
    return "\n".join(lines) + "\n"


def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, list | tuple):
        return [_jsonable(v) for v in o]
    if isinstance(o, np.integer | np.bool_):
        return o.item()
    if isinstance(o, float | np.floating):
        return None if math.isnan(o) else round(float(o), 6)
    return o


def analyse(costs: pd.DataFrame, cfg: dict, fig_dir: str | Path, table_dir: str | Path,
            plan: dict | None = None) -> dict:
    plan = plan or load_plan()
    a = Analysis(costs, plan, cfg)
    fig_dir, table_dir = Path(fig_dir), Path(table_dir)
    table_dir.mkdir(parents=True, exist_ok=True)
    tests = a.run_tests()
    dm = a.decision_matrix()
    figs = a.figures(fig_dir, dm)
    a.phase_a().to_csv(table_dir / "phase_a_baseline_style.csv", index=False)
    a.summary_by_cell().to_csv(table_dir / "summary_by_cell.csv", index=False)
    dm.to_csv(table_dir / "decision_matrix.csv", index=False)
    (table_dir / "decision_matrix.md").write_text(matrix_markdown(dm, a.label, a.cold_fraction_used))
    result = {"data_mode": a.mode, "label": a.label, "alpha": a.alpha, "tests": tests,
              "cold_fraction_used_for_cost": a.cold_fraction_used, "notes": a.notes, "figures": figs}
    (table_dir / "hypotheses.json").write_text(json.dumps(_jsonable(result), indent=2) + "\n")
    return result
