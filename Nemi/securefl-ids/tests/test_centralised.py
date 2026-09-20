"""Tests for centralised IDS comparator."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.centralised.centralised_ids import CentralisedIDS


@pytest.fixture
def tiny_csv(tmp_path):
    """Minimal numeric CSV compatible with UNSWDataLoader."""
    rng = np.random.default_rng(0)
    n = 200
    rows = ["f1,f2,f3,f4,label"]
    for i in range(n):
        label = 0 if i < 160 else 1
        feats = rng.normal(size=4)
        rows.append(",".join(str(x) for x in list(feats) + [label]))
    path = tmp_path / "tiny.csv"
    path.write_text("\n".join(rows) + "\n")
    return str(path)


def test_centralised_runs_and_summarises(tiny_csv):
    trainer = CentralisedIDS()
    trainer.setup(data_path=tiny_csv, sample_size=None)
    history = trainer.train(epochs=2, learning_rate=0.01, batch_size=32)
    assert len(history["epochs"]) == 2
    summary = trainer.get_results_summary()
    assert summary["mode"] == "centralised"
    assert summary["avg_communication_cost"] == 0.0
    assert 0.0 <= summary["accuracy"] <= 1.0
