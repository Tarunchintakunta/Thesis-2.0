"""Per-run and per-cell metrics for loss / dup / latency / reconnect / cost."""

from __future__ import annotations

from typing import Any

import numpy as np

from analysis.cost import estimate_usd
from matching.matcher import match_logs
from simulator.campaign import SpecRun


def run_metrics(run: SpecRun) -> dict[str, Any]:
    matched = match_logs(run.device_log, run.delivered)
    spec = run.manifest.spec
    duration_s = float(spec["n_messages"]) * float(spec["interval_s"])
    cost = estimate_usd(run.counters, duration_s, int(spec["n_devices"]))
    reached = max(1, int(run.counters.get("reached_broker", 0)))
    rule_success = float(run.counters.get("rule_invocations", 0)) / float(reached)

    row = {
        "run_id": run.manifest.run_id,
        "backend": run.manifest.backend,
        "measurement_kind": run.manifest.measurement_kind,
        "qos": spec["qos"],
        "disconnect_s": spec["disconnect_s"],
        "rate_mode": spec["rate_mode"],
        "replication": spec["replication"],
        "cell_id": spec["cell_id"],
        "config_id": spec["config_id"],
        "n_devices": spec["n_devices"],
        "n_messages_per_device": spec["n_messages"],
        "seed": run.manifest.seed,
        "n_published": matched.n_published,
        "n_lost": matched.n_lost,
        "n_delivered_unique": matched.n_delivered_unique,
        "n_duplicate_ids": matched.n_duplicate_ids,
        "n_delivery_copies": matched.n_delivery_copies,
        "loss_rate": matched.loss_rate,
        "duplicate_id_rate": matched.duplicate_id_rate,
        "extra_copy_rate": matched.extra_copy_rate,
        "latency_mean_ms": matched.latency_mean_ms,
        "latency_p95_ms": matched.latency_p95_ms,
        "latency_p99_ms": matched.latency_p99_ms,
        "reconnect_time_ms": run.reconnect.reconnect_time_ms,
        "backlog_queued": run.reconnect.backlog_queued,
        "backlog_survived": run.reconnect.backlog_survived,
        "rule_trigger_success_rate": rule_success,
        "usd_est": cost["usd_with_safety"],
        "usd_raw": cost["usd_raw"],
        "iot_messages_counted": cost["messages_counted"],
        "latencies_ms": matched.latencies_ms,
        "counters": run.counters,
    }
    return row


def cell_rows(run_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pool published/lost/dup across replications of the same cell."""
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in run_rows:
        groups.setdefault(str(row["cell_id"]), []).append(row)

    out: list[dict[str, Any]] = []
    for cell_id, rows in sorted(groups.items()):
        n_pub = sum(int(r["n_published"]) for r in rows)
        n_lost = sum(int(r["n_lost"]) for r in rows)
        n_dup = sum(int(r["n_duplicate_ids"]) for r in rows)
        lat: list[float] = []
        for r in rows:
            lat.extend(list(r.get("latencies_ms") or []))
        out.append(
            {
                "cell_id": cell_id,
                "qos": rows[0]["qos"],
                "disconnect_s": rows[0]["disconnect_s"],
                "rate_mode": rows[0]["rate_mode"],
                "n_runs": len(rows),
                "n_published": n_pub,
                "n_lost": n_lost,
                "n_duplicate_ids": n_dup,
                "loss_rate": (n_lost / n_pub) if n_pub else float("nan"),
                "duplicate_id_rate": (n_dup / n_pub) if n_pub else float("nan"),
                "latency_mean_ms": float(np.mean(lat)) if lat else float("nan"),
                "latency_p95_ms": float(np.percentile(lat, 95)) if lat else float("nan"),
                "latency_p99_ms": float(np.percentile(lat, 99)) if lat else float("nan"),
                "reconnect_time_ms_mean": float(
                    np.mean([float(r.get("reconnect_time_ms", 0.0)) for r in rows])
                ),
                "backlog_queued_sum": int(sum(int(r.get("backlog_queued", 0)) for r in rows)),
                "backlog_survived_sum": int(sum(int(r.get("backlog_survived", 0)) for r in rows)),
                "usd_est_sum": float(sum(float(r.get("usd_est", 0.0)) for r in rows)),
                "backend": rows[0].get("backend"),
                "latencies_ms": lat,
            }
        )
    return out
