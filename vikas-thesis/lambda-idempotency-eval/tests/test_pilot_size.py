import numpy as np
import pandas as pd
import yaml

from analysis import pilot_size
from analysis.tables import SIGN

CFG = yaml.safe_load(open("config/experiment.yaml"))


def pilot(lat_cv=0.1, n=50, seed=1):
    rng = np.random.default_rng(seed)
    cap = {"P1": 2.0, "P2": 2.0, "P3": 4.0}
    return pd.DataFrame([{"path": p, "injected_retries": 1, "dup_mutations": int(p == "P1"), "capacity_total": cap[p],
                          "latency_ms": rng.normal(50, 50 * lat_cv)} for p in cap for _ in range(n)])


def choose(req):
    return pilot_size.choose_n(pilot_size.sizing_table(req, CFG), CFG)


def test_quiet_pilot_keeps_the_provisional_n():
    c = choose(pilot())
    assert c["N"] == 1000 and "supports" in c["reason"]


def test_noisy_latency_raises_n():
    c = choose(pilot(lat_cv=1.0))
    assert 1000 < c["N"] <= c["budget_max_n"] and "latency" in c["binding"]


def test_budget_caps_n():
    c = choose(pilot(lat_cv=5.0))
    assert c["N"] == c["budget_max_n"] == 2431 and "budget" in c["reason"]


def test_wilson_sizing():
    assert pilot_size.n_for_wilson(0.0, 0.01) == 189
    assert 9590 <= pilot_size.n_for_wilson(0.5, 0.01) <= 9610


def test_report_is_labelled_and_signed(tmp_path):
    s = pilot_size.sizing_table(pilot(), CFG)
    text = pilot_size.write_report(s, pilot_size.choose_n(s, CFG), {"backend": "moto"}, CFG, tmp_path).read_text()
    assert "NOT an AWS measurement" in text and "Wen et al. (2025)" in text
    assert text.rstrip().splitlines()[-1] == SIGN
