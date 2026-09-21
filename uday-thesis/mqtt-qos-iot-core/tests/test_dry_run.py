import json
import os
from pathlib import Path

from analysis.stats_tests import run_confirmatory
from common.config import load_experiment, mock_params, specs_from_cfg
from common.models import factorial
from simulator.campaign import run_campaign


def test_dry_run_factorial_and_holm(tmp_path: Path):
    cfg = load_experiment()
    specs = specs_from_cfg(cfg, scale="dry_run")
    assert len(specs) == 2 * 4 * 2 * 2  # qos × disconnect × rate × reps
    assert all(s.backend == "mock" for s in specs)
    # Deterministic seed formula (matches prior mock manifests).
    s = next(x for x in specs if x.qos == 0 and x.disconnect_s == 15 and x.rate_mode == "steady" and x.replication == 1)
    assert s.seed == 57

    # Smoke a tiny subset for speed.
    tiny = factorial(
        qos=[0, 1],
        disconnect_s=[0, 15],
        rate=["steady"],
        replications=1,
        n_devices=2,
        n_messages=20,
        interval_s=1.0,
        seed=42,
        backend="mock",
    )
    params = mock_params(cfg)
    runs = run_campaign(tiny, params=params)
    from analysis.metrics import cell_rows, run_metrics

    run_rows = [run_metrics(r) for r in runs]
    cells = cell_rows(run_rows)
    conf = run_confirmatory(cells, run_rows, alpha=0.05)
    assert conf["adjustment"] == "holm-bonferroni"
    assert conf["n_tests"] >= 1
    assert any(c["disconnect_s"] == 15 for c in cells)

    m = tmp_path / "m.json"
    m.write_text(json.dumps(runs[0].manifest.to_dict()))
    assert json.loads(m.read_text())["backend"] == "mock"


def test_lambda_handler_dry_run(monkeypatch):
    monkeypatch.setenv("DRY_RUN_HANDLER", "1")
    monkeypatch.setenv("DELIVERED_TABLE", "unused")
    import handler as ingest

    out = ingest.handler(
        {
            "msg_id": "m1",
            "device_id": "device-01",
            "qos": 1,
            "seq": 0,
            "run_id": "r",
            "config_id": "c",
            "ts_publish_ms": 0,
        },
        None,
    )
    assert out["ok"] is True
    assert out["dry_run"] is True
    assert out["item"]["msg_id"] == "m1"
    assert "delivery_id" in out["item"]
