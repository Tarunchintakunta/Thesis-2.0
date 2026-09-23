"""One factorial cell: N simulated devices, device-side log, mock match backend."""

from __future__ import annotations

from collections import Counter

import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from common.models import DeviceLogRow, ExperimentSpec, ReconnectStats, RunManifest
from simulator.disconnect import DisconnectWindow
from simulator.mock_broker import MockBroker, MockParams
from simulator.mock_dynamodb import MockDynamoDB
from simulator.schedule import publish_times

MEASUREMENT_KIND = "mock broker + in-memory DynamoDB — not an AWS measurement"
LIVE_MEASUREMENT_KIND = "AWS IoT Core rules → Lambda → DynamoDB (live)"


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
    if spec.backend == "live":
        return run_spec_live(spec)
    if spec.backend != "mock":
        raise RuntimeError(f"unknown backend: {spec.backend}")
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


def run_spec_live(spec: ExperimentSpec, *, settle_s: float = 3.0) -> SpecRun:
    """Wall-clock live publish to IoT Core; match via DynamoDB GSI."""
    import time

    from simulator.live_client import (
        LiveAwsError,
        LiveDeviceSession,
        load_stack_meta,
        new_run_id,
        open_sessions,
        query_delivered,
    )

    root = Path(__file__).resolve().parents[2]
    certs_dir = root / ".certs"
    meta = load_stack_meta(certs_dir)
    region = str(meta.get("region") or spec.region)
    thing_names = list(meta.get("thing_names") or [])
    table_name = str(meta.get("delivered_table") or "")
    if not table_name:
        raise LiveAwsError("stack_meta missing delivered_table")

    import boto3

    endpoint = boto3.client("iot", region_name=region).describe_endpoint(
        endpointType="iot:Data-ATS"
    )["endpointAddress"]

    run_id = new_run_id(spec.config_id, spec.seed)
    started = _utc_now()
    times = publish_times(spec.n_messages, spec.interval_s, spec.rate_mode)
    window = DisconnectWindow.from_schedule(times, spec.disconnect_s)

    sessions = open_sessions(
        endpoint=endpoint,
        thing_names=thing_names,
        certs_dir=certs_dir,
        n_devices=spec.n_devices,
    )

    all_log: list[DeviceLogRow] = []
    recon_acc = ReconnectStats()
    counter_sum = {
        "publishes_attempted_connected": 0,
        "pubacks": 0,
        "reached_broker": 0,
        "qos0_dropped_disconnected": 0,
        "qos1_queued": 0,
    }
    reconnect_times: list[float] = []

    def _run_one_device(i: int, sess: LiveDeviceSession) -> None:
        device_id = f"device-{i + 1:02d}"
        topic = f"devices/{sess.thing_name}/telemetry"
        flushed = False
        t0 = time.monotonic()

        for seq, t_s in enumerate(times):
            target = t0 + t_s
            now = time.monotonic()
            if target > now:
                time.sleep(target - now)

            if window.active() and not flushed and t_s >= window.end_s:
                t_re_start = time.monotonic()
                if not sess.connected:
                    sess.connect()
                queued, survived = sess.flush_outbox(topic)
                recon_acc.backlog_queued += queued
                recon_acc.backlog_survived += survived
                counter_sum["qos1_queued"] += queued
                rt = (time.monotonic() - t_re_start) * 1000.0
                recon_acc.reconnect_time_ms = rt
                reconnect_times.append(rt)
                flushed = True

            ts_ms = int(time.time() * 1000)
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
            all_log.append(row)
            env = _envelope(row)

            if window.disconnected_at(t_s):
                if sess.connected:
                    sess.disconnect()
                    recon_acc.disconnect_events += 1
                if spec.qos >= 1:
                    sess.outbox.append((env, spec.qos))
                    counter_sum["qos1_queued"] += 1
                else:
                    counter_sum["qos0_dropped_disconnected"] += 1
                continue

            if not sess.connected:
                sess.connect()

            counter_sum["publishes_attempted_connected"] += 1
            ok = sess.publish(topic, env, spec.qos)
            if ok:
                counter_sum["reached_broker"] += 1
                if spec.qos >= 1:
                    counter_sum["pubacks"] += 1

        if window.active() and not flushed:
            if not sess.connected:
                sess.connect()
            queued, survived = sess.flush_outbox(topic)
            recon_acc.backlog_queued += queued
            recon_acc.backlog_survived += survived
        elif sess.outbox:
            queued, survived = sess.flush_outbox(topic)
            recon_acc.backlog_queued += queued
            recon_acc.backlog_survived += survived

    try:
        for i, sess in enumerate(sessions):
            _run_one_device(i, sess)
    finally:
        for sess in sessions:
            try:
                sess.disconnect()
            except Exception:  # noqa: BLE001
                pass

    time.sleep(float(settle_s))
    delivered = query_delivered(table_name, run_id, region)
    counter_sum["rule_invocations"] = len(delivered)
    counter_sum["ddb_puts"] = len(delivered)
    msg_ids = [str(d.get("msg_id") or "") for d in delivered if d.get("msg_id")]
    unique_delivered = len(set(msg_ids))
    reached = int(counter_sum["reached_broker"])
    counter_sum["rule_failures"] = max(0, reached - unique_delivered)
    id_counts = Counter(msg_ids)
    counter_sum["duplicates_injected"] = int(sum(c - 1 for c in id_counts.values() if c > 1))
    finished = _utc_now()
    if reconnect_times:
        recon_acc.reconnect_time_ms = float(np.mean(reconnect_times))

    manifest = RunManifest(
        run_id=run_id,
        spec=spec.to_dict(),
        backend="live",
        measurement_kind=LIVE_MEASUREMENT_KIND,
        n_device_log=len(all_log),
        n_delivered_copies=len(delivered),
        started_at=started,
        finished_at=finished,
        seed=spec.seed,
        region=region,
        extra={
            "iot_endpoint": endpoint,
            "table": table_name,
            "uuid_ns": str(uuid.uuid4()),
            "settle_s": settle_s,
        },
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
