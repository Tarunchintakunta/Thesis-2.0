"""Fail-closed loaders for GCT / Alibaba plus explicit synthetic proxy.

Never substitutes the sine-spike simulator when a trace dataset is requested."""

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

GCT2011_USAGE_GLOBS = (
    "2011/task_usage/part-*-of-*.csv.gz",
    "2011/task_usage/part-*-of-*.csv",
)
GCT2019_USAGE_GLOBS = ("2019/*/instance_usage/*",)
ALIBABA_USAGE_GLOBS = (
    "**/machine_usage*.csv*",
    "**/machine_usage*.csv.gz",
    "**/machine_usage*.tar.gz*",
    "**/batch_task*.csv*",
)

GCT2010_CLUSTER = "gct2010_cluster_cpu.csv"
GCT2010_JOBS = "gct2010_job_cpu_series.csv.gz"
GCT2011_CLUSTER = "gct2011_part00000_cluster_cpu.csv"
GCT2011_JOBS = "gct2011_part00000_job_cpu_series.csv.gz"
ALIBABA_CLUSTER = "alibaba_v2018_machine_usage_sample_cluster_cpu.csv"

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
    derived = (DEFAULT_TRACES / GCT2011_CLUSTER).is_file() and (DEFAULT_TRACES / GCT2011_JOBS).is_file()
    return {
        "root": str(root),
        "ready": bool(hits) or derived,
        "files": [str(p) for p in hits],
        "derived_ready": derived,
    }


def gct2019_inventory(root: Optional[Path] = None) -> Dict[str, Any]:
    root = Path(root) if root else DEFAULT_GCT_ROOT
    hits = _expand(root, GCT2019_USAGE_GLOBS)
    return {"root": str(root), "ready": bool(hits), "files": [str(p) for p in hits]}


def alibaba_inventory(root: Optional[Path] = None) -> Dict[str, Any]:
    root = Path(root) if root else DEFAULT_ALIBABA_ROOT
    hits = _expand(root, ALIBABA_USAGE_GLOBS)
    derived = (DEFAULT_TRACES / ALIBABA_CLUSTER).is_file()
    return {
        "root": str(root),
        "ready": bool(hits) or derived,
        "files": [str(p) for p in hits],
        "derived_ready": derived,
    }


def gct2010_paths(traces: Optional[Path] = None) -> Tuple[Path, Path]:
    traces = Path(traces) if traces else DEFAULT_TRACES
    return traces / GCT2010_CLUSTER, traces / GCT2010_JOBS


def gct2011_paths(traces: Optional[Path] = None) -> Tuple[Path, Path]:
    traces = Path(traces) if traces else DEFAULT_TRACES
    return traces / GCT2011_CLUSTER, traces / GCT2011_JOBS


def alibaba_cluster_path(traces: Optional[Path] = None) -> Path:
    traces = Path(traces) if traces else DEFAULT_TRACES
    return traces / ALIBABA_CLUSTER


def gct2010_ready(traces: Optional[Path] = None) -> bool:
    cluster, jobs = gct2010_paths(traces)
    return cluster.is_file() and jobs.is_file()


def gct2011_derived_ready(traces: Optional[Path] = None) -> bool:
    cluster, jobs = gct2011_paths(traces)
    return cluster.is_file() and jobs.is_file()


def alibaba_derived_ready(traces: Optional[Path] = None) -> bool:
    return alibaba_cluster_path(traces).is_file()


def missing_checklist(dataset: str) -> str:
    g11 = gct2011_inventory()
    g19 = gct2019_inventory()
    ali = alibaba_inventory()
    c2010, j2010 = gct2010_paths()
    c2011, j2011 = gct2011_paths()
    lines = [
        f"Trace dataset '{dataset}' is not available (fail-closed; no synthetic fallback).",
        DATA_GAPS_HINT,
        "",
        f"GCT 2011 task_usage ready={g11['ready']} root={g11['root']} derived={g11.get('derived_ready')}",
        f"GCT 2019 instance_usage ready={g19['ready']} root={g19['root']}",
        f"Alibaba machine_usage ready={ali['ready']} root={ali['root']} derived={ali.get('derived_ready')}",
        f"GCT 2010 public slice cluster={c2010.is_file()} jobs={j2010.is_file()}",
        f"GCT 2011 derived cluster={c2011.is_file()} jobs={j2011.is_file()}",
        f"Alibaba derived cluster={alibaba_cluster_path().is_file()}",
        "",
        "Populate the paths in DATA_GAPS.md, run scripts/fetch_extended_trace_samples.py,",
        "or use --dataset gct2010 for the committed 2010 slice,",
    ]
    return "\n".join(lines)


