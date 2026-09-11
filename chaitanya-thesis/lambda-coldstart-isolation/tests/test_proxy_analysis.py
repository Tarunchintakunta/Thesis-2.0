"""Proxy analysis on a small hand-made runs table (test input only, not a result)."""
import json

import numpy as np
import pandas as pd

from coldstart.proxy_analysis import analyse_proxy, proxy_label

BASE = {"python": 40, "nodejs": 50, "java": 120}


def fake_runs():
    rng = np.random.default_rng(0)
    rows = []
    for r, base in BASE.items():
        for v in ("default", "optimised"):
            extra = 300 if v == "default" else 0
            for rep in range(12):
                rows.append({"runtime": r, "variant": v, "ok": True, "warmup": False, "rep": rep,
                             "init_proxy_ms": (base + extra) * rng.lognormal(0, 0.1),
                             "handler_ms": 10.0, "process_wall_ms": base + extra + 20})
            rows.append({"runtime": r, "variant": v, "ok": True, "warmup": True, "rep": -1,
                         "init_proxy_ms": 9999.0, "handler_ms": 10.0, "process_wall_ms": 9999.0})
    rows.append({"runtime": "java", "variant": "default", "ok": False, "warmup": False, "rep": 0,
                 "init_proxy_ms": np.nan, "handler_ms": np.nan, "process_wall_ms": 5.0})
    return pd.DataFrame(rows)


INFO = {"machine": {"github_actions": True, "platform": "Linux"},
        "packages": [{"runtime": r, "variant": v, "zip_bytes": 2e7 if v == "default" else 800,
                      "unzipped_bytes": 5e7 if v == "default" else 900}
                     for r in BASE for v in ("default", "optimised")]}


def test_proxy_tests_and_outputs(tmp_path):
    res = analyse_proxy(fake_runs(), INFO, tmp_path / "fig", tmp_path / "tab")
    assert set(res["tests"]) == {"H1_proxy", "H2_proxy_python", "H2_proxy_nodejs", "H2_proxy_java"}
    assert all(t["family"] == "proxy" and t["p_holm"] >= t["p"] for t in res["tests"].values())
    assert res["tests"]["H2_proxy_java"]["median_diff"] > 200
    assert (tmp_path / "fig/init_proxy_by_variant.png").exists()
    assert (tmp_path / "fig/package_size_vs_init_proxy.png").exists()
    md = (tmp_path / "tab/proxy_summary.md").read_text()
    assert "NOT an AWS Lambda Init Duration" in md
    json.loads((tmp_path / "tab/proxy_tests.json").read_text())


def test_warmup_and_failed_rows_are_left_out(tmp_path):
    analyse_proxy(fake_runs(), INFO, tmp_path / "fig", tmp_path / "tab")
    s = pd.read_csv(tmp_path / "tab/proxy_summary.csv")
    assert (s["n"] == 12).all()
    assert s["init_proxy_p99_ms"].max() < 9999


def test_label_says_where_it_ran():
    assert "GitHub Actions" in proxy_label(INFO)
    assert "Darwin" in proxy_label({"machine": {"github_actions": False, "platform": "macOS-Darwin"}})
