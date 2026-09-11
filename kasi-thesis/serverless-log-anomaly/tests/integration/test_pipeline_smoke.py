"""Whole pipeline on the smoke config (seconds). Needs the Loghub BGL sample."""
import json

import pandas as pd
import pytest

from logad import pipeline
from logad.config import CONFIG_DIR
from logad.eval import report
from logad.source.loghub_bgl import BGL_PATH

pytestmark = pytest.mark.skipif(not BGL_PATH.exists(), reason="run scripts/fetch_loghub.sh first")


@pytest.fixture(scope="module")
def smoke(tmp_path_factory):
    root = tmp_path_factory.mktemp("smoke")
    out = root / "results"
    rc = pipeline.main(["--config", str(CONFIG_DIR / "smoke.yaml"), "--out", str(out),
                        "--raw", str(root / "raw"), "--interim", str(root / "interim")])
    assert rc == 0
    assert report.main(["--results", str(out)]) == 0
    return root, out


def test_window_predictions_for_every_detector(smoke):
    _, out = smoke
    B = pd.read_csv(out / "metrics" / "windows_B_seed_7.csv")
    for det in ("d1_ocsvm", "d1_iforest", "d1_primary", "d2_transfer", "d3_thresholds"):
        assert f"pred_{det}" in B and f"score_{det}" in B
    assert B["label"].sum() > 0
    C = pd.read_csv(out / "metrics" / "windows_C_seed_7.csv")
    assert not C["label"].any()


def test_training_window_certified_and_parser_fingerprinted(smoke):
    _, out = smoke
    cert = json.loads((out / "certification" / "seed_7.json").read_text())
    assert cert["certified"] and cert["injections_overlapping_A"] == []
    assert all(v == 0 for v in cert["fault_signature_lines"].values())
    fp = json.loads((out / "parser_fingerprint.json").read_text())
    assert fp["parser"] == "drain3" and len(fp["config_sha256"]) == 64


def test_identifiers_are_gone_from_interim(smoke):
    root, _ = smoke
    text = (root / "interim" / "smoke" / "seed_7" / "phase_A.log").read_text()
    assert "<RID>" in text
    assert "123456789012" not in text


def test_report_outputs(smoke):
    _, out = smoke
    h = json.loads((out / "stats" / "hypotheses.json").read_text())
    assert set(h["tests"]) == {"H1", "H2_d1_primary", "H2_d2_transfer", "H2_d3_thresholds", "H3"}
    assert "viable_substitute" in h["decision_rule"]
    for name in ("f1_by_detector.png", "f1_by_category.png", "pr_curves.png", "elasticity_far.png",
                 "detection_delay.png", "timeline_phase_B.png"):
        assert (out / "figures" / name).exists()
    run = json.loads((out / "run_info.json").read_text())
    assert run["runs"][0]["d1"]["primary"] == "d1_ocsvm"


def test_changed_parser_config_is_refused(smoke, tmp_path):
    _, out = smoke
    fp = json.loads((out / "parser_fingerprint.json").read_text())
    fp["config_sha256"] = "0" * 64
    bad = tmp_path / "fp.json"
    bad.write_text(json.dumps(fp))
    from logad.parse.drain_parser import ParserChanged, check_or_write_fingerprint

    with pytest.raises(ParserChanged):
        check_or_write_fingerprint(bad)
