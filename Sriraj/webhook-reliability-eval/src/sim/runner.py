"""Local simulator: synthetic webhooks × configs × fault rates → JSON results."""
from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any

from fault.injector import FaultPlan, should_inject_duplicate
from pipeline.processor import ConfigMode, Pipeline, PipelineConfig


def make_event(i: int, *, poison: bool = False) -> dict[str, Any]:
    return {
        "event_id": f"evt-{i:06d}",
        "source": "payments.demo",
        "type": "invoice.paid",
        "amount_cents": 1000 + (i % 500),
        "currency": "EUR",
        "poison": poison,
        "synthetic": True,
    }


def run_cell(
    mode: ConfigMode,
    fault_rate: float,
    *,
    n_events: int = 200,
    duplicate_rate: float = 0.10,
    permanent_fraction: float = 0.15,
    seed: int = 42,
    max_receive_count: int = 3,
) -> dict[str, Any]:
    """Run one experimental cell and return metrics dict (LOCAL_SIM)."""
    rng = random.Random(seed)
    pipe = Pipeline(
        PipelineConfig(mode=mode, max_receive_count=max_receive_count),
        rng=rng,
    )
    pipe.metrics.fault_rate = fault_rate
    pipe.metrics.mode = "local_sim"

    # permanent vs transient split of the fault mass
    transient_rate = fault_rate * (1.0 - permanent_fraction)
    permanent_rate = fault_rate * permanent_fraction
    plan = FaultPlan(
        transient_rate=transient_rate,
        permanent_rate=permanent_rate,
        duplicate_rate=duplicate_rate,
    )

    events = [make_event(i, poison=(i % 97 == 0)) for i in range(n_events)]
    pipe.metrics.unique_events = n_events

    # Ingest (+ optional duplicate ingestions)
    for ev in events:
        pipe.ingest(ev)
        if should_inject_duplicate(plan, rng):
            pipe.metrics.duplicate_attempts += 1
            pipe.ingest(ev)  # same event_id again

    # Drain with bounded steps
    safety = (n_events + pipe.metrics.duplicate_attempts) * (max_receive_count + 2) + 50
    for _ in range(safety):
        if pipe.main_q.depth() == 0:
            break
        pipe.drain_once(plan)

    # DLQ replay phase (RD/RDI)
    if mode in (ConfigMode.RD, ConfigMode.RDI) and pipe.dlq.depth() > 0:
        pipe.replay_dlq(clear_permanent=True)

    pipe.metrics.delivered_unique = len(pipe.sink)
    return pipe.metrics.to_dict()


def run_pilot(
    *,
    n_events: int = 200,
    fault_rates: list[float] | None = None,
    modes: list[str] | None = None,
    seed: int = 42,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    fault_rates = fault_rates or [0.0, 0.10, 0.25, 0.50]
    modes = modes or ["B", "R", "RD", "RDI"]
    cells = []
    for m in modes:
        for fr in fault_rates:
            cell_seed = seed + hash((m, fr)) % 10_000
            result = run_cell(ConfigMode(m), fr, n_events=n_events, seed=cell_seed)
            cells.append(result)

    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "mode": "local_sim",
        "note": "LOCAL_SIM / in-memory queues+store — NOT live AWS. Numbers are reproducible simulator output.",
        "n_events_per_cell": n_events,
        "fault_rates": fault_rates,
        "configs": modes,
        "duplicate_rate": 0.10,
        "cells": cells,
        "dataset": {
            "type": "synthetic_webhook_payloads",
            "pii": False,
            "generator": "sim.runner.make_event",
            "fields": ["event_id", "source", "type", "amount_cents", "currency", "poison", "synthetic"],
            "fault_injection_rates": fault_rates,
        },
    }

    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "pilot_results.json"
        path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        # also write a compact CSV-like JSON lines
        (out_dir / "pilot_cells.jsonl").write_text(
            "\n".join(json.dumps(c) for c in cells) + "\n",
            encoding="utf-8",
        )
        summary["written"] = str(path)
    return summary


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    out = run_pilot(out_dir=root / "results" / "local_sim")
    print(json.dumps({"cells": len(out["cells"]), "written": out.get("written")}, indent=2))
