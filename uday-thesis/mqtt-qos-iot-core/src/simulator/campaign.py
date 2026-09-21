"""One factorial cell: N simulated devices, device-side log, mock match backend."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

import numpy as np

from common.models import DeviceLogRow, ExperimentSpec, ReconnectStats, RunManifest
from simulator.disconnect import DisconnectWindow
from simulator.mock_broker import MockBroker, MockParams
from simulator.mock_dynamodb import MockDynamoDB
from simulator.schedule import publish_times

MEASUREMENT_KIND = "mock broker + in-memory DynamoDB — not an AWS measurement"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _envelope(row: DeviceLogRow) -> dict[str, Any]:
    return {
        "msg_id": row.msg_id,
        "device_id": row.device_id,
        "qos": row.qos,
        "seq": row.seq,
        "run_id": row.run_id,
        "config_id": row.config_id,
        "ts_publish_ms": row.ts_intended_publish_ms,
    }


def _run_device(
    *,
    spec: ExperimentSpec,
    run_id: str,
    device_id: str,
    table: MockDynamoDB,
    rng: np.random.Generator,
    params: MockParams,
) -> tuple[list[DeviceLogRow], ReconnectStats]:
    times = publish_times(spec.n_messages, spec.interval_s, spec.rate_mode)
    window = DisconnectWindow.from_schedule(times, spec.disconnect_s)
    broker = MockBroker(table, rng, params)
    recon = ReconnectStats()
    log: list[DeviceLogRow] = []
    flushed = False

    def maybe_flush(t_s: float) -> None:
        nonlocal flushed
        if flushed or not window.active():
            return
        if t_s < window.end_s:
            return
        queued, survived, delay = broker.flush_on_reconnect(int(window.end_s * 1000))
        recon.backlog_queued += queued
        recon.backlog_survived += survived
        recon.reconnect_time_ms = float(delay)
        flushed = True

    for seq, t_s in enumerate(times):
        maybe_flush(t_s)
        ts_ms = int(t_s * 1000)
        row = DeviceLogRow(
            msg_id=f"{run_id}:{device_id}:{seq:04d}",
            device_id=device_id,
            seq=seq,
            qos=spec.qos,
            rate_mode=spec.rate_mode,
            disconnect_s=spec.disconnect_s,
            replication=spec.replication,
            run_id=run_id,
            config_id=spec.config_id,
            ts_log_ms=ts_ms,
            ts_intended_publish_ms=ts_ms,
            payload_bytes=spec.payload_bytes,
        )
        log.append(row)
        env = _envelope(row)

        if window.disconnected_at(t_s):
            broker.publish_disconnected(env)
            continue

        inflight = window.in_inflight_cut(t_s, params.inflight_window_s)
        broker.publish_connected(env, ts_ms, maybe_inflight_cut=inflight)

    # End-of-run flush if disconnect ended after last message time.
    if window.active() and not flushed:
        end_t = max(times[-1] if times else 0.0, window.end_s)
        maybe_flush(end_t)
        if not flushed:
            queued, survived, delay = broker.flush_on_reconnect(int(window.end_s * 1000))
            recon.backlog_queued += queued
            recon.backlog_survived += survived
            recon.reconnect_time_ms = float(delay)
            flushed = True

    # QoS 1 connected-path retries (network loss) still sit in the outbox when
    # there was no disconnect window; flush once at end of the device schedule.
    if broker.outbox_depth() > 0:
        t_end_ms = int((times[-1] if times else 0.0) * 1000) + 1
        queued, survived, delay = broker.flush_on_reconnect(t_end_ms)
        recon.backlog_queued += queued
        recon.backlog_survived += survived
        if not recon.reconnect_time_ms:
            recon.reconnect_time_ms = float(delay)

    if window.active():
        recon.disconnect_events = 1

    # Attach broker counters onto reconnect stats object for aggregation.
    recon._counters = broker.counters  # type: ignore[attr-defined]
    return log, recon


@dataclass
class SpecRun:
    manifest: RunManifest
    device_log: list[dict[str, Any]]
    delivered: list[dict[str, Any]]
    reconnect: ReconnectStats
    counters: dict[str, Any]


def run_spec(spec: ExperimentSpec, params: MockParams | None = None) -> SpecRun:
    if spec.backend != "mock":
        raise RuntimeError("live AWS backend is blocked in this pass")
    params = params or MockParams()
    rng = np.random.default_rng(spec.seed)
    table = MockDynamoDB()
    run_id = f"mock-{spec.config_id}-s{spec.seed}"
    started = _utc_now()

    all_log: list[DeviceLogRow] = []
    recon_acc = ReconnectStats()
    counter_sum = {
        "publishes_attempted_connected": 0,
        "pubacks": 0,
        "reached_broker": 0,
        "rule_invocations": 0,
        "rule_failures": 0,
        "ddb_puts": 0,
        "qos0_dropped_disconnected": 0,
        "qos1_queued": 0,
        "qos1_dropped_cap": 0,
        "duplicates_injected": 0,
    }
    reconnect_times: list[float] = []

    for i in range(spec.n_devices):
        device_id = f"device-{i + 1:02d}"
        log, recon = _run_device(
            spec=spec,
            run_id=run_id,
            device_id=device_id,
            table=table,
            rng=rng,
            params=params,
        )
        all_log.extend(log)
        recon_acc.backlog_queued += recon.backlog_queued
        recon_acc.backlog_survived += recon.backlog_survived
        recon_acc.disconnect_events += recon.disconnect_events
        if recon.reconnect_time_ms:
            reconnect_times.append(float(recon.reconnect_time_ms))
        c = getattr(recon, "_counters", None)
        if c is not None:
            for k in counter_sum:
                counter_sum[k] += int(getattr(c, k, 0))

    if reconnect_times:
        recon_acc.reconnect_time_ms = float(np.mean(reconnect_times))

    finished = _utc_now()
    delivered = table.query_run(run_id)
    manifest = RunManifest(
        run_id=run_id,
        spec=spec.to_dict(),
        backend="mock",
        measurement_kind=MEASUREMENT_KIND,
        n_device_log=len(all_log),
        n_delivered_copies=len(delivered),
        started_at=started,
        finished_at=finished,
        seed=spec.seed,
        region=spec.region,
        extra={"git_note": "local dry-run", "uuid_ns": str(uuid.uuid4())},
    )
    return SpecRun(
        manifest=manifest,
        device_log=[r.to_dict() for r in all_log],
        delivered=delivered,
        reconnect=recon_acc,
        counters=dict(counter_sum),
    )


def run_campaign(specs: list[ExperimentSpec], params: MockParams | None = None) -> list[SpecRun]:
    return [run_spec(s, params=params) for s in specs]
