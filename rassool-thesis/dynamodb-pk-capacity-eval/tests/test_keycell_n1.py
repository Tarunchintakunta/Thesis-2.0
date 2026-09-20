"""Key-cell n=1 analysis refuses confirmatory ANOVA."""
from pathlib import Path

import pandas as pd

from analysis.analyse_keycell_n1 import batch_factorial


def test_n1_not_identified():
    rows = []
    for k in ("K1", "K2", "K3"):
        for m in ("on_demand", "provisioned"):
            rows.append({"workload": "W3", "key_design": k, "capacity_mode": m,
                         "configuration": f"{k}-{m}", "latency_mean_ms": 5.0 + (1 if k == "K3" else 0)})
            rows.append({"workload": "W4", "key_design": k, "capacity_mode": m,
                         "configuration": f"{k}-{m}", "latency_mean_ms": 6.0})
    r = batch_factorial(pd.DataFrame(rows))
    assert r["W3"]["identified_two_way_with_interaction"] is False
    assert r["W3"]["n_per_config"] == 1
    assert r["W3"]["additive_ols_exploratory"]["confirmatory"] is False
