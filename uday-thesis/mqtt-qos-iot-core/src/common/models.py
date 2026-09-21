"""Shared experiment types. Formal factorial is the source of truth."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

QOS_LEVELS: tuple[int, ...] = (0, 1)
DISCONNECT_S: tuple[int, ...] = (0, 15, 60, 300)
RATE_MODES: tuple[str, ...] = ("steady", "bursty")


@dataclass(frozen=True)
class FormalScale:
    devices: int = 5
    messages: int = 1000
    replications: int = 5
    interval_s: float = 5.0
    payload_bytes: int = 64


FORMAL = FormalScale()


@dataclass
class ExperimentSpec:
    qos: int
    disconnect_s: int
    rate_mode: str
    n_devices: int = FORMAL.devices
    n_messages: int = FORMAL.messages
    replication: int = 1
    interval_s: float = FORMAL.interval_s
    payload_bytes: int = FORMAL.payload_bytes
    seed: int = 42
    backend: str = "mock"
    region: str = "eu-west-1"

    def __post_init__(self) -> None:
        if self.qos not in QOS_LEVELS:
            raise ValueError(f"qos must be 0 or 1 (IoT Core device-to-cloud); got {self.qos}")
        if self.disconnect_s not in DISCONNECT_S:
            raise ValueError(f"disconnect_s must be one of {DISCONNECT_S}")
        if self.rate_mode not in RATE_MODES:
            raise ValueError(f"rate_mode must be one of {RATE_MODES}")
        if self.backend not in ("mock", "live"):
            raise ValueError("backend must be mock or live")

    @property
    def config_id(self) -> str:
        return f"qos{self.qos}_d{self.disconnect_s}_{self.rate_mode}_r{self.replication}"

    @property
    def cell_id(self) -> str:
        return f"qos{self.qos}_d{self.disconnect_s}_{self.rate_mode}"

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["config_id"] = self.config_id
        d["cell_id"] = self.cell_id
        return d


def factorial(
    qos: Iterable[int] = QOS_LEVELS,
    disconnect_s: Iterable[int] = DISCONNECT_S,
    rate: Iterable[str] = RATE_MODES,
    replications: int = FORMAL.replications,
    n_devices: int = FORMAL.devices,
    n_messages: int = FORMAL.messages,
    interval_s: float = FORMAL.interval_s,
    payload_bytes: int = FORMAL.payload_bytes,
    seed: int = 42,
    backend: str = "mock",
) -> list[ExperimentSpec]:
    """Expand QoS × disconnect × rate × replication with deterministic seeds."""
    specs: list[ExperimentSpec] = []
    for q in qos:
        for d in disconnect_s:
            for r in rate:
                for rep in range(1, int(replications) + 1):
                    burst_offset = 7 if str(r) == "bursty" else 0
                    cell_seed = int(seed) + int(q) * 17 + int(d) + burst_offset + (rep - 1) * 1000
                    specs.append(
                        ExperimentSpec(
                            qos=int(q),
                            disconnect_s=int(d),
                            rate_mode=str(r),
                            n_devices=int(n_devices),
                            n_messages=int(n_messages),
                            replication=rep,
                            interval_s=float(interval_s),
                            payload_bytes=int(payload_bytes),
                            seed=cell_seed,
                            backend=backend,
                        )
                    )
    return specs


@dataclass
class DeviceLogRow:
    msg_id: str
    device_id: str
    seq: int
    qos: int
    rate_mode: str
    disconnect_s: int
    replication: int
    run_id: str
    config_id: str
    ts_log_ms: int
    ts_intended_publish_ms: int
    payload_bytes: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DeliveredRow:
    msg_id: str
    delivery_id: str
    device_id: str
    qos: int
    seq: int
    run_id: str
    config_id: str
    ts_publish_ms: int
    ts_ingest_ms: int
    source: str = "mock"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReconnectStats:
    reconnect_time_ms: float = 0.0
    backlog_queued: int = 0
    backlog_survived: int = 0
    disconnect_events: int = 0


@dataclass
class RunManifest:
    run_id: str
    spec: dict[str, Any]
    backend: str
    measurement_kind: str
    n_device_log: int
    n_delivered_copies: int
    started_at: str
    finished_at: str
    seed: int
    region: str
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
