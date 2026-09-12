"""Load configs/experiment.yaml (pilot.yaml `extends` it and brings its own phases)."""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
RUNTIMES = ("python", "nodejs", "java")
VARIANTS = ("default", "optimised", "bytecode")
PHASE_KINDS = {"warm", "cold", "warming", "burst", "idle_probe"}


def resolve(path: str | Path) -> Path:
    p = Path(path)
    if p.is_absolute() or p.exists():
        return p
    return ROOT / p


def _merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def load_config(path: str | Path) -> dict:
    with open(resolve(path), encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}
    if "extends" in cfg:
        base = load_config(cfg.pop("extends"))
        phases = cfg.pop("phases", None)
        cfg = _merge(base, cfg)
        if phases is not None:  # a pilot replaces the phase list, it does not add to it
            cfg["phases"] = phases
    validate(cfg)
    return cfg


def validate(cfg: dict) -> None:
    if cfg.get("force_cold") not in ("update_env", "idle"):
        raise ValueError("force_cold must be update_env or idle")
    if cfg.get("arch") not in ("arm64", "x86_64"):
        raise ValueError("arch must be arm64 or x86_64")
    for name, ph in cfg.get("phases", {}).items():
        kind = ph.get("kind")
        if kind not in PHASE_KINDS:
            raise ValueError(f"phase {name}: unknown kind {kind}")
        if kind == "warming":
            continue
        for r in ph.get("runtimes", []):
            if r not in RUNTIMES:
                raise ValueError(f"phase {name}: unknown runtime {r}")
        for v in ph.get("variants", []):
            if v not in VARIANTS:
                raise ValueError(f"phase {name}: unknown variant {v}")
        for _, _, m in phase_cells(ph):
            if not 128 <= int(m) <= 10240:
                raise ValueError(f"phase {name}: memory {m} outside 128-10240 MB")
        if int(ph.get("reps", 0)) < 1:
            raise ValueError(f"phase {name}: reps must be >= 1")


def phase_cells(ph: dict) -> list[tuple[str, str, int]]:
    """(runtime, variant, memory) cells of a phase, in a fixed order."""
    valid = {"python-default", "python-optimised", "python-bytecode",
             "nodejs-default", "nodejs-optimised", "java-default", "java-optimised"}
    if "cells" in ph:
        cells = [(r, c["variant"], int(c["memory"])) for r in ph["runtimes"] for c in ph["cells"]]
    else:
        cells = [(r, v, int(m)) for r in ph["runtimes"] for v in ph["variants"] for m in ph["memories"]]
    return [(r, v, m) for r, v, m in cells if f"{r}-{v}" in valid]
