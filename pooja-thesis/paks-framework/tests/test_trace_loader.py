"""Fail-closed trace loader tests."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data.trace_loader import (
    cluster_workload_from_frame,
    load_gct2010_cluster,
    load_scaling_workload,
    missing_checklist,
    require_dataset,
    resolve_formal_source,
)


def test_gct2011_fail_closed():
    with pytest.raises(FileNotFoundError, match="fail-closed"):
        require_dataset("gct2011")


def test_gct2019_fail_closed():
    with pytest.raises(FileNotFoundError, match="fail-closed"):
        require_dataset("gct2019")


def test_alibaba_fail_closed():
    with pytest.raises(FileNotFoundError, match="fail-closed"):
        require_dataset("alibaba")


def test_checklist_mentions_data_gaps():
    text = missing_checklist("gct2011")
    assert "DATA_GAPS.md" in text
    assert "synthetic" in text.lower()


def test_gct2010_committed_slice_loads():
    src = resolve_formal_source("gct2010")
    assert src["proxy"] is False
    assert src["dataset"] == "gct2010"
    df = load_gct2010_cluster()
    assert len(df) >= 20
    series = cluster_workload_from_frame(df)
    assert series.dtype == np.float64
    assert np.all(np.isfinite(series))
    assert series[0] >= 0


def test_gct_alias_uses_2010_when_2011_absent():
    src = resolve_formal_source("gct")
    assert src["dataset"] == "gct2010"
    assert "2011" in src.get("residual", "") or "2011" in src.get("note", "")


def test_gct_does_not_silently_use_synthetic():
    series, meta = load_scaling_workload("gct2010")
    assert meta["proxy"] is False
    assert len(series) == len(np.unique(series)) or len(series) > 10
    # sine-proxy has ~500 steps by default; GCT v1 cluster is ~76
    assert len(series) < 200


def test_synthetic_is_explicit_proxy():
    series, meta = load_scaling_workload("synthetic", seed=42, synthetic_steps=40)
    assert meta["proxy"] is True
    assert len(series) == 40


def test_cluster_drop_zero_tail():
    df = pd.DataFrame({"time_s": [1, 2, 3], "cpu_cores_sum": [1.0, 2.0, 0.0]})
    v = cluster_workload_from_frame(df, drop_zero_tail=True)
    np.testing.assert_array_equal(v, [1.0, 2.0])
