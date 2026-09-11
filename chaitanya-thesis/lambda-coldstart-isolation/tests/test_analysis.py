"""Analysis end to end on a small mock campaign."""
import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest

from coldstart.analysis import analyse, band
from coldstart.backends import MockBackend
from coldstart.config import load_config
from coldstart.cost_model import load_prices
from coldstart.driver import run_phase
from coldstart.logs import collect_mock
from coldstart.metrics import build_metrics, load_invocations, reports_frame

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cost_cli", ROOT / "scripts/cost_model.py")
cost_cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cost_cli)


@pytest.fixture(scope="module")
def campaign(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("campaign")
    cfg = load_config("configs/experiment.yaml")
    cfg["budget"]["spend_log"] = str(tmp / "spend.csv")
    small = {"baseline": 6, "runtime_compare": 10, "package_size": 10, "memory": 6, "burst": 2, "combined": 8}
    for name, reps in small.items():
        cfg["phases"][name]["reps"] = reps
    cfg["phases"]["warming"]["duration_h"] = 8
    b = MockBackend(seed=21)
    for name in cfg["phases"]:
        run_phase(b, cfg, name, tmp / "raw", seed=21)
    m = build_metrics(load_invocations(tmp / "raw"), reports_frame(collect_mock(tmp / "raw"), cfg["stack_name"]))
    costs = cost_cli.add_costs(m, load_prices(ROOT / "configs/pricing.yaml"), cfg["arch"])
    res = analyse(costs, cfg, tmp / "fig", tmp / "tab")
    return tmp, cfg, costs, res


def test_all_hypotheses_ran(campaign):
    _, _, _, res = campaign
    for k in ["H1", "H2_python", "H2_nodejs", "H2_java", "H3", "H4_python", "H4_nodejs", "H4_java",
              "combined_python", "combined_nodejs", "combined_java"]:
        assert k in res["tests"], k
        assert "p_holm" in res["tests"][k]
    assert res["tests"]["H1"]["family"] == "confirmatory"
    assert res["tests"]["H4_java"]["family"] == "exploratory:H4"


def test_holm_never_lowers_a_p_value(campaign):
    for t in campaign[3]["tests"].values():
        if "p_holm" in t:
            assert t["p_holm"] >= t["p"] - 1e-12


def test_outputs_written_and_labelled(campaign):
    tmp, _, _, res = campaign
    for f in ["baseline_style_duration_cost.png", "init_by_runtime.png", "package_size_effect.png",
              "memory_effect.png", "warming_frequency.png", "burst_latency.png", "decision_matrix.png"]:
        assert (tmp / "fig" / f).stat().st_size > 5000, f
    md = (tmp / "tab/decision_matrix.md").read_text()
    assert "SYNTHETIC" in md and "Provisioned concurrency" in md
    h = json.loads((tmp / "tab/hypotheses.json").read_text())
    assert h["data_mode"] == "mock" and "SYNTHETIC" in h["label"]


def test_decision_matrix_rows_and_bands(campaign):
    dm = pd.read_csv(campaign[0] / "tab/decision_matrix.csv")
    controls = set(dm["control"])
    assert {"Switch runtime", "Prune package", "Raise memory (exploratory)", "Low-frequency warming",
            "Combined free controls", "(Future) Provisioned concurrency"} <= controls
    assert set(dm["band"]) <= {"adopt", "situational", "avoid", "not tested"}
    warm = dm[dm["control"] == "Low-frequency warming"].iloc[0]
    assert warm["cold_freq_delta"] < 0  # the mock warmer does keep an environment alive


def test_phase_a_table_has_the_four_memories(campaign):
    pa = pd.read_csv(campaign[0] / "tab/phase_a_baseline_style.csv")
    assert list(pa["memory_mb"]) == [128, 512, 1024, 3008]
    assert pa["duration_p50_ms"].iloc[0] > pa["duration_p50_ms"].iloc[-1]


def test_mixed_modes_are_refused(campaign):
    _, cfg, costs, _ = campaign
    mixed = costs.copy()
    mixed.loc[mixed.index[:5], "data_mode"] = "live"
    with pytest.raises(ValueError):
        analyse(mixed, cfg, "/tmp/unused_fig", "/tmp/unused_tab")


def test_band_rule():
    assert band(True, 120, 50, 0.0005, 0.001) == "adopt"
    assert band(True, 120, 50, 0.01, 0.001) == "situational"
    assert band(False, 120, 50, 0.0, 0.001) == "avoid"
    assert band(True, 20, 50, 0.0, 0.001) == "avoid"
    assert band(None, 120, 50, 0.0, 0.001) == "not tested"
