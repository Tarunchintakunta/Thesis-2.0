"""analysis/analyse.py on a hand-made batches table (test input only - not a result)."""
import json

import numpy as np
import pandas as pd
import pytest
import yaml

from analysis import analyse as A
from analysis.fetch_prices import extract, render
from workloads.matrix import CONFIGS

CFG = yaml.safe_load(open("config/experiment.yaml"))
CFG["analysis"]["bootstrap"] = 200


def fake_batches(source="moto-smoke", n=5, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for w in ["W1", "W2", "W3", "W4"]:
        for k, m in CONFIGS:
            for r in range(n):
                lat = 5 + (2 if k == "K3" else 0) + rng.normal(0, 0.3)
                rows.append({"batch_id": f"b{r:02d}-{k}-{m}-{w}", "workload": w, "key_design": k, "capacity_mode": m,
                             "configuration": f"{k}-{m}", "latency_mean_ms": lat, "latency_p95_ms": lat * 2,
                             "latency_p99_ms": lat * 3, "throughput_ops_s": 200.0,
                             "throttle_rate": 0.01 * (m == "provisioned") * (w == "W4") + rng.uniform(0, 0.001),
                             "attempted": 18000, "succeeded": 18000, "rcu": 4500.0 * (10 if k == "K3" else 1),
                             "wcu": 9000.0, "wall_s": 90.0, "cold_contaminated": r == 0 and w == "W1",
                             "data_source": source, "prov_rcu_avg": 140.0 if m == "provisioned" else np.nan,
                             "prov_wcu_avg": 200.0 if m == "provisioned" else np.nan})
    return pd.DataFrame(rows)


def test_placeholders_when_there_is_no_data(tmp_path):
    res = A.analyse(tmp_path / "none", tmp_path / "out", CFG)
    assert res["status"].startswith("no data")
    text = (tmp_path / "out/cell_summary.md").read_text()
    assert text.count(A.PLACEHOLDER) == 24 * len(A.SUMMARY_COLS) + 1  # every cell + the note on top


def test_full_analysis_on_a_small_table(tmp_path):
    (tmp_path / "res").mkdir()
    fake_batches().to_csv(tmp_path / "res/batches.csv", index=False)
    res = A.analyse(tmp_path / "res", tmp_path / "out", CFG)
    assert len(res["tests"]) == 12 and res["cold_contaminated_excluded"] == 6
    assert all(t["p_holm"] >= t["p_primary"] - 1e-12 for t in res["tests"].values())
    assert res["tests"]["H_key_W3"]["reject"]  # K3 was made 2 ms slower
    assert "NOT DynamoDB" in res["label"]
    for f in ["latency_by_configuration.png", "throttle_rate.png", "cost_per_10k.png", "tradeoff_surface.png"]:
        assert (tmp_path / "out" / f).stat().st_size > 5000
    h = json.loads((tmp_path / "out/hypotheses.json").read_text())
    assert h["data_source"] == "moto-smoke"
    cs = pd.read_csv(tmp_path / "out/cell_summary.csv")
    assert len(cs) == 24 and (cs["cost_per_10k"] > 0).all()


def test_mixed_sources_are_refused(tmp_path):
    (tmp_path / "res").mkdir()
    b = fake_batches()
    b.loc[:3, "data_source"] = "live"
    b.to_csv(tmp_path / "res/batches.csv", index=False)
    with pytest.raises(ValueError):
        A.analyse(tmp_path / "res", tmp_path / "out", CFG)


def test_pareto_front():
    cs = pd.DataFrame([{"workload": "W1", "configuration": "a", "latency_mean_ms": 1, "throttle_rate": 0, "cost_per_10k": 2},
                       {"workload": "W1", "configuration": "b", "latency_mean_ms": 2, "throttle_rate": 0, "cost_per_10k": 1},
                       {"workload": "W1", "configuration": "c", "latency_mean_ms": 3, "throttle_rate": 0.1, "cost_per_10k": 3}])
    front = A.pareto(cs).set_index("configuration")["on_front"]
    assert front["a"] and front["b"] and not front["c"]


def test_price_extraction_from_the_real_offer_excerpt():
    offer = json.load(open("tests/data/price_offer_eu_west_1_excerpt.json"))
    p = extract(offer)
    assert p == {"read_request_unit": 0.0000001415, "write_request_unit": 0.000000705,
                 "rcu_hour": 0.000147, "wcu_hour": 0.000735}
    text = render("eu-west-1", offer["publicationDate"], p)
    assert yaml.safe_load(text)["on_demand"]["write_request_unit"] == pytest.approx(0.000000705)
    assert yaml.safe_load(text) == yaml.safe_load(open("config/prices.yaml"))
