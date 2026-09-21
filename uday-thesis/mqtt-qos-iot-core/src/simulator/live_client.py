"""Live AWS IoT Core MQTT publisher (device cert TLS via paho-mqtt)."""

from __future__ import annotations

import json
import ssl
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import paho.mqtt.client as mqtt


class LiveAwsError(RuntimeError):
    pass


@dataclass
class LiveDeviceSession:
    thing_name: str
    endpoint: str
    cert_path: Path
    key_path: Path
    ca_path: Path
    client: mqtt.Client | None = None
    connected: bool = False
    pubacks: int = 0
    publishes_ok: int = 0
    outbox: list[tuple[dict[str, Any], int]] = field(default_factory=list)

    def connect(self) -> None:
        client_id = self.thing_name
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
            protocol=mqtt.MQTTv311,
        )
        self.client.tls_set(
            ca_certs=str(self.ca_path),
            certfile=str(self.cert_path),
            keyfile=str(self.key_path),
            tls_version=ssl.PROTOCOL_TLS_CLIENT,
        )
        self.client.on_connect = self._on_connect
        self.client.on_publish = self._on_publish
        self.client.connect(self.endpoint, 8883, keepalive=60)
        self.client.loop_start()
        deadline = time.time() + 15
        while not self.connected and time.time() < deadline:
            time.sleep(0.05)
        if not self.connected:
            raise LiveAwsError(f"MQTT connect timeout for {self.thing_name}")

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):  # noqa: ANN001
        rc = int(getattr(reason_code, "value", reason_code))
        self.connected = rc == 0

    def _on_publish(self, client, userdata, mid, reason_codes=None, properties=None):  # noqa: ANN001
        self.pubacks += 1

    def disconnect(self) -> None:
        if self.client is None:
            return
        try:
            self.client.loop_stop()
            self.client.disconnect()
        finally:
            self.connected = False
            self.client = None

    def publish(self, topic: str, payload: dict[str, Any], qos: int) -> bool:
        if not self.connected or self.client is None:
            if qos >= 1:
                self.outbox.append((payload, qos))
            return False
        body = json.dumps(payload, separators=(",", ":"))
        info = self.client.publish(topic, body, qos=int(qos))
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            if qos >= 1:
                self.outbox.append((payload, qos))
            return False
        self.publishes_ok += 1
        if qos >= 1:
            info.wait_for_publish(timeout=10)
        return True

    def flush_outbox(self, topic: str) -> tuple[int, int]:
        queued = len(self.outbox)
        survived = 0
        pending = list(self.outbox)
        self.outbox.clear()
        for payload, qos in pending:
            if self.publish(topic, payload, qos):
                survived += 1
            else:
                self.outbox.append((payload, qos))
        return queued, survived


def ensure_amazon_root_ca(path: Path) -> Path:
    """Download Amazon Root CA 1 once into the certs dir if missing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and path.stat().st_size > 0:
        return path
    import urllib.request

    url = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
    with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310
        path.write_bytes(resp.read())
    return path


def load_stack_meta(certs_dir: Path) -> dict[str, Any]:
    meta_path = certs_dir / "stack_meta.json"
    if not meta_path.is_file():
        raise LiveAwsError(f"missing {meta_path}; terraform apply with enable_apply=true first")
    return json.loads(meta_path.read_text())


def device_paths(certs_dir: Path, index: int) -> tuple[Path, Path]:
    d = certs_dir / f"device-{index:02d}"
    return d / "cert.pem", d / "private.key"


def open_sessions(
    *,
    endpoint: str,
    thing_names: list[str],
    certs_dir: Path,
    n_devices: int,
) -> list[LiveDeviceSession]:
    ca = ensure_amazon_root_ca(certs_dir / "AmazonRootCA1.pem")
    sessions: list[LiveDeviceSession] = []
    for i in range(n_devices):
        if i >= len(thing_names):
            raise LiveAwsError(f"need {n_devices} things; stack has {len(thing_names)}")
        cert, key = device_paths(certs_dir, i + 1)
        if not cert.is_file() or not key.is_file():
            raise LiveAwsError(f"missing certs for device-{i + 1:02d} under {certs_dir}")
        sess = LiveDeviceSession(
            thing_name=thing_names[i],
            endpoint=endpoint,
            cert_path=cert,
            key_path=key,
            ca_path=ca,
        )
        sess.connect()
        sessions.append(sess)
    return sessions


def query_delivered(table_name: str, run_id: str, region: str) -> list[dict[str, Any]]:
    import boto3

    table = boto3.resource("dynamodb", region_name=region).Table(table_name)
    items: list[dict[str, Any]] = []
    kwargs: dict[str, Any] = {
        "IndexName": "run_id-index",
        "KeyConditionExpression": "run_id = :r",
        "ExpressionAttributeValues": {":r": run_id},
    }
    while True:
        resp = table.query(**kwargs)
        items.extend(resp.get("Items") or [])
        if "LastEvaluatedKey" not in resp:
            break
        kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]
    # Normalize numeric types from DynamoDB Decimal
    out: list[dict[str, Any]] = []
    for it in items:
        out.append(
            {
                "msg_id": str(it.get("msg_id", "")),
                "delivery_id": str(it.get("delivery_id", "")),
                "device_id": str(it.get("device_id", "")),
                "qos": int(it.get("qos", 0)),
                "seq": int(it.get("seq", 0)),
                "run_id": str(it.get("run_id", "")),
                "config_id": str(it.get("config_id", "")),
                "ts_publish_ms": int(it.get("ts_publish_ms", 0)),
                "ts_ingest_ms": int(it.get("ts_ingest_ms", 0)),
                "source": str(it.get("source", "iot-rule")),
            }
        )
    return out


def new_run_id(config_id: str, seed: int) -> str:
    return f"live-{config_id}-s{seed}-{uuid.uuid4().hex[:8]}"
