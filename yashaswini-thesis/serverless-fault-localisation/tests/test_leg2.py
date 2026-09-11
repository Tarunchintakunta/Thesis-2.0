import json

import numpy as np

from eval import leg2

SERVICES = ["checkoutservice", "currencyservice", "emailservice", "frontend", "paymentservice"]


def write(raw, method, case, ranking, root, fault, **extra):
    d = raw / method
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{case}.json").write_text(json.dumps({"case": case, "ranking": ranking, "root_cause": root, "fault": fault,
                                                "error": None, **extra}))


def fake_raw(tmp_path, n=40, seed=0):
    rng = np.random.default_rng(seed)
    raw = tmp_path / "raw"
    for i in range(n):
        root = SERVICES[i % 5]
        fault = ["delay", "loss", "cpu", "mem"][i % 4]
        case = f"re2ob_{root}_{fault}_{i}"
        others = [s for s in SERVICES if s != root]
        good = [root, *others]                                   # baseline: always right
        rules = good if rng.random() < 0.6 else [*others[:2], root, *others[2:]]  # rules: right 60 %, else 3rd
        write(raw, "rules", case, rules, root, fault, detected=bool(rng.random() < 0.9),
              delay_s=float(rng.integers(10, 60)), control_fp_episodes=int(rng.random() < 0.2), rank_seconds=0.5)
        write(raw, "baro", case, good, root, fault, seconds=1.0)
        if i % 2 == 0:  # a slow baseline that only ran on half the cases
            write(raw, "deep", case, [*others[:1], root, *others[1:]], root, fault, seconds=290.0)
    write(raw, "baro", "re2ob_extra_delay_99", SERVICES, "extra", "delay", seconds=1.0)  # not a rule-arm case
    return raw


def test_leg2_tables_tests_and_expectation(tmp_path):
    res = leg2.analyse(fake_raw(tmp_path), tmp_path / "out", tmp_path / "fig", B=300)
    loc = res["localisation"].set_index("method")
    assert len(res["ranks"]) == 40 and loc.loc["deep", "cases"] == 20 and len(res["common"]) == 3
    assert loc.loc["baro", "ac@1"] == 1.0 and loc.loc["rules", "ac@3"] == 1.0 and loc.loc["deep", "ac@1"] == 0.0
    assert 0.4 < loc.loc["rules", "ac@1"] < 0.8
    cmp_ = res["comparisons"].set_index(["baseline", "outcome"])
    assert cmp_.loc[("baro", "top-1"), "p_holm"] < 0.05 and not cmp_.loc[("baro", "top-3"), "reject_h0"]
    assert cmp_.loc[("deep", "top-1"), "cases"] == 20
    assert res["top3"]["decision"] == "refuted"  # everyone reaches 100 % top-3: the rule arm concedes nothing there
    assert 0 < res["detection"]["f1"] < 1
    text = (tmp_path / "out" / "summary.md").read_text()
    assert "not AWS" in text and text.rstrip().splitlines()[-1] == leg2.SIGN
    assert (tmp_path / "fig" / "localisation.png").stat().st_size > 5000


def test_a_failed_baseline_case_counts_as_a_miss(tmp_path):
    raw = fake_raw(tmp_path, n=5)
    f = raw / "baro" / "re2ob_checkoutservice_delay_0.json"
    d = json.loads(f.read_text())
    d.update(ranking=[], error="boom")
    f.write_text(json.dumps(d))
    tab = leg2.ranks_table(leg2.load(raw))
    assert tab.loc["re2ob_checkoutservice_delay_0", "baro"] == len(SERVICES) + 1
