"""Run matrix, per-batch metrics and CloudWatch collection helpers."""
import datetime as dt
import gzip

import numpy as np
import pandas as pd
import pytest
import yaml

from analysis.batch_metrics import batch_metrics, read_raw
from scripts.collect_metrics import collect, merge_provisioned, window
from workloads.matrix import CONFIGS, lambda_events, scaled_profile, schedule, stable_seed, table_name

CFG = yaml.safe_load(open("config/experiment.yaml"))


def test_schedule_blocks_hold_every_cell_once():
    s = schedule(CFG, blocks=3)
    assert len(s) == 3 * 32
    for b in range(3):
        block = [(c["configuration"], c["workload"]) for c in s if c["block"] == b]
        assert len(set(block)) == 32
    orders = [tuple(c["batch_id"].split("-", 1)[1] for c in s if c["block"] == b) for b in range(3)]
    assert len(set(orders)) == 3  # a new random order in every block


def test_schedule_is_reproducible_and_seeds_are_stable():
    assert schedule(CFG, blocks=2) == schedule(CFG, blocks=2)
    assert stable_seed("b00-K1-on_demand-W1") == stable_seed("b00-K1-on_demand-W1")


def test_table_names_match_terraform():
    assert table_name("ddbpk", "K2", "on_demand") == "ddbpk-k2-ondemand"
    assert table_name("ddbpk", "K3", "provisioned") == "ddbpk-k3-provisioned"
    assert len(CONFIGS) == 8


def test_lambda_events_split_the_rate():
    cell = schedule(CFG, blocks=1)[0]
    evs = lambda_events(cell, CFG, "measure", 4, extra={"results_bucket": "b"})
    assert len(evs) == 4 and all(e["scale"] == 0.25 for e in evs)
    assert len({e["seed"] for e in evs}) == 4 and len({e["batch_id"] for e in evs}) == 4
    assert evs[0]["zipf_s"] == CFG["zipf"]["s"] and evs[0]["results_bucket"] == "b"


def test_scaled_profile():
    p = scaled_profile("W4", rate_scale=0.1, time_scale=0.5)
    assert p["cycle"] == [(20.0, 30.0), (100.0, 15.0)] and p["cycles"] == 2


def raw_bytes(rows):
    head = "seq,t_planned_s,t_start_s,latency_ms,response_ms,op,order,rank,ok,throttled,code,units\n"
    body = "".join(",".join(map(str, r)) + "\n" for r in rows)
    return gzip.compress((head + body).encode())


def test_batch_metrics_merge_lambdas_before_percentiles():
    a = [[i, 0, 0, 10.0, 10.0, "R", i, i, 1, 0, "", 0.5] for i in range(50)]
    b = [[i, 0, 0, 30.0, 30.0, "W", i, i, 1, 0, "", 1.0] for i in range(50)]
    t = [[0, 0, 0, 1.0, 1.0, "W", 1, 1, 0, 1, "ProvisionedThroughputExceededException", 0.0]]
    m = batch_metrics([read_raw(raw_bytes(a)), read_raw(raw_bytes(b + t))], wall_s=10)
    assert m["attempted"] == 101 and m["succeeded"] == 100 and m["throttled"] == 1 and m["errors"] == 0
    assert m["latency_mean_ms"] == pytest.approx(20.0)
    assert m["latency_p50_ms"] == pytest.approx(20.0)  # the merged median, not the mean of two medians
    assert m["rcu"] == pytest.approx(25.0) and m["wcu"] == pytest.approx(50.0)
    assert m["throughput_ops_s"] == pytest.approx(10.0)


def test_cloudwatch_window_is_whole_minutes():
    s, e = window(1_767_225_630.5, 1_767_225_700.0)
    assert s.second == 0 and e.second == 0 and s < e
    assert (e - s) >= dt.timedelta(minutes=2)


class FakeCW:
    def get_metric_data(self, MetricDataQueries, StartTime, EndTime):
        vals = {"m0": [100.0, 50.0], "m1": [10.0], "m2": [0.0], "m3": [3.0], "m4": [140.0, 160.0], "m5": [200.0]}
        return {"MetricDataResults": [{"Id": q["Id"], "Values": vals[q["Id"]]} for q in MetricDataQueries]}


def test_collect_and_merge_provisioned():
    b = pd.DataFrame([{"batch_id": "x", "table": "ddbpk-k1-provisioned", "capacity_mode": "provisioned",
                       "t_start_epoch": 1_767_225_600.0, "t_end_epoch": 1_767_225_690.0,
                       "prov_rcu_avg": 140.0, "prov_wcu_avg": 200.0, "prov_source": "config"},
                      {"batch_id": "y", "table": "ddbpk-k1-ondemand", "capacity_mode": "on_demand",
                       "t_start_epoch": 1_767_225_600.0, "t_end_epoch": 1_767_225_690.0,
                       "prov_rcu_avg": np.nan, "prov_wcu_avg": np.nan, "prov_source": ""}])
    cw = collect(b, FakeCW())
    assert cw.loc[0, "cw_ConsumedReadCapacityUnits"] == 150.0
    assert cw.loc[0, "cw_ProvisionedReadCapacityUnits"] == 150.0
    merged = merge_provisioned(b, cw)
    assert merged.loc[0, "prov_source"] == "cloudwatch" and merged.loc[0, "prov_rcu_avg"] == 150.0
    assert merged.loc[1, "prov_source"] == ""  # on-demand rows are left alone
