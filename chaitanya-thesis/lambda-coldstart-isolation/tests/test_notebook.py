"""The notebook's code cells must run against the committed mock data (no Jupyter needed)."""
import json
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks/analysis.ipynb"


@pytest.mark.skipif(not (ROOT / "data/processed/mock/costs.csv").exists(), reason="run make mock-all first")
def test_notebook_code_cells_run(monkeypatch):
    monkeypatch.chdir(ROOT / "notebooks")
    cells = [c for c in json.loads(NB.read_text())["cells"] if c["cell_type"] == "code"]
    ns: dict = {}
    for c in cells:
        exec(compile("".join(c["source"]), "notebook", "exec"), ns)  # noqa: S102
    assert ns["MODE"] == "mock" and len(ns["costs"]) > 1000
    assert os.getcwd().endswith("notebooks")
