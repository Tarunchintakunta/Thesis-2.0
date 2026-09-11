"""Run manifests - the single source of truth for the analysis.

Every run writes ``<out>/manifests/<RUN_ID>.json`` with the git commit, config
hash, region, runtime, start/end time, fault schedule, seed, the full run spec
and the computed metrics. ``analysis/`` only ever reads these files, never
hand-edited CSVs.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def git_commit() -> dict[str, Any]:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain", "--", "src", "configs"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        )
        return {"sha": sha, "dirty": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"sha": "unknown", "dirty": None}


def runtime_info() -> dict[str, str]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "lambda_runtime": "python3.12",
    }


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _clean(value: Any) -> Any:
    """NaN/inf are not valid JSON, store them as null."""
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean(v) for v in value]
    return value


def build_manifest(
    spec,
    metrics: dict[str, Any],
    cost: dict[str, Any],
    counters: dict[str, float],
    backend: str,
    started_at: str,
    finished_at: str,
    order_position: int,
    config_file: str,
    git: dict[str, Any] | None = None,
) -> dict[str, Any]:
    window = spec.fault_window
    manifest = {
        "run_id": spec.run_id,
        "campaign": spec.campaign,
        "repeat": spec.repeat,
        "order_position": order_position,
        "backend": backend,
        "measurement_kind": "local simulation (not an AWS measurement)" if backend == "localsim" else "live AWS",
        "git": git or git_commit(),
        "config_file": config_file,
        "config_hash": spec.config_hash(),
        "region": "local" if backend == "localsim" else spec.region,
        "runtime": runtime_info(),
        "started_at": started_at,
        "finished_at": finished_at,
        "seed": spec.seed,
        "cell": spec.cell(),
        "fault_schedule": {
            "mode": spec.fault_mode,
            "rate": spec.fault_rate,
            "point": spec.fault_point,
            "on_s": window[0] if window else None,
            "off_s": window[1] if window else None,
        },
        "spec": spec.to_dict(),
        "metrics": metrics,
        "cost": cost,
        "counters": counters,
    }
    return _clean(manifest)


def write_manifest(out_dir: str | Path, manifest: dict[str, Any]) -> Path:
    folder = Path(out_dir) / "manifests"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{manifest['run_id']}.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def read_manifests(root: str | Path) -> list[dict[str, Any]]:
    root = Path(root)
    paths = sorted(root.glob("**/manifests/*.json"))
    if root.name == "manifests":
        paths = sorted(root.glob("*.json"))
    out = []
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        data["_path"] = str(path)
        out.append(data)
    return out
