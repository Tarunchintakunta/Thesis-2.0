"""The driver against in-memory DynamoDB (moto) - a functional check, not a measurement."""
import json

import pytest
import yaml

from driver import run, schedule

CFG = yaml.safe_load(open("config/experiment.yaml"))
QUIET = {"log": lambda *_: None}


def rows(folder):
    return [json.loads(line) for line in (folder / "deliveries.jsonl").read_text().splitlines()]


def test_record_is_found_in_a_lambda_log_tail():
    tail = ("START RequestId: abc Version: $LATEST\n"
            '2026-09-11T10:00:00.000Z\tabc\tINFO\t{"type": "delivery", "request_id": "r", "wcu": 1.0}\n'
            "2026-09-11T10:00:02.100Z abc Task timed out after 2.00 seconds\nEND RequestId: abc\n")
    assert run.last_record(tail)["wcu"] == 1.0
    assert run.last_record("Task timed out after 2.00 seconds") is None


def test_every_delivery_is_logged_with_its_capacity(ddb, tmp_path):
    reqs = schedule.build(CFG, "campaign", n_per_cell=2)
    info = run.run_phase(reqs, run.LocalBackend("moto"), tmp_path, max_invocations=1000, warmup_rounds=1, **QUIET)
    got = rows(tmp_path)
    assert len(got) == sum(r["multiplicity"] for r in reqs) == info["invocations"]
    assert info["warmup"] == {"calls": 1, "cold": 1}
    assert (tmp_path / "ground_truth.jsonl").exists() and (tmp_path / "schedule.csv").exists()
    assert {r["status"] for r in got if r["inject"] == "after_commit"} == {"timeout"}
    assert {r["status"] for r in got if r["inject"] == "none"} == {"ok"}
    assert all(r["consumed_capacity"] is not None for r in got)  # kept for timed-out deliveries too


def test_final_outcomes_per_path(ddb, tmp_path):
    reqs = schedule.build(CFG, "campaign", n_per_cell=2)
    run.run_phase(reqs, run.LocalBackend("moto"), tmp_path, max_invocations=1000, **QUIET)
    final = {(r["path"], r["multiplicity"]): r["outcome"] for r in rows(tmp_path) if r["delivery"] == r["multiplicity"]}
    assert final[("P1", 5)] == "APPLIED" and final[("P2", 5)] == "SUPPRESSED" and final[("P3", 5)] == "REPLAYED"
    assert {final[(p, 1)] for p in ("P1", "P2", "P3")} == {"APPLIED"}


def test_budget_is_checked_before_anything_is_written(ddb, tmp_path):
    reqs = schedule.build(CFG, "pilot", n_per_cell=2)
    with pytest.raises(RuntimeError):
        run.run_phase(reqs, run.LocalBackend(), tmp_path / "a", max_invocations=3, **QUIET)
    assert not (tmp_path / "a").exists()


def test_a_run_folder_is_never_reused(ddb, tmp_path):
    reqs = schedule.build(CFG, "pilot", n_per_cell=1)
    run.run_phase(reqs, run.LocalBackend(), tmp_path, max_invocations=100, **QUIET)
    with pytest.raises(FileExistsError):
        run.run_phase(reqs, run.LocalBackend(), tmp_path, max_invocations=100, **QUIET)
