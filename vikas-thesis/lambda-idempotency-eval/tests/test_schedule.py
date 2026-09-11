import csv
import json
from collections import Counter

import yaml

from driver import schedule
from lambda_fn.paths import business_item, write_units

CFG = yaml.safe_load(open("config/experiment.yaml"))


def test_campaign_has_every_cell():
    reqs = schedule.build(CFG, "campaign", n_per_cell=20)
    cells = Counter((r["path"], r["multiplicity"]) for r in reqs)
    assert len(cells) == 9 and set(cells.values()) == {20}
    assert {r["inject_mode"] for r in reqs} == {"after_commit"}


def test_requests_are_interleaved_not_grouped():
    reqs = schedule.build(CFG, "campaign", n_per_cell=20)
    first = [r["path"] for r in reqs[:30]]
    assert len(set(first)) == 3


def test_pilot_and_sensitivity_phases():
    pilot = schedule.build(CFG, "pilot")
    assert len(pilot) == 150 and {r["multiplicity"] for r in pilot} == {2}
    sens = schedule.build(CFG, "sensitivity", n_per_cell=10)
    assert {r["path"] for r in sens} == {"P3"} and {r["multiplicity"] for r in sens} == {2, 5}
    assert {r["inject_mode"] for r in sens} == {"p3_between"}


def test_deliveries_inject_on_all_but_the_last():
    r = {"multiplicity": 5, "inject_mode": "after_commit"}
    d = schedule.deliveries(r)
    assert [x["inject"] for x in d] == ["after_commit"] * 4 + ["none"]
    assert schedule.deliveries({"multiplicity": 1, "inject_mode": "after_commit"}) == [{"delivery": 1, "inject": "none"}]


def test_same_seed_same_schedule_and_unique_ids():
    a = schedule.build(CFG, "campaign", n_per_cell=5)
    b = schedule.build(CFG, "campaign", n_per_cell=5)
    assert a == b
    assert len({r["request_id"] for r in a}) == len(a)


def test_ground_truth_file(tmp_path):
    reqs = schedule.build(CFG, "pilot", n_per_cell=3)
    p = schedule.write_ground_truth(reqs, tmp_path / "gt.jsonl")
    rows = [json.loads(line) for line in p.read_text().splitlines()]
    assert len(rows) == 9 and all("payload" not in r for r in rows)
    assert all(r["injected_retries"] == r["intended_deliveries"] - 1 for r in rows)


def test_schedule_file_lists_every_planned_delivery(tmp_path):
    reqs = schedule.build(CFG, "campaign", n_per_cell=2)
    rows = list(csv.DictReader(open(schedule.write_schedule(reqs, tmp_path / "s.csv"))))
    assert len(rows) == sum(r["multiplicity"] for r in reqs)
    assert sum(r["inject"] != "none" for r in rows) == sum(r["injected_retries"] for r in reqs)


def test_payload_keeps_the_item_at_one_write_unit():
    import random
    p = schedule.payload(random.Random(1), 1)
    item = business_item("f" * 36, p, "e" * 36, 5)
    assert write_units(item) == 1.0
