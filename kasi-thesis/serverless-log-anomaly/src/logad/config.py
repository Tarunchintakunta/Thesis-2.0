"""Config loading. All experiment settings live in configs/*.yaml."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "configs"


def load_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a mapping at the top level")
    return data


def deep_merge(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(base)
    for key, value in (extra or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def load_experiment(path: str | Path | None = None) -> dict[str, Any]:
    """experiment.yaml, optionally overlaid by a smaller file (e.g. smoke.yaml)
    that names its parent with ``extends:``."""
    path = Path(path or CONFIG_DIR / "experiment.yaml")
    cfg = load_yaml(path)
    parent = cfg.pop("extends", None)
    if parent:
        cfg = deep_merge(load_experiment(path.parent / parent), cfg)
    return cfg


def file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dict_hash(data: dict[str, Any]) -> str:
    raw = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
