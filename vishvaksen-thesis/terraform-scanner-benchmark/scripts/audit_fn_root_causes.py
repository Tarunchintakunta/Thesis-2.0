#!/usr/bin/env python3
"""Scripted remediable audit for Vishvaksen Checkov FN mapping undercount — not manual.

Verifies:
  - Checkov ALL recall ≈ 0.917 after catalog-ID mapping fix (not stuck ~0.56)
  - hard_verify_6+ packs present with matching Checkov recall
  - remediable mapping undercount closed (R floor met); residual FN = evidenced negative
  - Verdet baseline paper + SoT present
  - no marketing ALIGNMENT=100 as scanner-complete

EXIT 2 if remediable_total > 0 (move_blocker). EXIT 0 when clean.

Usage (from terraform-scanner-benchmark/):
  python3 scripts/audit_fn_root_causes.py
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THESIS = ROOT.parent
RESULTS = ROOT / "results"
CHECKOV_R_TARGET = 0.917
CHECKOV_R_TOL = 0.02  # accept ~0.90–0.94 band around 0.917
CHECKOV_R_FLOOR = 0.90


def _checkov_all(metrics_csv: Path) -> dict | None:
    if not metrics_csv.exists():
        return None
    with metrics_csv.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("stage") == "checkov" and row.get("category") == "ALL":
                return {
                    "tp": int(float(row["tp"])),
                    "fn": int(float(row["fn"])),
                    "fp": int(float(row.get("fp") or 0)),
                    "precision": float(row["precision"]),
                    "recall": float(row["recall"]),
                    "f1": float(row["f1"]),
                }
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", type=Path, default=RESULTS)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    results = args.results
    out = args.out or (results / "analysis" / "fn_root_causes_audit_report.json")

    findings: list[dict] = []
    remediable: dict[str, int] = defaultdict(int)

    metrics = _checkov_all(results / "metrics_per_category.csv")
    if metrics is None:
        remediable["missing_metrics_per_category"] += 1
        findings.append({"kind": "missing_metrics_per_category", "remediable": True})
    else:
        r = metrics["recall"]
        if r < CHECKOV_R_FLOOR or abs(r - CHECKOV_R_TARGET) > CHECKOV_R_TOL:
            remediable["checkov_recall_mapping_undercount"] += 1
            findings.append(
                {
                    "kind": "checkov_recall_mapping_undercount",
                    "remediable": True,
                    "recall": r,
                    "expected_approx": CHECKOV_R_TARGET,
                    "hint": "Extend mappings/checkov_ids.json for fired-but-unmatched catalog IDs; re-score from raw/checkov_batch.json",
                }
            )
        else:
            findings.append(
                {
                    "kind": "checkov_recall_ok",
                    "remediable": False,
                    "recall": r,
                    "tp": metrics["tp"],
                    "fn": metrics["fn"],
                }
            )

    # mapping file must exist and note extension / include known fix IDs
    map_path = ROOT / "mappings" / "checkov_ids.json"
    if not map_path.exists():
        remediable["missing_checkov_map"] += 1
        findings.append({"kind": "missing_checkov_map", "remediable": True})
    else:
        raw = json.loads(map_path.read_text(encoding="utf-8"))
        # spot-check a few IDs from the 2026-09-23 classify set
        need = {
            "public_storage": "CKV_AWS_321",
            "weak_logging": "CKV_AWS_118",
            "encryption_at_rest": "CKV_AWS_94",
            "overpermissive_access": "CKV_AWS_230",
        }
        missing = [
            f"{cat}:{cid}"
            for cat, cid in need.items()
            if cid not in set(raw.get(cat) or [])
        ]
        if missing:
            remediable["mapping_fix_ids_absent"] += 1
            findings.append(
                {
                    "kind": "mapping_fix_ids_absent",
                    "remediable": True,
                    "missing": missing,
                }
            )
        else:
            findings.append({"kind": "mapping_fix_ids_ok", "remediable": False})

    # hard_verify_6+
    hv_packs = sorted(
        [
            p
            for p in results.iterdir()
            if p.is_dir() and re.fullmatch(r"hard_verify_([6-9]|\d{2,})", p.name)
        ],
        key=lambda p: p.name,
    )
    if not hv_packs:
        remediable["missing_hard_verify_6_plus"] += 1
        findings.append({"kind": "missing_hard_verify_6_plus", "remediable": True})
    else:
        hv_ok = 0
        for pack in hv_packs:
            summary_path = pack / "hard_verify_summary.json"
            m = _checkov_all(pack / "metrics_per_category.csv")
            summary = (
                json.loads(summary_path.read_text(encoding="utf-8"))
                if summary_path.exists()
                else None
            )
            recall = None
            if summary and summary.get("checkov_ALL"):
                recall = float(summary["checkov_ALL"]["recall"])
            elif m:
                recall = m["recall"]
            if recall is None:
                remediable["hv_missing_checkov_metrics"] += 1
                findings.append(
                    {
                        "kind": "hv_missing_checkov_metrics",
                        "remediable": True,
                        "pack": pack.name,
                    }
                )
                continue
            if recall < CHECKOV_R_FLOOR or abs(recall - CHECKOV_R_TARGET) > CHECKOV_R_TOL:
                remediable["hv_checkov_recall_fail"] += 1
                findings.append(
                    {
                        "kind": "hv_checkov_recall_fail",
                        "remediable": True,
                        "pack": pack.name,
                        "recall": recall,
                    }
                )
            else:
                hv_ok += 1
                findings.append(
                    {
                        "kind": "hv_checkov_ok",
                        "remediable": False,
                        "pack": pack.name,
                        "recall": recall,
                    }
                )
        if hv_ok < 1:
            remediable["hard_verify_6_plus_none_ok"] += 1

    # Verdet baseline
    baseline = THESIS / "baseline_papers" / "BASELINE_PAPER.md"
    verdet_doc = ROOT / "docs" / "VERDET_COMPARISON.md"
    if not baseline.exists() or "Verdet" not in baseline.read_text(encoding="utf-8"):
        remediable["baseline_not_verdet"] += 1
        findings.append({"kind": "baseline_not_verdet", "remediable": True})
    else:
        findings.append({"kind": "baseline_verdet_ok", "remediable": False})
    if not verdet_doc.exists():
        remediable["missing_verdet_comparison"] += 1
        findings.append({"kind": "missing_verdet_comparison", "remediable": True})
    else:
        findings.append({"kind": "verdet_comparison_ok", "remediable": False})

    # SoT
    sot = THESIS / "CA2_PROPOSED_VS_ARTEFACT.md"
    if not sot.exists():
        remediable["missing_sot"] += 1
        findings.append({"kind": "missing_sot", "remediable": True})
    else:
        st = sot.read_text(encoding="utf-8")
        need = ["Verdet", "Checkov", "recall", "Precision"]
        missing = [k for k in need if k not in st]
        if missing:
            remediable["sot_incomplete"] += 1
            findings.append(
                {"kind": "sot_incomplete", "remediable": True, "missing": missing}
            )
        else:
            findings.append({"kind": "sot_ok", "remediable": False})

    # config
    config_candidates = [
        THESIS / "CONFIGURATION_MANUAL.md",
        ROOT / "docs" / "CONFIGURATION_MANUAL.md",
        ROOT / "CONFIGURATION_MANUAL.md",
    ]
    if not any(p.exists() for p in config_candidates):
        remediable["missing_configuration_manual"] += 1
        findings.append({"kind": "missing_configuration_manual", "remediable": True})
    else:
        findings.append({"kind": "configuration_manual_ok", "remediable": False})

    # residual FN honesty: after R≈0.917, remaining FN are evidenced negative (not remediable)
    verd_path = results / "checkov_verdicts.json"
    residual_fn_with_findings = 0
    if verd_path.exists() and metrics is not None and metrics["recall"] >= CHECKOV_R_FLOOR:
        verd = json.loads(verd_path.read_text(encoding="utf-8"))
        for v in verd.get("verdicts") or []:
            if v.get("label") == "insecure" and not v.get("predicted") and int(v.get("n_all_findings") or 0) > 0:
                residual_fn_with_findings += 1
        findings.append(
            {
                "kind": "evidenced_residual_fn",
                "remediable": False,
                "n_fn_with_unmapped_findings": residual_fn_with_findings,
                "note": "Post-fix residual FN is soft negative (N-Vish), not mapping undercount",
            }
        )

    # ban marketing complete scans
    for stamp in (
        THESIS / "STATUS.md",
        ROOT / "STATUS.md",
        results / "FINAL3_BASELINE.md",
    ):
        if not stamp.exists():
            continue
        t = stamp.read_text(encoding="utf-8")
        if re.search(r"(?i)Checkov.*100%|zero FN|no false negatives", t):
            remediable["status_claims_perfect_checkov"] += 1
            findings.append(
                {
                    "kind": "status_claims_perfect_checkov",
                    "remediable": True,
                    "path": str(stamp),
                }
            )

    remediable_total = int(sum(remediable.values()))
    disposition = (
        "FIX_REMEDIABLE"
        if remediable_total > 0
        else "DATED_WONTFIX_RESIDUAL_CHECKOV_FN"
    )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "thesis": "vishvaksen",
        "artefact": "terraform-scanner-benchmark",
        "findings": findings,
        "remediable": dict(remediable),
        "remediable_total": remediable_total,
        "move_blocker": remediable_total > 0,
        "disposition": disposition,
        "checkov_all": metrics,
        "hard_verify_6_plus": [p.name for p in hv_packs],
        "n_vish_close": disposition.startswith("DATED_WONTFIX"),
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = out.with_suffix(".md")
    lines = [
        "# Vishvaksen FN / mapping remediable audit",
        "",
        f"- generated_at: `{report['generated_at']}`",
        f"- remediable_total: **{remediable_total}**",
        f"- move_blocker: `{report['move_blocker']}`",
        f"- disposition: `{disposition}`",
        f"- Checkov ALL recall: **{(metrics or {}).get('recall')}** (target ≈ {CHECKOV_R_TARGET})",
        f"- hard_verify_6+: `{', '.join(p.name for p in hv_packs) or 'NONE'}`",
        "",
        "## Remediable counts",
        "",
    ]
    if remediable:
        for k, v in sorted(remediable.items()):
            lines.append(f"- `{k}`: {v}")
    else:
        lines.append("- (none)")
    lines += ["", f"JSON: `{out}`", ""]
    md.write_text("\n".join(lines), encoding="utf-8")

    print(
        json.dumps(
            {
                "remediable_total": remediable_total,
                "disposition": disposition,
                "checkov_recall": (metrics or {}).get("recall"),
                "out": str(out),
            },
            indent=2,
        )
    )
    return 2 if remediable_total > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
