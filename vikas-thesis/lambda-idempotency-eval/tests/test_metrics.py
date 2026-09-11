import numpy as np
import pandas as pd

from analysis import metrics
from tests.conftest import moto_run


def test_duplicates_are_counted_from_the_stream(ddb, tmp_path):
    gt, dl, st, _ = metrics.load_run(moto_run(ddb, tmp_path, "campaign", 3))
    req = metrics.per_request(gt, dl, st)
    by = req.groupby(["path", "multiplicity"])["dup_mutations"].sum()
    assert by[("P1", 5)] == 12 and by[("P1", 2)] == 3 and by[("P1", 1)] == 0
    assert by[("P2", 5)] == 0 and by[("P3", 5)] == 0
    assert (req["mutation_source"] == "stream").all() and not req["stream_self_mismatch"].any()
    assert (req["missing_deliveries"] == 0).all() and not req["no_mutation"].any()


def test_self_report_fallback_gives_the_same_counts(ddb, tmp_path):
    gt, dl, st, _ = metrics.load_run(moto_run(ddb, tmp_path, "campaign", 2))
    a, b = metrics.per_request(gt, dl, st), metrics.per_request(gt, dl, None)
    assert (b["mutation_source"] == "self_report").all()
    assert a["dup_mutations"].tolist() == b["dup_mutations"].tolist()


def test_cell_summary_rates_and_capacity(ddb, tmp_path):
    gt, dl, st, _ = metrics.load_run(moto_run(ddb, tmp_path, "campaign", 3))
    c = metrics.cell_summary(metrics.per_request(gt, dl, st), B=200).set_index(["path", "multiplicity"])
    assert c.loc[("P1", 5), "dup_rate"] == 1.0 and c.loc[("P2", 5), "dup_rate"] == 0.0
    assert c.loc[("P2", 5), "ccf_per_retry"] == 1.0 and c.loc[("P3", 5), "successful_retry_rate"] == 1.0
    assert c.loc[("P2", 5), "capacity_rule_mean"] == 4.0  # four failed conditions, billed by the rule
    assert np.isnan(c.loc[("P1", 1), "dup_rate"])  # one delivery = no retry


def test_crash_between_writes_is_a_duplicate_for_p3(ddb, tmp_path):
    gt, dl, st, _ = metrics.load_run(moto_run(ddb, tmp_path, "sensitivity", 3))
    c = metrics.cell_summary(metrics.per_request(gt, dl, st), B=200).set_index(["path", "multiplicity"])
    assert c.loc[("P3", 2), "dup_rate"] == 1.0 and c.loc[("P3", 5), "dup_rate"] == 1.0


def test_a_lost_log_record_is_counted_not_hidden():
    gt = pd.DataFrame([{"request_id": "r", "phase": "campaign", "path": "P1", "multiplicity": 2,
                        "inject_mode": "after_commit", "injected_retries": 1}])
    base = {"request_id": "r", "path": "P1", "multiplicity": 2, "ccf": 0, "wcu_ccf_rule": 0.0, "ddb_ms": 3.0,
            "cold_start": False, "outcome": "APPLIED"}
    dl = pd.DataFrame([{**base, "delivery": 1, "status": "timeout", "consumed_capacity": None, "business_writes": None,
                        "rtt_ms": 2100.0},
                       {**base, "delivery": 2, "status": "ok", "consumed_capacity": 1.0, "business_writes": 1,
                        "rtt_ms": 40.0}])
    req = metrics.per_request(gt, dl)
    assert req["lost_records"].iloc[0] == 1 and req["latency_ms"].iloc[0] == 40.0
