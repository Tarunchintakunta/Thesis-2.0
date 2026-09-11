"""Join of client records and REPORT lines, including warmer pings and warm-discards."""
import pandas as pd

from coldstart.backends import MockBackend
from coldstart.config import load_config
from coldstart.driver import run_phase
from coldstart.logs import collect_mock, function_of
from coldstart.metrics import build_metrics, discarded_intended_colds, load_invocations, reports_frame

STACK = "coldstart-study"


def run(tmp_path, phases, edits=None):
    cfg = load_config("configs/experiment.yaml")
    cfg["budget"]["spend_log"] = str(tmp_path / "spend.csv")
    for (phase, key), value in (edits or {}).items():
        cfg["phases"][phase][key] = value
    b = MockBackend(seed=11)
    for p in phases:
        run_phase(b, cfg, p, tmp_path / "raw", seed=11)
    inv = load_invocations(tmp_path / "raw")
    return inv, reports_frame(collect_mock(tmp_path / "raw"), STACK)


def test_every_client_row_matches_a_log_report(tmp_path):
    inv, reps = run(tmp_path, ["runtime_compare"], {("runtime_compare", "reps"): 3})
    m = build_metrics(inv, reps)
    assert len(m) == len(inv)
    assert (m["report_source"] == "logs").all()
    assert m.loc[m["role"] == "measure", "cold"].all()
    assert m["init_ms"].notna().sum() == m["cold"].sum()


def test_tail_is_the_fallback_when_logs_are_missing(tmp_path):
    inv, reps = run(tmp_path, ["runtime_compare"], {("runtime_compare", "reps"): 2})
    m = build_metrics(inv, reps.iloc[0:0])
    assert (m["report_source"] == "tail").all()
    assert m.loc[m["role"] == "measure", "cold"].all()


def test_warmer_pings_are_kept_but_flagged(tmp_path):
    inv, reps = run(tmp_path, ["warming"], {("warming", "duration_h"): 2})
    m = build_metrics(inv, reps)
    pings = m[m["role"] == "warmer_ping"]
    assert len(pings) >= 20  # every 5 minutes for ~2 hours
    assert (pings["function"] == "warm-target").all()
    assert (m.loc[m["role"] == "measure", "report_source"] == "logs").all()


def test_idle_method_can_come_back_warm_and_is_counted(tmp_path):
    cfg_edit = {("runtime_compare", "reps"): 6}
    cfg = load_config("configs/experiment.yaml")
    cfg["budget"]["spend_log"] = str(tmp_path / "spend.csv")
    cfg["force_cold"] = "idle"
    cfg["idle_gap_min"] = 6  # shorter than the mock's typical idle lifetime -> some stay warm
    cfg["phases"]["runtime_compare"]["reps"] = cfg_edit[("runtime_compare", "reps")]
    b = MockBackend(seed=12)
    run_phase(b, cfg, "runtime_compare", tmp_path / "raw", seed=12)
    m = build_metrics(load_invocations(tmp_path / "raw"), reports_frame(collect_mock(tmp_path / "raw"), STACK))
    d = discarded_intended_colds(m)
    assert d["intended_cold"].sum() == 18
    assert d["came_back_warm"].sum() > 0


def test_error_flag(tmp_path):
    inv = pd.DataFrame([{"seq": 0, "phase": "p", "data_mode": "mock", "function": "python-default",
                         "request_id": "r1", "status": 200, "function_error": "Unhandled", "rtt_ms": 5.0,
                         "t_start": 1.0, "tail_report": None}])
    m = build_metrics(inv, reports_frame([], STACK))
    assert bool(m.loc[0, "error"]) and m.loc[0, "report_source"] == "missing" and not m.loc[0, "cold"]


def test_function_of_log_group():
    assert function_of("/aws/lambda/coldstart-study-java-default", STACK) == "java-default"
    assert function_of("/aws/lambda/other-java-default", STACK) is None
