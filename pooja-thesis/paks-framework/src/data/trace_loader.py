"""Fail-closed loaders for GCT / Alibaba (formal CA2) plus explicit synthetic proxy.

Never substitutes the sine-spike simulator when a trace dataset is requested.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.data.workload_simulator import generate_workload

FRAMEWORK_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TRACES = FRAMEWORK_ROOT / "data" / "traces"
DEFAULT_GCT_ROOT = FRAMEWORK_ROOT / "data" / "gct"
DEFAULT_ALIBABA_ROOT = FRAMEWORK_ROOT / "data" / "alibaba"

GCT2011_USAGE_GLOBS = ("2011/task_usage/part-*-of-*.csv.gz", "2011/task_usage/part-*-of-*.csv")
GCT2019_USAGE_GLOBS = ("2019/*/instance_usage/*",)
ALIBABA_USAGE_GLOBS = (
    "**/machine_usage*.csv*",
    "**/machine_usage*.csv.gz",
    "**/batch_task*.csv*",
)

GCT2010_CLUSTER = "gct2010_cluster_cpu.csv"
GCT2010_JOBS = "gct2010_job_cpu_series.csv.gz"

DATA_GAPS_HINT = (
    "See pooja-thesis/DATA_GAPS.md and paks-framework/data/traces/PROVENANCE.md."
)


def _expand(root: Path, patterns: Iterable[str]) -> List[Path]:
    found: List[Path] = []
    for pattern in patterns:
        found.extend(sorted(root.glob(pattern)))
    return found


def gct2011_inventory(root: Optional[Path] = None) -> Dict[str, Any]:
    root = Path(root) if root else DEFAULT_GCT_ROOT
    hits = _expand(root, GCT2011_USAGE_GLOBS)
    return {"root": str(root), "ready": bool(hits), "files": [str(p) for p in hits]}


def gct2019_inventory(root: Optional[Path] = None) -> Dict[str, Any]:
    root = Path(root) if root else DEFAULT_GCT_ROOT
    hits = _expand(root, GCT2019_USAGE_GLOBS)
    return {"root": str(root), "ready": bool(hits), "files": [str(p) for p in hits]}


def alibaba_inventory(root: Optional[Path] = None) -> Dict[str, Any]:
    root = Path(root) if root else DEFAULT_ALIBABA_ROOT
    hits = _expand(root, ALIBABA_USAGE_GLOBS)
    return {"root": str(root), "ready": bool(hits), "files": [str(p) for p in hits]}


def gct2010_paths(traces: Optional[Path] = None) -> Tuple[Path, Path]:
    traces = Path(traces) if traces else DEFAULT_TRACES
    return traces / GCT2010_CLUSTER, traces / GCT2010_JOBS


def gct2010_ready(traces: Optional[Path] = None) -> bool:
    cluster, jobs = gct2010_paths(traces)
    return cluster.is_file() and jobs.is_file()


def missing_checklist(dataset: str) -> str:
    g11 = gct2011_inventory()
    g19 = gct2019_inventory()
    ali = alibaba_inventory()
    c2010, j2010 = gct2010_paths()
    lines = [
        f"Trace dataset '{dataset}' is not available (fail-closed; no synthetic fallback).",
        DATA_GAPS_HINT,
        "",
        f"GCT 2011 task_usage ready={g11['ready']} root={g11['root']}",
        f"GCT 2019 instance_usage ready={g19['ready']} root={g19['root']}",
        f"Alibaba machine_usage ready={ali['ready']} root={ali['root']}",
        f"GCT 2010 public slice cluster={c2010.is_file()} jobs={j2010.is_file()}",
        "",
        "Populate the paths in DATA_GAPS.md, or use --dataset gct2010 for the committed 2010 slice,",
        "or --dataset synthetic for the PROXY NimbusGuard simulator (not formal CA2 evidence).",
    ]
    return "\n".join(lines)


def load_gct2010_cluster(traces: Optional[Path] = None) -> pd.DataFrame:
    cluster, _ = gct2010_paths(traces)
    if not cluster.is_file():
        raise FileNotFoundError(missing_checklist("gct2010"))
    df = pd.read_csv(cluster)
    required = {"time_s", "cpu_cores_sum"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"gct2010 cluster series missing columns {sorted(missing)}")
    df = df.sort_values("time_s").reset_index(drop=True)
    return df


def load_gct2010_jobs(traces: Optional[Path] = None) -> pd.DataFrame:
    _, jobs = gct2010_paths(traces)
    if not jobs.is_file():
        raise FileNotFoundError(missing_checklist("gct2010"))
    df = pd.read_csv(jobs, compression="gzip")
    required = {"job_id", "time_s", "cpu_cores_sum"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"gct2010 job series missing columns {sorted(missing)}")
    return df


def cluster_workload_from_frame(df: pd.DataFrame, drop_zero_tail: bool = True) -> np.ndarray:
    """1-D cluster CPU demand. Optional drop of trailing all-zero bins (end-of-trace)."""
    cpu = df["cpu_cores_sum"].to_numpy(dtype=float)
    if drop_zero_tail:
        nz = np.where(cpu > 0)[0]
        if len(nz):
            cpu = cpu[: nz[-1] + 1]
    if cpu.size < 2:
        raise ValueError("cluster CPU series too short after filtering")
    return cpu


def require_dataset(dataset: str) -> None:
    key = dataset.strip().lower()
    if key in {"gct2011", "google2011"}:
        if not gct2011_inventory()["ready"]:
            raise FileNotFoundError(missing_checklist(key))
    elif key in {"gct2019", "borg2019"}:
        if not gct2019_inventory()["ready"]:
            raise FileNotFoundError(missing_checklist(key))
    elif key in {"alibaba", "ali"}:
        if not alibaba_inventory()["ready"]:
            raise FileNotFoundError(missing_checklist(key))
    elif key in {"gct2010", "gct-v1", "gct"}:
        if key in {"gct2010", "gct-v1"} and not gct2010_ready():
            raise FileNotFoundError(missing_checklist(key))
        if key == "gct":
            if gct2011_inventory()["ready"] or gct2019_inventory()["ready"] or gct2010_ready():
                return
            raise FileNotFoundError(missing_checklist(key))
    elif key in {"synthetic", "proxy"}:
        return
    else:
        raise ValueError(f"Unknown dataset '{dataset}'. {DATA_GAPS_HINT}")


def resolve_formal_source(dataset: str = "gct") -> Dict[str, Any]:
    """Choose the best available trace. Never returns synthetic for gct/alibaba keys."""
    key = dataset.strip().lower()
    require_dataset(key)
    if key in {"synthetic", "proxy"}:
        return {
            "dataset": "synthetic",
            "family": "proxy",
            "proxy": True,
            "evidence": "SIMULATED",
            "note": "NimbusGuard-framed sine/spike generator; not GCT/Alibaba.",
        }
    if key in {"gct2011", "google2011"}:
        return {
            "dataset": "gct2011",
            "family": "gct",
            "proxy": False,
            "evidence": "TRACE",
            "files": gct2011_inventory()["files"],
            "note": "GCT 2011 present; window join beyond presence-gate is still required.",
        }
    if key in {"gct2019", "borg2019"}:
        return {
            "dataset": "gct2019",
            "family": "gct",
            "proxy": False,
            "evidence": "TRACE",
            "files": gct2019_inventory()["files"],
            "note": "GCT 2019 present; window join beyond presence-gate is still required.",
        }
    if key in {"alibaba", "ali"}:
        return {
            "dataset": "alibaba",
            "family": "alibaba",
            "proxy": False,
            "evidence": "TRACE",
            "files": alibaba_inventory()["files"],
            "note": "Alibaba files present; usage parser still required.",
        }
    # gct / gct2010: prefer 2011, then 2019, then committed 2010 slice
    if key == "gct" and gct2011_inventory()["ready"]:
        return resolve_formal_source("gct2011")
    if key == "gct" and gct2019_inventory()["ready"]:
        return resolve_formal_source("gct2019")
    if not gct2010_ready():
        raise FileNotFoundError(missing_checklist(key))
    return {
        "dataset": "gct2010",
        "family": "gct",
        "proxy": False,
        "evidence": "TRACE",
        "generation": "Google Cluster Data v1 (2010, ~7h)",
        "residual": "GCT 2011/2019 and Alibaba still absent (DATA_GAPS.md)",
        "note": "Public CC-BY 7-hour GCT sample; not the 29-day 2011 or 2019 traces.",
        "cluster_csv": str(gct2010_paths()[0]),
        "jobs_csv": str(gct2010_paths()[1]),
    }


def load_scaling_workload(
    dataset: str = "gct",
    seed: int = 42,
    synthetic_steps: int = 500,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    meta = resolve_formal_source(dataset)
    if meta["proxy"]:
        return generate_workload(synthetic_steps, seed=seed), meta
    if meta["dataset"] != "gct2010":
        raise FileNotFoundError(
            f"{meta['dataset']} files are listed present but a usage→series parser "
            f"is not implemented yet. {DATA_GAPS_HINT}"
        )
    df = load_gct2010_cluster()
    series = cluster_workload_from_frame(df)
    meta = dict(meta)
    meta["n_steps"] = int(series.size)
    meta["bin_seconds"] = 300
    meta["dropped_zero_tail"] = bool(df["cpu_cores_sum"].iloc[-1] == 0)
    return series, meta


def env_dataset_override() -> Optional[str]:
    return os.environ.get("PAKS_DATASET")
