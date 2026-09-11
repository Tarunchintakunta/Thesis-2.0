import gzip

import pandas as pd
import pytest

from analysis.pilot_check import anova_power, check, drift


def raw(latencies):
    return pd.DataFrame({"ok": 1, "t_start_s": range(len(latencies)), "latency_ms": latencies})


def test_drift_between_first_and_last_third():
    assert drift(raw([10.0] * 30 + [10.0] * 30 + [12.0] * 30)) == pytest.approx(0.2)
    assert drift(raw([5.0] * 90)) == 0.0
    assert pd.isna(drift(raw([5.0] * 10)))


def test_power_of_the_planned_design():
    # 30 batches per cell, 6 cells: a medium effect (f = 0.25) should be found most of the time
    assert anova_power(0.25, 30, df1=2) > 0.8
    assert anova_power(0.25, 30, df1=1) > 0.8
    assert anova_power(0.25, 5, df1=2) < 0.5


def test_check_reads_batches_and_raw(tmp_path):
    (tmp_path / "raw").mkdir()
    head = "seq,t_planned_s,t_start_s,latency_ms,response_ms,op,order,rank,ok,throttled,code,units\n"
    body = "".join(f"{i},{i},{i},{10 + (i >= 60) * 5},{10},R,{i},{i},1,0,,0.5\n" for i in range(90))
    (tmp_path / "raw/b1.csv.gz").write_bytes(gzip.compress((head + body).encode()))
    pd.DataFrame([{"batch_id": "b1", "workload": "W1", "configuration": "K1-on_demand", "latency_mean_ms": 11.0,
                   "hot_rank_share": 0.9}]).to_csv(tmp_path / "batches.csv", index=False)
    res = check(tmp_path)
    assert res["settling"]["share_over_10pct"] == 1.0 and res["settling"]["lengthen_settling"] is True
    assert res["hot_rank_share"]["min"] == 0.9
