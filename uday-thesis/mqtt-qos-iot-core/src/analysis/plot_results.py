"""Figures for mock (or later live) cell summaries. Always labelled as such."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_cells(cells: list[dict[str, Any]], out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    backend = cells[0]["backend"] if cells else "mock"
    disconnects = sorted({int(c["disconnect_s"]) for c in cells})
    rates = sorted({c["rate_mode"] for c in cells})
    written: list[Path] = []

    fig, axes = plt.subplots(1, len(rates), figsize=(10, 4), sharey=True)
    if len(rates) == 1:
        axes = [axes]
    for ax, rate in zip(axes, rates):
        for qos, marker in ((0, "o"), (1, "s")):
            ys = []
            for d in disconnects:
                row = next(c for c in cells if c["qos"] == qos and c["disconnect_s"] == d and c["rate_mode"] == rate)
                ys.append(row["loss_rate"] * 100)
            ax.plot(disconnects, ys, marker=marker, label=f"QoS {qos}")
        ax.set_xlabel("disconnect (s)")
        ax.set_ylabel("loss rate (%)")
        ax.set_title(rate)
        ax.legend()
        ax.set_xticks(disconnects)
    fig.suptitle("Message loss vs disconnect duration")
    fig.tight_layout()
    p = out_dir / "loss_vs_disconnect.png"
    fig.savefig(p, dpi=120)
    plt.close(fig)
    written.append(p)

    fig, axes = plt.subplots(1, len(rates), figsize=(10, 4), sharey=True)
    if len(rates) == 1:
        axes = [axes]
    for ax, rate in zip(axes, rates):
        for qos, marker in ((0, "o"), (1, "s")):
            ys = []
            for d in disconnects:
                row = next(c for c in cells if c["qos"] == qos and c["disconnect_s"] == d and c["rate_mode"] == rate)
                ys.append(row["duplicate_id_rate"] * 100)
            ax.plot(disconnects, ys, marker=marker, label=f"QoS {qos}")
        ax.set_xlabel("disconnect (s)")
        ax.set_ylabel("duplicate-id rate (%)")
        ax.set_title(rate)
        ax.legend()
        ax.set_xticks(disconnects)
    fig.suptitle("Duplicate-id rate vs disconnect duration")
    fig.tight_layout()
    p = out_dir / "dup_vs_disconnect.png"
    fig.savefig(p, dpi=120)
    plt.close(fig)
    written.append(p)

    fig, ax = plt.subplots(figsize=(6, 5))
    for c in cells:
        ax.scatter(c["usd_est_sum"], c["loss_rate"] * 100, c=("C0" if c["qos"] == 0 else "C1"), marker=("o" if c["rate_mode"] == "steady" else "x"), s=40 + 4 * np.sqrt(c["disconnect_s"] + 1))
    ax.set_xlabel("estimated USD (unit prices × counted ops, safety factor)")
    ax.set_ylabel("loss rate (%)")
    ax.set_title(f"Reliability–cost surface ({backend})")
    fig.tight_layout()
    p = out_dir / "reliability_cost_surface.png"
    fig.savefig(p, dpi=120)
    plt.close(fig)
    written.append(p)
    return written
