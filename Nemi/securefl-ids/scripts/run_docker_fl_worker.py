#!/usr/bin/env python3
"""Multi-container FL worker (orchestrator | client) via shared volume.

Artefact path for cloud-native evidence: each client runs in its own container;
orchestrator aggregates FedAvg across round files under SHARED_DIR.
Not Kubernetes; Docker Compose is the executed cloud-native packaging.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import torch

from src.common.data_loader import create_federated_data
from src.common.models import create_model


def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name, default)
    if v is None:
        raise SystemExit(f"missing env {name}")
    return v


def _wait_file(path: Path, timeout_s: float = 600.0) -> None:
    t0 = time.time()
    while not path.exists():
        if time.time() - t0 > timeout_s:
            raise TimeoutError(f"timeout waiting for {path}")
        time.sleep(0.5)


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)


def _save_state(path: Path, state: dict) -> None:
    buf = __import__("io").BytesIO()
    torch.save(state, buf)
    _atomic_write_bytes(path, buf.getvalue())


def _load_state(path: Path) -> dict:
    return torch.load(path, map_location="cpu", weights_only=False)


def run_client() -> None:
    client_id = int(_env("CLIENT_ID"))
    num_clients = int(_env("NUM_CLIENTS", "2"))
    num_rounds = int(_env("NUM_ROUNDS", "3"))
    sample_rows = int(_env("SAMPLE_ROWS", "2500"))
    shared = Path(_env("SHARED_DIR", "/shared"))
    shared.mkdir(parents=True, exist_ok=True)

    ready = shared / f"client{client_id}.ready"
    ready.write_text("ok", encoding="utf-8")

    fed = create_federated_data(
        num_clients=num_clients,
        sample_size=sample_rows,
        alpha=0.5,
        binary=True,
    )
    X_train, y_train = fed["train_clients"][client_id]
    n_features = X_train.shape[1]
    model = create_model("cnn", input_dim=n_features, num_classes=2)

    for rnd in range(num_rounds):
        gpath = shared / f"round{rnd}_global.pt"
        _wait_file(gpath, timeout_s=900.0)
        state = _load_state(gpath)
        model.load_state_dict(state)
        model.train()
        opt = torch.optim.Adam(model.parameters(), lr=1e-3)
        loss_fn = torch.nn.CrossEntropyLoss()
        xb = torch.FloatTensor(np.asarray(X_train, dtype=np.float32))
        yb = torch.LongTensor(np.asarray(y_train, dtype=np.int64))
        for _ in range(2):
            opt.zero_grad()
            logits = model(xb)
            loss = loss_fn(logits, yb)
            loss.backward()
            opt.step()
        out = shared / f"round{rnd}_client{client_id}.pt"
        _save_state(out, model.state_dict())
        (shared / f"round{rnd}_client{client_id}.done").write_text("ok", encoding="utf-8")

    (shared / f"client{client_id}.finished").write_text("ok", encoding="utf-8")
    while not (shared / "orchestrator.done").exists():
        time.sleep(1.0)


def run_orchestrator() -> None:
    num_clients = int(_env("NUM_CLIENTS", "2"))
    num_rounds = int(_env("NUM_ROUNDS", "3"))
    sample_rows = int(_env("SAMPLE_ROWS", "2500"))
    shared = Path(_env("SHARED_DIR", "/shared"))
    out_json = Path(_env("OUT_JSON", str(shared / "docker_fl_summary.json")))
    shared.mkdir(parents=True, exist_ok=True)

    for cid in range(num_clients):
        _wait_file(shared / f"client{cid}.ready")

    fed = create_federated_data(
        num_clients=num_clients,
        sample_size=sample_rows,
        alpha=0.5,
        binary=True,
    )
    n_features = fed["num_features"]
    global_model = create_model("cnn", input_dim=n_features, num_classes=2)

    t0 = time.time()
    for rnd in range(num_rounds):
        gpath = shared / f"round{rnd}_global.pt"
        _save_state(gpath, global_model.state_dict())
        for cid in range(num_clients):
            _wait_file(shared / f"round{rnd}_client{cid}.done", timeout_s=900.0)
        states = [_load_state(shared / f"round{rnd}_client{cid}.pt") for cid in range(num_clients)]
        avg = {}
        for k in states[0]:
            avg[k] = sum(s[k] for s in states) / float(num_clients)
        global_model.load_state_dict(avg)

    X_te, y_te = fed["test_set"]
    global_model.eval()
    with torch.no_grad():
        logits = global_model(torch.FloatTensor(np.asarray(X_te, dtype=np.float32)))
        pred = logits.argmax(dim=1).numpy()
    y_te = np.asarray(y_te)
    acc = float((pred == y_te).mean())
    tp = int(((pred == 1) & (y_te == 1)).sum())
    fp = int(((pred == 1) & (y_te == 0)).sum())
    fn = int(((pred == 0) & (y_te == 1)).sum())
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0

    summary = {
        "mode": "docker_compose_multi_container",
        "num_clients": num_clients,
        "num_rounds": num_rounds,
        "sample_rows": sample_rows,
        "accuracy": acc,
        "f1": f1,
        "elapsed_s": time.time() - t0,
        "containers": [f"securefl-client{i}" for i in range(num_clients)] + ["securefl-orchestrator"],
        "note": "Clients are separate containers; FedAvg via shared volume. Not K8s.",
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(summary, indent=2)
    out_json.write_text(text, encoding="utf-8")
    host_out = Path("/out/docker_fl_summary.json")
    if host_out.parent.exists():
        host_out.write_text(text, encoding="utf-8")
    (shared / "orchestrator.done").write_text("ok", encoding="utf-8")
    print(text)


def main() -> None:
    role = _env("ROLE", "orchestrator")
    if role == "client":
        run_client()
    else:
        run_orchestrator()


if __name__ == "__main__":
    main()
