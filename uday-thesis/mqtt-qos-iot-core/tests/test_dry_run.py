import json
import os
from pathlib import Path

from common.models import ExperimentSpec, factorial
from simulator.campaign import run_campaign
from simulator.mock_broker import MockParams
from analysis.metrics import cell_rows, run_metrics
from analysis.stats_tests import run_confirmatory


def test_factorial_is_sixteen_cells_times_reps():
    specs = factorial(replications=5, n_messages=2, n_devices=1)
    assert len(specs) == 16 * 5
    cells = {(s.qos, s.disconnect_s, s.rate_mode) for s in specs}
    assert len(cells) == 16


def test_mini_campaign_writes_matchable_logs(tmp_path: Path):
    specs = [
        ExperimentSpec(qos=q, disconnect_s=d, rate_mode="steady", n_devices=2, n_messages=12, replication=1, seed=20 + q + d)
        for q in (0, 1)
        for d in (0, 15, 60)
    ]
    runs = run_campaign(specs, params=MockParams(p_network_loss_connected=0.0))
    assert len(runs) == 6
    rows = [run_metrics(r) for r in runs]
    cells = cell_rows(rows)
    stats = run_confirmatory(cells, rows)
    assert stats["adjustment"] == "holm-bonferroni"
    assert stats["n_tests"] > 0
    assert any(t["dv"] == "loss_rate" for t in stats["confirmatory"])
    # QoS0 at 60s must lose; QoS1 must lose less (harness property of the mock).
    c0 = next(c for c in cells if c["qos"] == 0 and c["disconnect_s"] == 60)
    c1 = next(c for c in cells if c["qos"] == 1 and c["disconnect_s"] == 60)
    assert c0["loss_rate"] > c1["loss_rate"]
    man = runs[0].manifest.to_dict()
    (tmp_path / "m.json").write_text(json.dumps(man))
    assert man["backend"] == "mock"


def test_lambda_handler_dry_build_item():
    os.environ["DRY_RUN_HANDLER"] = "1"
    os.environ.pop("DELIVERED_TABLE", None)
    import handler as ingest

    out = ingest.handler({"msg_id": "x", "device_id": "device-01", "qos": 1, "seq": 0, "ts_publish_ms": 1}, None)
    assert out["ok"] is True
    assert out["item"]["msg_id"] == "x"
    assert "delivery_id" in out["item"]
