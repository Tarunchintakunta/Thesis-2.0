"""Fail-closed / ready-state trace loader tests."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data.trace_loader import (
    alibaba_derived_ready,
    cluster_workload_from_frame,
    gct2011_derived_ready,
    load_alibaba_cluster,
    load_gct2010_cluster,
    load_gct2011_cluster,
    load_gct2011_jobs,
    load_scaling_workload,
    missing_checklist,
    require_dataset,
    resolve_formal_source,
)


def test_gct2019_still_fail_closed():
    with pytest.raises(FileNotFoundError, match="fail-closed"):
        require_dataset("gct2019")


def test_checklist_mentions_data_gaps():
    text = missing_checklist("gct2019")
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


@pytest.mark.skipif(not gct2011_derived_ready(), reason="GCT 2011 derived sample not present")
def test_gct2011_sample_loads():
    src = resolve_formal_source("gct2011")
    assert src["dataset"] == "gct2011"
    assert src["proxy"] is False
    assert src["evidence"] == "TRACE"
    df = load_gct2011_cluster()
    assert len(df) >= 5
    jobs = load_gct2011_jobs()
    assert {"job_id", "time_s", "cpu_cores_sum"} <= set(jobs.columns)
    series, meta = load_scaling_workload("gct2011")
    assert meta["proxy"] is False
    assert len(series) >= 5


@pytest.mark.skipif(not alibaba_derived_ready(), reason="Alibaba derived sample not present")
def test_alibaba_sample_loads():
    src = resolve_formal_source("alibaba")
    assert src["dataset"] == "alibaba"
    assert src["sample_kind"] == "HTTP_RANGE_64MiB"
    df = load_alibaba_cluster()
    assert len(df) >= 20
    series, meta = load_scaling_workload("alibaba", max_steps=50)
    assert len(series) == 50
    assert meta["proxy"] is False


def test_gct_alias_prefers_2011_when_ready():
    src = resolve_formal_source("gct")
    if gct2011_derived_ready():
        assert src["dataset"] == "gct2011"
    else:
        assert src["dataset"] == "gct2010"


def test_gct_does_not_silently_use_synthetic():
    series, meta = load_scaling_workload("gct2010")
    assert meta["proxy"] is False
    assert len(series) < 200


def test_synthetic_is_explicit_proxy():
    series, meta = load_scaling_workload("synthetic", seed=42, synthetic_steps=40)
    assert meta["proxy"] is True
    assert len(series) == 40


def test_cluster_drop_zero_tail():
    df = pd.DataFrame({"time_s": [1, 2, 3], "cpu_cores_sum": [1.0, 2.0, 0.0]})
    v = cluster_workload_from_frame(df, drop_zero_tail=True)
    np.testing.assert_array_equal(v, [1.0, 2.0])
