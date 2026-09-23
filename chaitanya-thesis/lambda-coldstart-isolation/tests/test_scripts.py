"""Command-line scripts: mock log printer and the whole CLI chain."""
import importlib.util
import json
from pathlib import Path

import pandas as pd

from coldstart.cli import main as invoke_main
from coldstart.report_parser import parse_log_text

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_mock_cloudwatch_lines():
    text = "\n".join(load("mock_cloudwatch").lines("java-default", 512, 6, 3, 0))
    reps = parse_log_text(text)
    assert len(reps) == 6
    assert [r.cold for r in reps] == [True, False, False, True, False, False]
    assert {r.memory_mb for r in reps} == {512}


def test_mock_cloudwatch_refuses_live(monkeypatch):
    monkeypatch.setenv("DATA_MODE", "live")
    assert load("mock_cloudwatch").main([]) == 2


def test_cli_chain_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_MODE", "mock")
    raw, proc = tmp_path / "raw", tmp_path / "proc"
    assert invoke_main("idle", {"cold"}, ["--phase", "package_size", "--reps", "4", "--out", str(raw)]) == 0
    assert invoke_main("steady", {"warm", "warming"}, ["--phase", "warming", "--duration", "3h", "--out", str(raw)]) == 0
    assert load("collect_logs").main(["--runs", str(raw)]) == 0
    assert load("parse_report_metrics").main(["--in", str(raw), "--out", str(proc / "metrics.csv")]) == 0
    assert load("cost_model").main(["--in", str(proc / "metrics.csv"), "--out", str(proc / "costs.csv")]) == 0
    assert load("analyse").main(["--in", str(proc), "--out", str(tmp_path / "fig"), str(tmp_path / "tab")]) == 0
    costs = pd.read_csv(proc / "costs.csv")
    assert costs["cost_usd"].notna().all() and set(costs["data_mode"]) == {"mock"}
    h = json.loads((tmp_path / "tab/hypotheses.json").read_text())
    assert {"H2_python", "H2_nodejs", "H2_java", "H3"} <= set(h["tests"])
    assert any("H1" in n for n in h["notes"])  # runtime_compare was not run, the note says so


def test_invoker_rejects_phase_of_the_wrong_kind(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_MODE", "mock")
    assert invoke_main("burst", {"burst"}, ["--phase", "baseline", "--out", str(tmp_path)]) == 2
    assert invoke_main("idle", {"cold"}, ["--phase", "nope", "--out", str(tmp_path)]) == 2
