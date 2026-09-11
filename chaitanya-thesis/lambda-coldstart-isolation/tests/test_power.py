import importlib.util
import shutil
from pathlib import Path

import pytest

from coldstart.analysis import load_plan
from coldstart.backends import MockBackend
from coldstart.config import load_config
from coldstart.driver import run_phase
from coldstart.logs import collect_mock
from coldstart.metrics import build_metrics, load_invocations, reports_frame
from coldstart.power import END, START, n_per_group, pilot_report, replace_section, report_markdown

ROOT = Path(__file__).resolve().parents[1]


def test_n_per_group_textbook_value():
    # 2 * ((1.96 + 0.8416) * 100 / 50)^2 = 62.8 -> 63
    assert n_per_group(100, 50, 0.05, 0.8) == 63
    assert n_per_group(100, 50, 0.05, 0.8, are=0.864) == 73
    assert n_per_group(0, 50, 0.05, 0.8) == 2


def test_replace_section_keeps_the_rest():
    text = f"top\n{START}\nold stuff\n{END}\nbottom\n"
    out = replace_section(text, "new stuff\n")
    assert "old stuff" not in out and "new stuff" in out
    assert out.startswith("top") and out.endswith("bottom\n")
    with pytest.raises(ValueError):
        replace_section("no markers", "x")


@pytest.fixture(scope="module")
def pilot(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("pilot")
    cfg = load_config("configs/pilot.yaml")
    cfg["budget"]["spend_log"] = str(tmp / "spend.csv")
    cfg["phases"]["pilot_cold"]["reps"] = 8
    cfg["phases"]["idle_probe"]["reps"] = 6
    b = MockBackend(seed=31)
    for name in cfg["phases"]:
        run_phase(b, cfg, name, tmp / "raw", seed=31)
    m = build_metrics(load_invocations(tmp / "raw"), reports_frame(collect_mock(tmp / "raw"), cfg["stack_name"]))
    m.to_csv(tmp / "metrics.csv", index=False)
    return tmp, m


def test_pilot_report_on_mock(pilot):
    _, m = pilot
    r = pilot_report(m, load_plan(), load_config("configs/experiment.yaml"))
    assert len(r["cells"]) == 6
    assert len(r["comparisons"]) == 6  # 3 runtime pairs (H1) + 3 package pairs (H2)
    assert all(v >= 30 for v in r["recommended"].values())
    assert r["recommended"]["memory"] == 40  # exploratory: plan kept
    assert r["update_env_cold"][0] == r["update_env_cold"][1] == 48
    assert [g["idle_gap_min"] for g in r["idle_probe"]] == [5, 10, 20, 30, 45]
    assert set(r["planned_reps"]) == {"runtime_compare", "package_size", "memory", "combined"}
    md = report_markdown(r, "test")
    assert "SYNTHETIC" in md and "| idle gap (min)" in md


def test_mock_pilot_is_not_written_into_the_plan(pilot, tmp_path):
    spec = importlib.util.spec_from_file_location("pilot_power", ROOT / "scripts/pilot_power.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    plan = tmp_path / "ANALYSIS_PLAN.md"
    shutil.copy(ROOT / "docs/ANALYSIS_PLAN.md", plan)
    src = pilot[0] / "metrics.csv"
    assert mod.main(["--in", str(src), "--out", str(plan)]) == 2
    assert "Not run yet" in plan.read_text()
    assert mod.main(["--in", str(src), "--out", str(plan), "--allow-mock"]) == 0
    text = plan.read_text()
    assert "Not run yet" not in text and "SYNTHETIC mock pilot" in text and "## 8. Amendments" in text