def _require_cpu_column(df: pd.DataFrame, label: str) -> pd.DataFrame:
    if "cpu_cores_sum" not in df.columns and "cpu_rate_sum" in df.columns:
        df = df.rename(columns={"cpu_rate_sum": "cpu_cores_sum"})
    if "cpu_cores_sum" not in df.columns and "cpu_util_mean" in df.columns:
        df = df.rename(columns={"cpu_util_mean": "cpu_cores_sum"})
    required = {"time_s", "cpu_cores_sum"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{label} missing columns {sorted(missing)}")
    return df.sort_values("time_s").reset_index(drop=True)


def load_gct2010_cluster(traces: Optional[Path] = None) -> pd.DataFrame:
    cluster, _ = gct2010_paths(traces)
    if not cluster.is_file():
        raise FileNotFoundError(missing_checklist("gct2010"))
    return _require_cpu_column(pd.read_csv(cluster), "gct2010 cluster")


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


def load_gct2011_cluster(traces: Optional[Path] = None) -> pd.DataFrame:
    cluster, _ = gct2011_paths(traces)
    if not cluster.is_file():
        raise FileNotFoundError(missing_checklist("gct2011"))
    return _require_cpu_column(pd.read_csv(cluster), "gct2011 cluster")


def load_gct2011_jobs(traces: Optional[Path] = None) -> pd.DataFrame:
    _, jobs = gct2011_paths(traces)
    if not jobs.is_file():
        raise FileNotFoundError(missing_checklist("gct2011"))
    df = pd.read_csv(jobs, compression="gzip")
    required = {"job_id", "time_s", "cpu_cores_sum"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"gct2011 job series missing columns {sorted(missing)}")
    return df


def load_alibaba_cluster(traces: Optional[Path] = None) -> pd.DataFrame:
    path = alibaba_cluster_path(traces)
    if not path.is_file():
        raise FileNotFoundError(missing_checklist("alibaba"))
    return _require_cpu_column(pd.read_csv(path), "alibaba cluster")


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
            if (
                gct2011_inventory()["ready"]
                or gct2019_inventory()["ready"]
                or gct2010_ready()
            ):
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
        if not gct2011_derived_ready():
            raise FileNotFoundError(
                f"GCT 2011 raw part present but derived series missing. "
                f"Run scripts/fetch_extended_trace_samples.py --aggregate-only. {DATA_GAPS_HINT}"
            )
        return {
            "dataset": "gct2011",
            "family": "gct",
            "proxy": False,
            "evidence": "TRACE",
            "generation": "GCT 2011 task_usage part-00000-of-00500 (single shard sample)",
            "residual": "Full 500-part 29-day dump and GCT 2019 still absent; Alibaba is a separate --dataset.",
            "note": "One public GCS shard (~87 MiB), SHA256-verified; not the full 29-day cell.",
            "cluster_csv": str(gct2011_paths()[0]),
            "jobs_csv": str(gct2011_paths()[1]),
            "files": gct2011_inventory()["files"],
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
        if not alibaba_derived_ready():
            raise FileNotFoundError(
                f"Alibaba artefacts present but derived cluster series missing. "
                f"Run scripts/fetch_extended_trace_samples.py --aggregate-only. {DATA_GAPS_HINT}"
            )
        return {
            "dataset": "alibaba",
            "family": "alibaba",
            "proxy": False,
            "evidence": "TRACE",
            "generation": "Alibaba cluster-trace-v2018 machine_usage RANGE sample (first 64 MiB of tar.gz)",
            "residual": "Full 1.7 GiB machine_usage.tar.gz not downloaded; GCT 2019 still absent.",
            "note": "Public OSS range sample, SHA256-verified; resampled to 300s mean CPU.",
            "cluster_csv": str(alibaba_cluster_path()),
            "files": alibaba_inventory()["files"],
            "sample_kind": "HTTP_RANGE_64MiB",
        }
    # gct / gct2010: prefer 2011, then 2019, then committed 2010 slice
    if key == "gct" and gct2011_inventory()["ready"] and gct2011_derived_ready():
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
    max_steps: Optional[int] = None,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    meta = resolve_formal_source(dataset)
    if meta["proxy"]:
        return generate_workload(synthetic_steps, seed=seed), meta
    if meta["dataset"] == "gct2010":
        df = load_gct2010_cluster()
    elif meta["dataset"] == "gct2011":
        df = load_gct2011_cluster()
    elif meta["dataset"] == "alibaba":
        df = load_alibaba_cluster()
    else:
        raise FileNotFoundError(
            f"{meta['dataset']} files are listed present but a usage→series parser "
            f"is not implemented yet. {DATA_GAPS_HINT}"
        )
    series = cluster_workload_from_frame(df)
    if max_steps is not None and series.size > max_steps:
        series = series[: int(max_steps)]
    meta = dict(meta)
    meta["n_steps"] = int(series.size)
    meta["bin_seconds"] = 300
    meta["dropped_zero_tail"] = bool(df["cpu_cores_sum"].iloc[-1] == 0)
    if "mem_sum" in df.columns:
        mem = df["mem_sum"].to_numpy(dtype=float)[: series.size]
        meta["mem_series"] = mem
    return series, meta


def env_dataset_override() -> Optional[str]:
    return os.environ.get("PAKS_DATASET")
