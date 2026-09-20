"""Tests for GCT loader: fail-closed without files; windows from 2011-shaped gzip."""
from __future__ import annotations

import gzip
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.gct_loader import inventory, load_gct_windows, require_gct

PERIOD_US = 300_000_000


def _usage_line(start: int, job: int, task: int, cpu: float, mem: float, disk: float, samp: float) -> str:
    # 20 ClusterData2011_2 task_usage fields
    end = start + PERIOD_US
    fields = [""] * 20
    fields[0] = str(start)
    fields[1] = str(end)
    fields[2] = str(job)
    fields[3] = str(task)
    fields[4] = "1"
    fields[5] = str(cpu)
    fields[6] = str(mem)
    fields[11] = str(disk)
    fields[19] = str(samp)
    return ",".join(fields) + "\n"


def _event_line(ts: int, job: int, task: int, event_type: int) -> str:
    fields = [""] * 13
    fields[0] = str(ts)
    fields[2] = str(job)
    fields[3] = str(task)
    fields[5] = str(event_type)
    return ",".join(fields) + "\n"


def test_require_gct_fail_closed(tmp_path):
    with pytest.raises(FileNotFoundError) as exc:
        require_gct(str(tmp_path))
    msg = str(exc.value)
    assert "task_events" in msg
    assert "task_usage" in msg


def test_gzip_fixture_fail_forces_l2(tmp_path):
    root = tmp_path / "gct"
    te = root / "2011" / "task_events"
    tu = root / "2011" / "task_usage"
    te.mkdir(parents=True)
    tu.mkdir(parents=True)
    t0 = 600_000_000
    # seq_length 10 + horizon 5 = 15 samples
    lines = [_usage_line(t0 + i * PERIOD_US, 11, 0, 0.2, 0.2, 0.001, 0.2) for i in range(15)]
    with gzip.open(tu / "part-00000-of-00001.csv.gz", "wt") as fh:
        fh.writelines(lines)
    # FAIL inside the future window of the only possible start=0 window
    fail_ts = t0 + 12 * PERIOD_US
    with gzip.open(te / "part-00000-of-00001.csv.gz", "wt") as fh:
        fh.write(_event_line(fail_ts, 11, 0, 3))
    X, y, is_transient = load_gct_windows(
        root=str(root), seq_length=10, horizon=5, max_windows=8, seed=0
    )
    assert X.shape == (1, 10, 4)
    assert y.shape == (1, 4)
    assert np.all(y == 2)
    assert bool(is_transient[0]) is True
    assert X.min() >= 0.0 and X.max() <= 1.0


def test_gzip_fixture_healthy_usage_labels(tmp_path):
    root = tmp_path / "gct"
    te = root / "2011" / "task_events"
    tu = root / "2011" / "task_usage"
    te.mkdir(parents=True)
    tu.mkdir(parents=True)
    t0 = 600_000_000
    lines = [_usage_line(t0 + i * PERIOD_US, 22, 0, 0.1, 0.1, 0.0, 0.1) for i in range(15)]
    with gzip.open(tu / "part-00000-of-00001.csv.gz", "wt") as fh:
        fh.writelines(lines)
    with gzip.open(te / "part-00000-of-00001.csv.gz", "wt") as fh:
        fh.write(_event_line(t0, 22, 0, 4))  # FINISH only, not a fail-family event
    X, y, is_transient = load_gct_windows(
        root=str(root), seq_length=10, horizon=5, max_windows=8, seed=0
    )
    assert X.shape[0] == 1
    assert np.all(y == 0)
    assert bool(is_transient[0]) is False


def test_inventory_keys():
    inv = inventory()
    assert "2011_ready" in inv
    assert "any_ready" in inv


@pytest.mark.skipif(not inventory()["2011_ready"], reason="GCT 2011 files not on disk")
def test_real_gct_windows_shape():
    X, y, is_transient = load_gct_windows(seq_length=10, horizon=5, max_windows=64)
    assert X.shape == (len(X), 10, 4)
    assert y.shape == (len(X), 4)
    assert is_transient.shape == (len(X),)
    assert set(np.unique(y)).issubset({0, 1, 2})
