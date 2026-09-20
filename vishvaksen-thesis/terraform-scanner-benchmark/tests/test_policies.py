"""OPA helpers compile; category packages are loadable."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
POLICIES = ROOT / "policies" / "rego"


def test_rego_files_present():
    names = {p.name for p in POLICIES.glob("*.rego")}
    assert names >= {
        "helpers.rego",
        "public_storage.rego",
        "overpermissive_access.rego",
        "encryption_at_rest.rego",
        "weak_logging.rego",
        "gate.rego",
    }


@pytest.mark.skipif(shutil.which("opa") is None and not (Path.home() / ".local/bin/opa").exists(), reason="opa missing")
def test_opa_check_policies():
    opa = shutil.which("opa") or str(Path.home() / ".local/bin/opa")
    proc = subprocess.run(
        [opa, "check", str(POLICIES)], capture_output=True, text=True
    )
    assert proc.returncode == 0, proc.stderr


@pytest.mark.skipif(shutil.which("opa") is None and not (Path.home() / ".local/bin/opa").exists(), reason="opa missing")
def test_opa_denies_literal_public_acl(tmp_path):
    opa = shutil.which("opa") or str(Path.home() / ".local/bin/opa")
    inp = {
        "resource": {
            "aws_s3_bucket_acl": {"this": {"acl": "public-read"}},
            "aws_s3_bucket_public_access_block": {
                "this": {
                    "block_public_acls": False,
                    "restrict_public_buckets": False,
                }
            },
        }
    }
    ip = tmp_path / "in.json"
    ip.write_text(json.dumps(inp), encoding="utf-8")
    proc = subprocess.run(
        [
            opa,
            "eval",
            "--format",
            "json",
            "-d",
            str(POLICIES),
            "-i",
            str(ip),
            "data.terraform.public_storage.deny",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    value = data["result"][0]["expressions"][0]["value"]
    assert value
