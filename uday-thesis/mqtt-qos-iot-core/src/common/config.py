"""Load experiment.yaml and expand the chosen scale (dry_run | lite | smoke | formal)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from common.models import DISCONNECT_S, QOS_LEVELS, RATE_MODES, ExperimentSpec, factorial
from simulator.mock_broker import MockParams

ROOT = Path(__file__).resolve().parents[2]


def load_experiment(path: Path | None = None) -> dict[str, Any]:
    p = path or (ROOT / "configs" / "experiment.yaml")
    return yaml.safe_load(p.read_text())


def mock_params(cfg: dict[str, Any]) -> MockParams:
    raw = dict(cfg.get("mock_params") or {})
    raw.pop("description", None)
    return MockParams(**raw)


def _factor_list(cfg: dict[str, Any], block: dict[str, Any], key: str, default: tuple) -> list:
    if key in block and block[key] is not None:
        return list(block[key])
    factors = cfg.get("factors") or {}
    if key in factors:
        return list(factors[key])
    # experiment.yaml uses rate_modes; factorial() uses rate=
    if key == "rate_modes" and "rate_modes" in factors:
        return list(factors["rate_modes"])
    return list(default)


def n_cells_for_scale(cfg: dict[str, Any], scale: str) -> int:
    block = cfg.get(scale)
    if not block:
        raise ValueError(f"unknown scale: {scale}")
    qos = _factor_list(cfg, block, "qos", QOS_LEVELS)
    disconnect = _factor_list(cfg, block, "disconnect_s", DISCONNECT_S)
    rates = _factor_list(cfg, block, "rate_modes", RATE_MODES)
    reps = int(block.get("replications", 1))
    return len(qos) * len(disconnect) * len(rates) * reps


def specs_from_cfg(cfg: dict[str, Any], scale: str = "dry_run") -> list[ExperimentSpec]:
    block = cfg.get(scale)
    if not block:
        raise ValueError(f"unknown scale: {scale}")
    backend = str(block.get("backend", "mock"))
    return factorial(
        qos=_factor_list(cfg, block, "qos", QOS_LEVELS),
        disconnect_s=_factor_list(cfg, block, "disconnect_s", DISCONNECT_S),
        rate=_factor_list(cfg, block, "rate_modes", RATE_MODES),
        replications=int(block.get("replications", 1)),
        n_devices=int(block.get("n_devices", 5)),
        n_messages=int(block.get("n_messages", 40)),
        interval_s=float(block.get("interval_s", 5.0)),
        payload_bytes=int(block.get("payload_bytes", 64)),
        seed=int(block.get("seed", 42)),
        backend=backend,
    )
