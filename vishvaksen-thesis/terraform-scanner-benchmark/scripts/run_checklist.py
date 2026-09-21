#!/usr/bin/env python3
"""Apply the label-oracle checklist as a deterministic procedure.

Implements checklist items in docs/MANUAL_CHECKLIST.md against HCL
text/literals and scores predictions against labels.csv.
Variable-indirection defects are expected false negatives for this stage.
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.io_util import CORPUS, RESULTS, load_labels  # noqa: E402

# Literal patterns for the label-oracle checklist.
# Variable references (var.*) are intentionally not treated as defects.
CHECKS = {
    "public_storage": [
        r'acl\s*=\s*"(public-read|public-read-write|authenticated-read)"',
        r"block_public_acls\s*=\s*false",
        r"restrict_public_buckets\s*=\s*false",
        r"publicly_accessible\s*=\s*true",
        r"associate_public_ip_address\s*=\s*true",
        r'group\s*=\s*"all"',
        r'Principal\s*=\s*"\*"',
        r'AWS\s*=\s*"\*"',
        r'"Principal"\s*:\s*"\*"',
    ],
    "overpermissive_access": [
        r'"0\.0\.0\.0/0"',
        r'"::/0"',
        r'Action\s*=\s*"\*"',
        r'Resource\s*=\s*"\*"',
        r"AdministratorAccess",
        r"IAMFullAccess",
        r'principal\s*=\s*"\*"',
        r'"s3:\*"',
    ],
    "encryption_at_rest": [
        r"encrypted\s*=\s*false",
        r"storage_encrypted\s*=\s*false",
        r"sqs_managed_sse_enabled\s*=\s*false",
        r"at_rest_encryption_enabled\s*=\s*false",
        r'encryption_type\s*=\s*"NONE"',
        r'catalog_encryption_mode\s*=\s*"DISABLED"',
        r"kms_master_key_id\s*=\s*null",
        r"kms_key_id\s*=\s*null",
        r"server_side_encryption\s*\{[^}]*enabled\s*=\s*false",
    ],
    "weak_logging": [
        r"enable_log_file_validation\s*=\s*false",
        r"access_logs\s*\{[^}]*enabled\s*=\s*false",
        r"enabled_cloudwatch_logs_exports\s*=\s*\[\]",
        r"enabled_cluster_log_types\s*=\s*\[\]",
        r"enable\s*=\s*false",
        r"xray_tracing_enabled\s*=\s*false",
        r"enabled\s*=\s*false",
    ],
}

ABSENCE_CHECKS = {
    "weak_logging": [
        ("aws_s3_bucket", "aws_s3_bucket_logging"),
        ("aws_vpc", "aws_flow_log"),
        ("aws_wafv2_web_acl", "aws_wafv2_web_acl_logging_configuration"),
        ("aws_api_gateway_stage", "aws_api_gateway_method_settings"),
    ],
    "encryption_at_rest": [
        ("aws_s3_bucket", "aws_s3_bucket_server_side_encryption_configuration"),
    ],
}


def apply_checklist(text: str, category: str) -> list[str]:
    hits = []
    for pat in CHECKS.get(category, []):
        if re.search(pat, text, flags=re.MULTILINE | re.DOTALL):
            hits.append(pat)
    for present, missing in ABSENCE_CHECKS.get(category, []):
        if f'resource "{present}"' in text and f'resource "{missing}"' not in text:
            # Avoid tagging CloudTrail-present modules as missing S3 logging
            # when the labelled pattern is trail presence; still a logging gap
            # if the category is weak_logging and the present resource exists.
            if present == "aws_s3_bucket" and 'resource "aws_cloudtrail"' in text:
                continue
            if present == "aws_s3_bucket" and 'resource "aws_lb"' in text:
                continue
            if present == "aws_s3_bucket" and 'resource "aws_elb"' in text:
                continue
            hits.append(f"missing:{missing}")
    return hits


def main() -> int:
    rows = load_labels()
    verdicts = []
    for r in rows:
        path = CORPUS / r["rel_path"]
        text = path.read_text(encoding="utf-8")
        t0 = time.perf_counter()
        hits = apply_checklist(text, r["category"])
        elapsed = time.perf_counter() - t0
        verdicts.append(
            {
                "module_id": r["module_id"],
                "category": r["category"],
                "label": r["label"],
                "predicted": 1 if hits else 0,
                "seconds": elapsed,
                "hits": hits[:12],
            }
        )
    payload = {
        "tool": "label_oracle_checklist",
        "version": "checklist-v1",
        "n_modules": len(rows),
        "batch_seconds": sum(v["seconds"] for v in verdicts),
        "verdicts": verdicts,
        "sample_times": [
            {
                "module_id": v["module_id"],
                "category": v["category"],
                "label": v["label"],
                "seconds": v["seconds"],
            }
            for v in verdicts
        ],
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "checklist_verdicts.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"checklist scripted {payload['batch_seconds']:.3f}s "
        f"flagged {sum(v['predicted'] for v in verdicts)}/{len(verdicts)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
