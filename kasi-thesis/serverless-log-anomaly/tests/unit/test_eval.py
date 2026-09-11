import numpy as np
import pandas as pd
import pytest

from logad.eval.metrics import (block_scores, false_alarm_rate, far_blocks, injection_table, per_category, prf,
                                window_blocks)
from logad.eval.stats import bootstrap_ci, friedman, holm, mcnemar, paired_power_n, paired_test
from logad.inject.schedule import Injection


def test_prf():
    r = prf([1, 1, 0, 0, 1], [1, 0, 0, 1, 1])
    assert (r["tp"], r["fp"], r["fn"], r["tn"]) == (2, 1, 1, 1)
    assert r["precision"] == pytest.approx(2 / 3)
    assert r["f1"] == pytest.approx(2 / 3)
    assert prf([0, 0], [0, 0])["f1"] == 0.0


def test_false_alarm_rate():
    assert false_alarm_rate([True, False, False, False]) == 0.25


def test_per_category_uses_all_normal_windows():
    pred = [True, True, False, True]
    label = [True, True, False, False]
    cat = ["a", "b", "", ""]
    res = per_category(pred, label, cat)
    assert res["a"]["fp"] == 1 and res["a"]["tp"] == 1


def test_injection_table_delay():
    starts = np.arange(0, 600, 60.0)
    sched = [Injection(0, 0, "x", 130, 250), Injection(1, 0, "y", 400, 460)]
    pred = np.zeros(10, dtype=bool)
    pred[3] = True
    t = injection_table(pred, starts, 60, sched)
    assert t["detected"].tolist() == [True, False]
    assert t.loc[0, "delay_s"] == pytest.approx(50.0)


def test_window_blocks_follow_the_next_injection():
    starts = np.array([0, 100, 200, 300, 400.0])
    sched = [Injection(0, 0, "x", 50, 150), Injection(1, 1, "y", 250, 350)]
    assert window_blocks(starts, sched).tolist() == [0, 0, 1, 1, 1]


def test_block_scores_and_far_blocks():
    df = pd.DataFrame({"seed": 1, "block": [0, 0, 1, 1], "label": [True, False, True, False],
                       "category": ["a", "", "b", ""], "pred": [True, False, False, False],
                       "start": [0, 60, 1800, 1860]})
    b = block_scores(df, "pred")
    assert b["f1"].tolist() == [1.0, 0.0]
    f = far_blocks(df.assign(pred=[True, True, False, False]), "pred")
    assert f["far"].tolist() == [1.0, 0.0]


def test_paired_test_picks_t_or_wilcoxon():
    rng = np.random.default_rng(0)
    a = rng.normal(0.8, 0.05, 40)
    res = paired_test(a, a - 0.1 + rng.normal(0, 0.01, 40))
    assert res["p"] < 1e-6 and res["mean_diff"] == pytest.approx(0.1, abs=0.01)
    skew = paired_test(np.r_[np.zeros(30), np.ones(10)], np.zeros(40))
    assert skew["test"].startswith("Wilcoxon")
    same = paired_test([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    assert same["p"] == 1.0


def test_friedman_and_kendalls_w():
    m = np.column_stack([np.linspace(0, 1, 20), np.linspace(0, 1, 20) + 0.5, np.linspace(0, 1, 20) + 1.0])
    res = friedman(m)
    assert res["p"] < 1e-6 and res["effect_size"] == pytest.approx(1.0)
    assert friedman(np.ones((5, 3)))["p"] == 1.0


def test_mcnemar_exact_and_chi2():
    a = np.array([True] * 10 + [False] * 10)
    b = np.array([False] * 10 + [False] * 10)
    small = mcnemar(a, b)
    assert small["exact"] and small["b10"] == 10 and small["p"] < 0.01
    a2 = np.array([True] * 40 + [False] * 40)
    b2 = np.array([False] * 40 + [True] * 5 + [False] * 35)
    assert not mcnemar(a2, b2)["exact"]


def test_holm_and_bootstrap_and_power():
    adj = holm({"a": 0.01, "b": 0.03, "c": 0.04})
    assert adj == pytest.approx({"a": 0.03, "b": 0.06, "c": 0.06})
    lo, hi = bootstrap_ci(np.random.default_rng(1).normal(5, 1, 300))
    assert lo < 5 < hi
    assert paired_power_n(0.2, 0.1) > paired_power_n(0.05, 0.1)
