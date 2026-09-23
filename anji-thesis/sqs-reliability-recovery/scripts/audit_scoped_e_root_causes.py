#!/usr/bin/env python3
"""Scripted remediable audit for Anji scoped E_guidance + full-IV amendment — not manual chat.

Verifies scoped_E_guidance_1 is 20/20 E_guidance_transfer (VT×batch×n=5), Kyrychenko
framing, and that full CA2 IV live matrix is not fabricated. Intentional full-IV
amendment gets dated WONTFIX when remediable_total=0.

Usage (from sqs-reliability-recovery/):
  python3 scripts/audit_scoped_e_root_causes.py
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "results" / "live"
PACK = LIVE / "scoped_E_guidance_1"
EXPECTED_RUNS = 20
EXPECTED_CELLS = {(30, 10), (30, 50), (600, 10), (600, 50)}
REPS_PER_CELL = 5


def _f(x: object) -> float | None:
    if x is None:
        return None
    s = str(x).strip()
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _scan_fabricated(remediable: dict[str, int], findings: list[dict]) -> None:
    patterns = [
        (
            re.compile(
                r"full\s+IV\s+(live\s+)?(matrix|factorial).{0,40}(complete|done|met|100)",
                re.I | re.S,
            ),
            "fabricated_full_iv_live_complete",
        ),
        (
            re.compile(r"ALIGNMENT\s*=\s*100", re.I),
            "fabricated_alignment_100",
        ),
        (
            re.compile(
                r"live\s+Holm\s+H1.?H3.{0,30}(reject|significant|supported)",
                re.I | re.S,
            ),
            "fabricated_live_holm_win",
        ),
        (
            re.compile(
                r"scoped_E_guidance_1.{0,40}(incomplete|missing|(?<!\d)0/20(?!\d))",
                re.I | re.S,
            ),
            "scoped_e_marked_incomplete_while_present",
        ),
    ]
    scan = [
        ROOT / "STATUS.md",
        ROOT / "GENAI_HANDOFF.md",
        LIVE / "FINAL3_BASELINE.md",
        PACK / "SCOPED_E_BASELINE.md",
        ROOT.parent / "CA2_PROPOSED_VS_ARTEFACT.md",
        ROOT.parent / "DATED_WONTFIX_N_Anji_2026-09-23.md",
        ROOT / "DESIGN_RATIONALE_BEYOND_CA2.md",
    ]
    hits: dict[str, list[str]] = defaultdict(list)
    for path in scan:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for cre, kind in patterns:
            for m in cre.finditer(text):
                start = max(0, m.start() - 120)
                window = text[start : m.end() + 80].lower()
                if any(
                    tok in window
                    for tok in (
                        "not",
                        "never",
                        "amended",
                        "wontfix",
                        "beyond",
                        "fail",
                        "overstated",
                        "do not",
                        "don't",
                        "forbidden",
                        "not claim",
                        "not met",
                        "absent",
                        "not on live",
                        "honest",
                    )
                ):
                    continue
                hits[kind].append(str(path))
    for kind, paths in hits.items():
        remediable[kind] += len(set(paths))
        findings.append({"kind": kind, "remediable": True, "paths": sorted(set(paths))})
    if not hits:
        findings.append({"kind": "no_fabricated_win_claims", "remediable": False})


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="JSON report path (default: results/live/scoped_E_guidance_1/scoped_e_audit_report.json)",
    )
    args = ap.parse_args()
    out = args.out or (PACK / "scoped_e_audit_report.json")

    findings: list[dict] = []
    remediable: dict[str, int] = defaultdict(int)

    if not PACK.exists():
        remediable["missing_scoped_E_guidance_1"] += 1
        findings.append({"kind": "missing_scoped_E_guidance_1", "remediable": True})
        rows: list[dict] = []
    else:
        summary_csv = PACK / "summary.csv"
        summary_json = PACK / "summary.json"
        raw = PACK / "raw"
        manifests = PACK / "manifests"

        if not summary_csv.exists():
            remediable["missing_scoped_e_summary_csv"] += 1
            findings.append({"kind": "missing_scoped_e_summary_csv", "remediable": True})
            rows = []
        else:
            with summary_csv.open(encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))

        raw_dirs = [p for p in raw.iterdir()] if raw.exists() else []
        raw_dirs = [p for p in raw_dirs if p.is_dir()]
        man_files = list(manifests.glob("*.json")) if manifests.exists() else []

        if len(raw_dirs) != EXPECTED_RUNS:
            remediable["scoped_e_raw_count_mismatch"] += 1
            findings.append(
                {
                    "kind": "scoped_e_raw_count_mismatch",
                    "remediable": True,
                    "n": len(raw_dirs),
                    "expected": EXPECTED_RUNS,
                }
            )
        if len(rows) != EXPECTED_RUNS:
            remediable["scoped_e_summary_count_mismatch"] += 1
            findings.append(
                {
                    "kind": "scoped_e_summary_count_mismatch",
                    "remediable": True,
                    "n": len(rows),
                    "expected": EXPECTED_RUNS,
                }
            )
        if len(man_files) != EXPECTED_RUNS:
            remediable["scoped_e_manifest_count_mismatch"] += 1
            findings.append(
                {
                    "kind": "scoped_e_manifest_count_mismatch",
                    "remediable": True,
                    "n": len(man_files),
                    "expected": EXPECTED_RUNS,
                }
            )

        if rows:
            campaigns = {r.get("campaign") for r in rows}
            backends = {r.get("backend") for r in rows}
            if campaigns != {"E_guidance_transfer"}:
                remediable["scoped_e_campaign_mismatch"] += 1
                findings.append(
                    {
                        "kind": "scoped_e_campaign_mismatch",
                        "remediable": True,
                        "got": sorted(c for c in campaigns if c),
                    }
                )
            if backends != {"localsim"}:
                # Live would also be OK if present, but this pack is localsim
                if "live" in backends and "localsim" not in backends:
                    findings.append(
                        {
                            "kind": "scoped_e_live_backend",
                            "remediable": False,
                            "note": "unexpected live; verify destroy",
                        }
                    )
                else:
                    remediable["scoped_e_backend_mismatch"] += 1
                    findings.append(
                        {
                            "kind": "scoped_e_backend_mismatch",
                            "remediable": True,
                            "got": sorted(b for b in backends if b),
                        }
                    )

            cell_counts: Counter[tuple[int, int]] = Counter()
            bad_metric = 0
            for r in rows:
                vt = int(float(r["visibility_timeout"]))
                bs = int(float(r["batch_size"]))
                cell_counts[(vt, bs)] += 1
                for col in ("loss_rate", "duplicate_rate", "recovery_time_s", "throughput_msg_s"):
                    v = _f(r.get(col))
                    if v is None or not math.isfinite(v) or v < 0:
                        bad_metric += 1
            if set(cell_counts) != EXPECTED_CELLS:
                remediable["scoped_e_cell_set_mismatch"] += 1
                findings.append(
                    {
                        "kind": "scoped_e_cell_set_mismatch",
                        "remediable": True,
                        "got": sorted(cell_counts),
                        "expected": sorted(EXPECTED_CELLS),
                    }
                )
            if any(v != REPS_PER_CELL for v in cell_counts.values()):
                remediable["scoped_e_reps_mismatch"] += 1
                findings.append(
                    {
                        "kind": "scoped_e_reps_mismatch",
                        "remediable": True,
                        "counts": {f"vt{k[0]}_b{k[1]}": v for k, v in cell_counts.items()},
                    }
                )
            if bad_metric:
                remediable["scoped_e_invalid_metrics"] += 1
                findings.append(
                    {
                        "kind": "scoped_e_invalid_metrics",
                        "remediable": True,
                        "n_bad": bad_metric,
                    }
                )
            else:
                findings.append(
                    {
                        "kind": "scoped_e_20_of_20_ok",
                        "remediable": False,
                        "n": len(rows),
                        "cells": {f"vt{k[0]}_b{k[1]}": v for k, v in sorted(cell_counts.items())},
                    }
                )

        if summary_json.exists():
            sj = json.loads(summary_json.read_text(encoding="utf-8"))
            if "Kyrychenko" not in str(sj.get("baseline") or ""):
                remediable["missing_kyrychenko_baseline_framing"] += 1
                findings.append(
                    {"kind": "missing_kyrychenko_baseline_framing", "remediable": True}
                )
            else:
                findings.append({"kind": "kyrychenko_framing_ok", "remediable": False})
            if int(sj.get("n_runs") or 0) != EXPECTED_RUNS:
                remediable["summary_json_n_runs_mismatch"] += 1
                findings.append(
                    {
                        "kind": "summary_json_n_runs_mismatch",
                        "remediable": True,
                        "n_runs": sj.get("n_runs"),
                    }
                )
        else:
            remediable["missing_scoped_e_summary_json"] += 1
            findings.append({"kind": "missing_scoped_e_summary_json", "remediable": True})

    # Full IV live matrix must remain amended-out (no fake pack)
    fake_full_iv = list(LIVE.glob("*full_iv*")) + list(LIVE.glob("*full-iv*"))
    if fake_full_iv:
        remediable["fabricated_full_iv_live_artefact"] += len(fake_full_iv)
        findings.append(
            {
                "kind": "fabricated_full_iv_live_artefact",
                "remediable": True,
                "paths": [str(p.relative_to(ROOT)) for p in fake_full_iv],
            }
        )
    else:
        findings.append(
            {
                "kind": "full_iv_live_absent_as_amended",
                "remediable": False,
                "note": "full CA2 IV live matrix intentionally not claimed",
            }
        )

    # Supporting live lite packs should exist (smoke / key_cells / finals)
    for name in ("final_1", "final_2", "final_3", "key_cells_n3"):
        p = LIVE / name
        if p.exists():
            findings.append({"kind": f"support_pack_present_{name}", "remediable": False})
        else:
            # key_cells_n3 / finals missing is remediable for floor; scoped_E alone is soft limb close
            if name == "key_cells_n3":
                remediable["missing_key_cells_n3"] += 1
                findings.append({"kind": "missing_key_cells_n3", "remediable": True})
            else:
                findings.append(
                    {
                        "kind": f"support_pack_absent_{name}",
                        "remediable": False,
                        "note": "optional relative to scoped_E + amendment close",
                    }
                )

    _scan_fabricated(remediable, findings)

    # Same-metrics snapshot from rows
    cell_means: dict[str, dict] = {}
    for r in rows:
        key = f"VT{r.get('visibility_timeout')}_B{r.get('batch_size')}"
        cell_means.setdefault(
            key, {"loss_rate": [], "recovery_time_s": [], "throughput_msg_s": []}
        )
        for k in cell_means[key]:
            v = _f(r.get(k))
            if v is not None:
                cell_means[key][k].append(v)
    pooled = {
        c: {k: (sum(vs) / len(vs) if vs else None) for k, vs in metrics.items()}
        for c, metrics in cell_means.items()
    }

    remediable_total = int(sum(remediable.values()))
    disposition = (
        "FIX_REMEDIABLE"
        if remediable_total > 0
        else "DATED_WONTFIX_FULL_IV_LIVE_AMENDED"
    )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "thesis": "anji",
        "artefact": "sqs-reliability-recovery",
        "findings": findings,
        "remediable": dict(remediable),
        "remediable_total": remediable_total,
        "move_blocker": remediable_total > 0,
        "disposition": disposition,
        "n_anji_close": disposition.startswith("DATED_WONTFIX"),
        "soft_limbs": {
            "full_iv_live_matrix": "amended / beyond disclosed lite + scoped E",
            "scoped_E_guidance_1": "20/20 localsim E_guidance_transfer",
            "live_holm_h1_h3": "not claimed",
        },
        "same_metrics_snapshot": {
            "baseline": "Kyrychenko et al. (2025) — steady-state SQS optima; no fault injection",
            "retained_metrics": [
                "loss_rate",
                "duplicate_rate",
                "recovery_time_s",
                "throughput_msg_s",
            ],
            "gap_fill": ["fault injection", "DLQ capture", "guidance-under-fault"],
            "scoped_E_cell_means": pooled,
            "n_runs": len(rows),
        },
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = out.with_suffix(".md")
    lines = [
        "# Anji scoped_E / full-IV remediable audit (scripted)",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Move gate",
        "",
        f"- **remediable_total:** {remediable_total}",
        f"- **move_blocker:** {report['move_blocker']}",
        f"- **disposition:** `{disposition}`",
        "",
        "## Soft limbs (intentional when EXIT 0)",
        "",
        "- scoped_E_guidance_1: **20/20** E_guidance_transfer (localsim)",
        "- Full IV live matrix: **amended / dated WONTFIX**",
        "- Live Holm H1–H3: **not claimed**",
        "",
        "## Remediable bag",
        "",
        "```json",
        json.dumps(dict(remediable), indent=2),
        "```",
        "",
        "## Findings",
        "",
    ]
    for fnd in findings:
        lines.append(f"- `{fnd['kind']}` remediable={fnd.get('remediable')}")
    lines.extend(
        [
            "",
            "```bash",
            "cd anji-thesis/sqs-reliability-recovery",
            "python3 scripts/audit_scoped_e_root_causes.py",
            "# EXIT 0 required; remediable_total must be 0",
            "```",
            "",
        ]
    )
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "out": str(out),
                "remediable_total": remediable_total,
                "move_blocker": report["move_blocker"],
                "disposition": disposition,
                "remediable": dict(remediable),
            },
            indent=2,
        )
    )
    return 2 if remediable_total > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
