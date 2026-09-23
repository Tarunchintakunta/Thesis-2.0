"""Phase runners end to end against the mock backend."""
import json
import random

import pytest

from coldstart.backends import MockBackend
from coldstart.cli import parse_duration_h
from coldstart.config import load_config, phase_cells, validate
from coldstart.driver import randomised_blocks, run_phase


def cfg_for(tmp_path, path="configs/experiment.yaml"):
    return load_config(path)


def rows(path):
    with open(path) as fh:
        return [json.loads(line) for line in fh]


def test_blocks_hold_every_cell_once_per_rep():
    cells = ["a", "b", "c", "d"]
    order = randomised_blocks(cells, 6, random.Random(1))
    for rep in range(6):
        assert sorted(c for r, c in order if r == rep) == cells
    assert len({tuple(c for r, c in order if r == rep) for rep in range(6)}) > 1


def test_cold_phase_measure_rows_are_cold(tmp_path):
    cfg = cfg_for(tmp_path)
    cfg["phases"]["package_size"]["reps"] = 3
    info = run_phase(MockBackend(seed=1), cfg, "package_size", tmp_path, seed=1)
    rs = rows(tmp_path / "package_size/invocations.jsonl")
    assert info["status"] == "complete" and info["invocations"] == 7 * 3 * 2
    assert all(r["tail_report"]["cold"] for r in rs if r["role"] == "measure")
    assert not any(r["tail_report"]["cold"] for r in rs if r["role"] == "follow_up")
    assert {r["data_mode"] for r in rs} == {"mock"}
    info = json.loads((tmp_path / "package_size/run_info.json").read_text())
    assert info["label"].startswith("SYNTHETIC") and info["mock_log_events"] == 3 * len(rs)


def test_warm_phase_is_steady_state(tmp_path):
    cfg = cfg_for(tmp_path)
    cfg["phases"]["baseline"]["reps"] = 2
    run_phase(MockBackend(seed=2), cfg, "baseline", tmp_path, seed=2)
    rs = rows(tmp_path / "baseline/invocations.jsonl")
    assert len(rs) == 4 * 2 * 3
    measured = [r for r in rs if r["role"] == "measure"]
    assert sorted({r["memory_mb"] for r in measured}) == [128, 512, 1024, 3008]
    assert not any(r["tail_report"]["cold"] for r in measured)


def test_warming_phase_pairs_the_arms(tmp_path):
    cfg = cfg_for(tmp_path)
    cfg["phases"]["warming"]["duration_h"] = 6
    run_phase(MockBackend(seed=3), cfg, "warming", tmp_path, seed=3)
    rs = rows(tmp_path / "warming/invocations.jsonl")
    on = [r for r in rs if r["warming"] == "on"]
    off = [r for r in rs if r["warming"] == "off"]
    assert len(on) == len(off) > 20
    frac = lambda xs: sum(r["tail_report"]["cold"] for r in xs) / len(xs)  # noqa: E731
    assert frac(on) < frac(off)
    assert all("block" in r for r in rs)


def test_burst_phase_from_quiet_state(tmp_path):
    cfg = cfg_for(tmp_path)
    cfg["phases"]["burst"].update(reps=2, concurrency=5)
    run_phase(MockBackend(seed=4), cfg, "burst", tmp_path, seed=4)
    rs = rows(tmp_path / "burst/invocations.jsonl")
    assert len(rs) == 3 * 2 * 5
    assert all(r["tail_report"]["cold"] for r in rs)
    assert len({r["burst_id"] for r in rs}) == 6


def test_idle_probe_records_gap(tmp_path):
    cfg = cfg_for(tmp_path, "configs/pilot.yaml")
    cfg["phases"]["idle_probe"]["reps"] = 2
    run_phase(MockBackend(seed=5), cfg, "idle_probe", tmp_path, seed=5)
    rs = [r for r in rows(tmp_path / "idle_probe/invocations.jsonl") if r["role"] == "measure"]
    assert sorted({r["idle_gap_min"] for r in rs}) == [5, 10, 20, 30, 45]


def test_existing_output_is_not_overwritten(tmp_path):
    cfg = cfg_for(tmp_path)
    cfg["phases"]["runtime_compare"]["reps"] = 1
    run_phase(MockBackend(seed=7), cfg, "runtime_compare", tmp_path, seed=7)
    with pytest.raises(FileExistsError):
        run_phase(MockBackend(seed=7), cfg, "runtime_compare", tmp_path, seed=7)


def test_same_seed_same_rows(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    for out in (a, b):
        cfg = cfg_for(tmp_path)
        cfg["phases"]["memory"]["reps"] = 2
        run_phase(MockBackend(seed=8), cfg, "memory", out, seed=8)
    assert (a / "memory/invocations.jsonl").read_text() == (b / "memory/invocations.jsonl").read_text()


def test_pilot_extends_experiment():
    cfg = load_config("configs/pilot.yaml")
    assert set(cfg["phases"]) == {"pilot_cold", "idle_probe"}
    assert cfg["arch"] == "arm64" and cfg["force_cold"] == "update_env"


def test_combined_cells_are_preregistered():
    cells = phase_cells(load_config("configs/experiment.yaml")["phases"]["combined"])
    assert ("python", "default", 128) in cells and ("java", "optimised", 1024) in cells
    assert len(cells) == 6


def test_bad_config_is_rejected():
    cfg = load_config("configs/experiment.yaml")
    cfg["phases"]["memory"]["runtimes"] = ["ruby"]
    with pytest.raises(ValueError):
        validate(cfg)


def test_duration_parser():
    assert parse_duration_h("2h") == 2.0
    assert parse_duration_h("90m") == 1.5
    assert parse_duration_h("3") == 3.0
