"""Per-request and per-cell metrics for one run folder.

Inputs written by the driver: ground_truth.jsonl, deliveries.jsonl, run_info.json
and - for the mutation ground truth - stream.jsonl (python -m driver.streams).
Without a stream file the function's own business_writes are used instead, and
the tables say so in `mutation_source`.

duplicate mutation = every state change of the business item after the first
one. A request with multiplicity N has N-1 injected retries, so

    duplicate-mutation rate = sum(dup_mutations) / sum(injected_retries)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from analysis import stats

NUMERIC = ["consumed_capacity", "wcu_ccf_rule", "ccf", "business_writes", "rtt_ms", "ddb_ms"]


def read_jsonl(path: str | Path) -> pd.DataFrame:
    with open(path, encoding="utf-8") as fh:
        return pd.DataFrame([json.loads(line) for line in fh if line.strip()])


def load_run(folder: str | Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame | None, dict]:
    folder = Path(folder)
    gt = read_jsonl(folder / "ground_truth.jsonl")
    dl = read_jsonl(folder / "deliveries.jsonl")
    st = read_jsonl(folder / "stream.jsonl") if (folder / "stream.jsonl").exists() else None
    info = json.loads((folder / "run_info.json").read_text()) if (folder / "run_info.json").exists() else {}
    return gt, dl, st, info


def per_request(gt: pd.DataFrame, dl: pd.DataFrame, st: pd.DataFrame | None = None) -> pd.DataFrame:
    dl = dl.copy()
    for c in NUMERIC:
        dl[c] = pd.to_numeric(dl[c], errors="coerce")
    g = dl.groupby("request_id")
    agg = pd.DataFrame({
        "observed_deliveries": g.size(),
        "capacity_reported": g["consumed_capacity"].sum(min_count=1),
        "capacity_rule": g["wcu_ccf_rule"].sum(),
        "ccf": g["ccf"].sum(),
        "timeouts": g["status"].agg(lambda s: int((s == "timeout").sum())),
        "errors": g["status"].agg(lambda s: int((s == "error").sum())),
        "lost_records": g["consumed_capacity"].agg(lambda s: int(s.isna().sum())),
        "self_mutations": g["business_writes"].sum(),
    })
    final = dl[dl["delivery"] == dl["multiplicity"]].drop_duplicates("request_id").set_index("request_id")
    agg = agg.join(final[["status", "outcome", "rtt_ms", "ddb_ms", "cold_start"]].rename(columns={
        "status": "final_status", "outcome": "final_outcome", "rtt_ms": "latency_ms", "ddb_ms": "ddb_ms",
        "cold_start": "cold_final"}))
    keep = ["phase", "path", "multiplicity", "inject_mode", "injected_retries"]
    out = gt.set_index("request_id")[keep].join(agg)
    out["observed_deliveries"] = out["observed_deliveries"].fillna(0).astype(int)
    if st is not None and len(st):
        b = st[(st["kind"] == "business") & st["event"].isin(["INSERT", "MODIFY"])]
        out["mutations"] = b.groupby("request_id").size().reindex(out.index).fillna(0).astype(int)
        out["mutation_source"] = "stream"
    else:
        out["mutations"] = out["self_mutations"].fillna(0).astype(int)
        out["mutation_source"] = "self_report"
    out["dup_mutations"] = (out["mutations"] - 1).clip(lower=0)
    out["successful_retries"] = (out["injected_retries"] - out["dup_mutations"]).clip(lower=0)
    out["capacity_total"] = out["capacity_reported"] + out["capacity_rule"]
    out["missing_deliveries"] = out["multiplicity"] - out["observed_deliveries"]
    out["no_mutation"] = out["mutations"] == 0
    out["stream_self_mismatch"] = out["mutations"] != out["self_mutations"].fillna(-1)
    return out.reset_index()


def cell_summary(req: pd.DataFrame, alpha: float = 0.05, B: int = 2000, seed: int = 0) -> pd.DataFrame:
    rows = []
    for (phase, path, m), g in req.groupby(["phase", "path", "multiplicity"], sort=True):
        retries, dups = int(g["injected_retries"].sum()), int(g["dup_mutations"].sum())
        p, lo, hi = stats.wilson(dups, retries, alpha)
        clo, chi = stats.cluster_rate_ci(g["dup_mutations"], g["injected_retries"], B, alpha, seed)
        cap = g["capacity_total"].dropna()
        lat = g["latency_ms"].dropna()
        warm = g.loc[g["cold_final"] == False, "latency_ms"].dropna()  # noqa: E712 - column may hold None
        rows.append({
            "phase": phase, "path": path, "multiplicity": int(m), "requests": len(g), "injected_retries": retries,
            "dup_mutations": dups, "dup_rate": p, "dup_ci_lo": lo, "dup_ci_hi": hi,
            "dup_cluster_ci_lo": clo, "dup_cluster_ci_hi": chi,
            "ccf_per_retry": g["ccf"].sum() / retries if retries else np.nan,
            "successful_retry_rate": g["successful_retries"].sum() / retries if retries else np.nan,
            "capacity_mean": cap.mean(), **_ci("capacity_mean", cap, "mean", B, alpha, seed),
            "capacity_reported_mean": g["capacity_reported"].mean(), "capacity_rule_mean": g["capacity_rule"].mean(),
            "latency_mean_ms": lat.mean(), **_ci("latency_mean_ms", lat, "mean", B, alpha, seed),
            "latency_p95_ms": lat.quantile(0.95) if len(lat) else np.nan,
            **_ci("latency_p95_ms", lat, "p95", B, alpha, seed),
            "latency_warm_mean_ms": warm.mean() if len(warm) else np.nan,
            "cold_final_share": float((g["cold_final"] == True).mean()),  # noqa: E712
            "ddb_mean_ms": g["ddb_ms"].mean(),
            "missing_deliveries": int(g["missing_deliveries"].sum()), "errors": int(g["errors"].sum()),
            "lost_records": int(g["lost_records"].sum()), "stream_self_mismatch": int(g["stream_self_mismatch"].sum()),
            "no_mutation": int(g["no_mutation"].sum()), "mutation_source": g["mutation_source"].iloc[0],
        })
    return pd.DataFrame(rows)


def _ci(name: str, x: pd.Series, stat: str, B: int, alpha: float, seed: int) -> dict:
    lo, hi = stats.bootstrap_ci(x.to_numpy(float), stat, B, alpha, seed) if len(x) else (np.nan, np.nan)
    return {f"{name}_ci_lo": lo, f"{name}_ci_hi": hi}
