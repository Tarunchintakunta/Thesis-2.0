"""Load experiment.yaml and expand the chosen scale (dry_run | formal)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from common.models import ExperimentSpec, factorial
from simulator.mock_broker import MockParams

ROOT = Path(__file__).resolve().parents[2]


def load_experiment(path: Path | None = None) -> dict[str, Any]:
    path = path or (ROOT / "configs" / "experiment.yaml")
    return yaml.safe_load(path.read_text())


def mock_params(cfg: dict[str, Any]) -> MockParams:
    raw = dict(cfg.get("mock") or {})
    raw.pop("session_queue_note", None)
    return MockParams(**raw)


def specs_from_cfg(cfg: dict[str, Any], scale: str) -> list[ExperimentSpec]:
    if scale not in ("dry_run", "formal"):
        raise ValueError(scale)
    block = cfg[scale]
    backend = "mock" if scale == "dry_run" else str(cfg.get("backend", "mock"))
    if scale == "formal":
        backend = "mock"  # generating formal-sized *mock* is allowed; live is a separate script
    return factorial(
        qos=block["qos"],
        disconnect_s=block["disconnect_s"],
        rate=block["rate"],
        replications=int(block["replications"]),
        n_devices=int(block["devices"]),
        n_messages=int(block["messages"]),
        interval_s=float(block["interval_s"]),
        payload_bytes=int(block.get("payload_bytes", 64)),
        seed=int(block.get("seed", 42)),
        backend=backend,
    )
