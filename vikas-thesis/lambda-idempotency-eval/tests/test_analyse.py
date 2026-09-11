"""The whole analysis on a small moto run - checks the plumbing, not AWS behaviour."""
import pandas as pd

from analysis import analyse
from analysis.tables import SIGN
from tests.conftest import moto_run


def test_analysis_end_to_end_on_moto(ddb, tmp_path):
    # 8 per cell: with fewer, 9 Holm-corrected capacity tests cannot reach alpha even for constant cells
    moto_run(ddb, tmp_path / "campaign", "campaign", 8)
    moto_run(ddb, tmp_path / "sensitivity", "sensitivity", 3)
    out, fig = tmp_path / "out", tmp_path / "fig"
    analyse.analyse(tmp_path / "campaign", out, fig, sensitivity=tmp_path / "sensitivity", B=200)
    for f in ("requests", "cells", "dup_tests", "chi2", "capacity_tests", "latency_tests", "expectations", "checks",
              "sensitivity_cells", "sensitivity_outcomes"):
        assert (out / f"{f}.csv").exists(), f
    for f in ("dup_rate", "latency", "capacity", "surface"):
        assert (fig / f"{f}.png").stat().st_size > 5000, f
    summary = (out / "summary.md").read_text()
    assert "NOT an AWS measurement" in summary
    assert summary.rstrip().splitlines()[-1] == SIGN

    e = pd.read_csv(out / "expectations.csv")
    assert set(e["expectation"]) == {"E1", "E2", "E3"}
    assert e.query("expectation == 'E1' and multiplicity == 5")["decision"].iloc[0] == "supported"
    assert (e.query("expectation == 'E3'")["decision"] == "supported").all()  # 3 writes vs 1 per first delivery
    d = pd.read_csv(out / "dup_tests.csv")
    assert len(d) == 6 and d["p_holm"].ge(d["p"]).all()
    assert (pd.read_csv(out / "sensitivity_cells.csv")["dup_rate"] == 1.0).all()
    chk = pd.read_csv(out / "checks.csv").set_index("check")["value"]
    assert chk["missing deliveries"] == "0" or chk["missing deliveries"] == 0
