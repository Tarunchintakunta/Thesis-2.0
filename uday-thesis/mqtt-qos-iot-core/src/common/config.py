"""Load experiment.yaml and expand the chosen scale (dry_run | formal)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from common.models import ExperimentSpec, factorial
from simulator.mock_broker import MockParams

ROOT = Path(__file__).resolve().parents[2]


def load_experiment(path: Path | None = None) -> dict[str, Any]:
    p = path or (ROOT / "configs" / "experiment.yaml")
    return yaml.safe_load(p.read_text())


def mock_params(cfg: dict[str, Any]) -> MockParams:
    raw = dict(cfg.get("mock_params") or {})
    raw.pop("description", None)
    return MockParams(**raw)


def specs_from_cfg(cfg: dict[str, Any], scale: str = "dry_run") -> list[ExperimentSpec]:
    block = cfg.get(scale)
    if not block:
        raise ValueError(f"unknown scale: {scale}")
    backend = str(block.get("backend", "mock"))
    return factorial(
        replications=int(block.get("replications", 1)),
        n_devices=int(block.get("n_devices", 5)),
        n_messages=int(block.get("n_messages", 40)),
        interval_s=float(block.get("interval_s", 5.0)),
        payload_bytes=int(block.get("payload_bytes", 64)),
        seed=int(block.get("seed", 42)),
        backend=backend,
    )
