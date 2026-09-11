import shutil

import pytest

from logad.config import CONFIG_DIR, load_yaml
from logad.parse.drain_parser import FixedDrainParser, ParserChanged, check_or_write_fingerprint, fingerprint

REPORTS = [
    "REPORT RequestId: <RID>\tDuration: 12.34 ms\tBilled Duration: 13 ms\tMemory Size: 256 MB\tMax Memory Used: 80 MB",
    "REPORT RequestId: <RID>\tDuration: 99.10 ms\tBilled Duration: 100 ms\tMemory Size: 256 MB\tMax Memory Used: 91 MB",
]


def test_lines_that_differ_in_numbers_share_a_template():
    parsed = FixedDrainParser().parse(REPORTS)
    assert parsed.cluster_id[0] == parsed.cluster_id[1]
    assert "<FLOAT>" in parsed.template[1]


def test_different_messages_get_different_templates():
    parsed = FixedDrainParser().parse(REPORTS + ["RequestId: <RID> Error: Runtime exited with error: signal: killed"])
    assert parsed.cluster_id[2] != parsed.cluster_id[0]


def test_timestamps_are_masked():
    parsed = FixedDrainParser().parse(["<RID> Task timed out after 3.00 seconds at 2026-06-01T10:00:00.123Z"])
    assert "<TS>" in parsed.template[0]


def test_fingerprint_is_written_then_enforced(tmp_path):
    cfg_copy = tmp_path / "drain.yaml"
    shutil.copy(CONFIG_DIR / "drain.yaml", cfg_copy)
    fp_path = tmp_path / "fingerprint.json"
    first = check_or_write_fingerprint(fp_path, cfg_copy)
    assert fp_path.exists()
    assert check_or_write_fingerprint(fp_path, cfg_copy)["config_sha256"] == first["config_sha256"]
    cfg_copy.write_text(cfg_copy.read_text().replace("sim_th: 0.4", "sim_th: 0.5"))
    with pytest.raises(ParserChanged):
        check_or_write_fingerprint(fp_path, cfg_copy)


def test_version_is_pinned():
    fp = fingerprint()
    assert fp["parser_version_pinned"] == load_yaml(CONFIG_DIR / "drain.yaml")["parser_version"]
    assert fp["parser_version_installed"] == fp["parser_version_pinned"]
