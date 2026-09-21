"""Load corpus labels and flatten HCL for OPA."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
MAPPINGS = ROOT / "mappings"
POLICIES = ROOT / "policies" / "rego"
RESULTS = ROOT / "results"


def load_labels(path: Path | None = None) -> list[dict[str, str]]:
    labels_path = path or (CORPUS / "labels.csv")
    with labels_path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load_id_map(name: str) -> dict[str, set[str]]:
    raw = json.loads((MAPPINGS / name).read_text(encoding="utf-8"))
    return {k: set(v) for k, v in raw.items() if not k.startswith("_")}


def module_dir(row: dict[str, str]) -> Path:
    return CORPUS / row["category"] / row["module_id"]


_META_KEYS = {"__start_line__", "__end_line__", "__is_block__"}


def _strip_quotes(value: Any) -> Any:
    """python-hcl2 ≥7 may leave JSON-style quotes on identifiers/literals."""
    if isinstance(value, str) and len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return value


def flatten_hcl_obj(node: Any) -> Any:
    """Collapse python-hcl2 list-of-dicts into nested dicts keyed by name.

    python-hcl2 wraps scalar attributes as one-element lists (acl = ["public-read"]).
    Those singletons are unwrapped so Rego can compare the HCL value directly.
    Newer python-hcl2 releases may also quote block type/name keys; those quotes
    are stripped so Rego can address input.resource.aws_s3_bucket_acl.this.
    """
    if isinstance(node, list):
        if node and all(isinstance(x, dict) for x in node):
            merged: dict[str, Any] = {}
            for item in node:
                for key, val in item.items():
                    if key in _META_KEYS:
                        continue
                    norm_key = _strip_quotes(key)
                    merged[norm_key] = _merge(
                        merged.get(norm_key), flatten_hcl_obj(val)
                    )
            return merged
        unwrapped = [flatten_hcl_obj(x) for x in node]
        if len(unwrapped) == 1 and not isinstance(unwrapped[0], (dict, list)):
            return unwrapped[0]
        return unwrapped
    if isinstance(node, dict):
        return {
            _strip_quotes(k): flatten_hcl_obj(v)
            for k, v in node.items()
            if k not in _META_KEYS
        }
    return _strip_quotes(node)


def _merge(left: Any, right: Any) -> Any:
    if left is None:
        return right
    if isinstance(left, dict) and isinstance(right, dict):
        out = dict(left)
        for k, v in right.items():
            out[k] = _merge(out.get(k), v)
        return out
    if isinstance(left, list) and isinstance(right, list):
        return left + right
    return right


def parse_tf_file(path: Path) -> dict[str, Any]:
    import hcl2

    with path.open(encoding="utf-8") as fh:
        raw = hcl2.load(fh)
    return flatten_hcl_obj(raw)


def opa_input_for_module(row: dict[str, str]) -> dict[str, Any]:
    tf_path = CORPUS / row["rel_path"]
    parsed = parse_tf_file(tf_path)
    parsed["_module_id"] = row["module_id"]
    parsed["_category"] = row["category"]
    parsed["_source"] = str(tf_path)
    return parsed
