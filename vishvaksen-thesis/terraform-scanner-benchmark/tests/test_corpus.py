"""Corpus scale and label invariants."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_corpus import build_specs  # noqa: E402
from src.common import CATEGORIES  # noqa: E402


def test_formal_n():
    specs = build_specs()
    assert len(specs) == 240
    for cat in CATEGORIES:
        rows = [s for s in specs if s.category == cat]
        assert len(rows) == 60
        insecure = sum(1 for s in rows if s.label == "insecure")
        assert insecure == 36
        assert insecure / 60 == 0.6


def test_unique_ids():
    specs = build_specs()
    ids = [s.module_id for s in specs]
    assert len(ids) == len(set(ids))


def test_hcl_singleton_unwrap():
    from src.io_util import flatten_hcl_obj

    raw = {
        "resource": [
            {
                "aws_s3_bucket_acl": {
                    "this": {"acl": ["public-read"], "block_public_acls": [False]}
                }
            }
        ]
    }
    out = flatten_hcl_obj(raw)
    acl = out["resource"]["aws_s3_bucket_acl"]["this"]["acl"]
    assert acl == "public-read"
    assert out["resource"]["aws_s3_bucket_acl"]["this"]["block_public_acls"] is False


def test_no_student_ids_in_module_ids():
    specs = build_specs()
    banned = ("25173421", "x25173421", "vishvaksen")
    blob = " ".join(s.module_id for s in specs).lower()
    for token in banned:
        assert token not in blob


def test_sibling_secure_exists():
    specs = build_specs()
    by_id = {s.module_id: s for s in specs}
    for spec in specs:
        sib = by_id[spec.sibling_id]
        assert sib.label == "secure"
        assert sib.pattern_id == spec.pattern_id


def test_labels_csv_roundtrip(tmp_path):
    from scripts.generate_corpus import write_corpus

    write_corpus(tmp_path)
    with (tmp_path / "labels.csv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 240
    for row in rows:
        tf = tmp_path / row["rel_path"]
        assert tf.is_file()
        text = tf.read_text(encoding="utf-8")
        assert "do not terraform apply" in text.lower()
        assert "EVALUATION ONLY" in text
