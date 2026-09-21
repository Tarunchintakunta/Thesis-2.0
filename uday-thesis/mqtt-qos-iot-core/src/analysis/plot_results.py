"""Figures for mock (or later live) cell summaries. Always labelled as such."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as pyplot
import numpy as np

plt = pyplot


def plot_cells(cells: list[dict[str, Any]], out_dir: Path, backend: str = "mock") -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    disconnects = sorted({int(c["disconnect_s"]) for c in cells})
    rates = sorted({str(c["rate_mode"]) for c in cells})
    written: list[Path] = []

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, rate in zip(axes, rates):
        for qos, marker in ((0, "o"), (1, "s")):
            ys = []
            for d in disconnects:
                row = next(
                    (c for c in cells if int(c["qos"]) == qos and int(c["disconnect_s"]) == d and c["rate_mode"] == rate),
                    None,
                )
                ys.append(float(row["loss_rate"]) * 100.0 if row else float("nan"))
            ax.plot(disconnects, ys, marker=marker, label=f"QoS {qos}")
        ax.set_xlabel("disconnect duration (s)")
        ax.set_ylabel("loss rate (%)")
        ax.set_title(f"{rate} ({backend})")
        ax.legend()
        ax.set_xticks(disconnects)
    fig.suptitle("Message loss vs disconnect duration")
    fig.tight_layout()
    p = out_dir / "loss_vs_disconnect.png"
    fig.savefig(p, dpi=120)
    plt.close(fig)
    written.append(p)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, rate in zip(axes, rates):
        for qos, marker in ((0, "o"), (1, "s")):
            ys = []
            for d in disconnects:
                row = next(
                    (c for c in cells if int(c["qos"]) == qos and int(c["disconnect_s"]) == d and c["rate_mode"] == rate),
                    None,
                )
                ys.append(float(row["duplicate_id_rate"]) * 100.0 if row else float("nan"))
            ax.plot(disconnects, ys, marker=marker, label=f"QoS {qos}")
        ax.set_xlabel("disconnect duration (s)")
        ax.set_ylabel("duplicate-id rate (%)")
        ax.set_title(f"{rate} ({backend})")
        ax.legend()
        ax.set_xticks(disconnects)
    fig.suptitle("Duplicate-id rate vs disconnect duration")
    fig.tight_layout()
    p = out_dir / "dup_vs_disconnect.png"
    fig.savefig(p, dpi=120)
    plt.close(fig)
    written.append(p)

    fig, ax = plt.subplots(figsize=(6, 5))
    for qos, marker in ((0, "o"), (1, "s")):
        xs, ys = [], []
        for c in cells:
            if int(c["qos"]) != qos:
                continue
            xs.append(float(c["usd_est_sum"]))
            ys.append(1.0 - float(c["loss_rate"]))
        ax.scatter(xs, ys, marker=marker, s=60, label=f"QoS {qos}")
        for c in cells:
            if int(c["qos"]) != qos:
                continue
            ax.annotate(
                f"d{c['disconnect_s']}/{c['rate_mode'][0]}",
                (float(c["usd_est_sum"]), 1.0 - float(c["loss_rate"])),
                fontsize=7,
                alpha=0.7,
            )
    ax.set_xlabel("estimated USD (unit prices × counted ops, safety factor)")
    ax.set_ylabel("delivery rate (1 − loss)")
    ax.set_title(f"Reliability–cost surface ({backend})")
    ax.legend()
    fig.tight_layout()
    p = out_dir / "reliability_cost_surface.png"
    fig.savefig(p, dpi=120)
    plt.close(fig)
    written.append(p)
    return written
