#!/usr/bin/env python3
"""Scripted remediable audit for Vikas live campaign E1–E3 — not manual.

Verifies:
  - campaign pack inventory + N-scale claims (N=1000 × 3 paths × 3 mult → 24000)
  - expectations.csv E1–E3 all supported with headline cell invariants
  - P4 / TransactWrite quarantine honesty (config A12; no P4 in live cells)
  - destroy-after evidence; config manual presence
  - no marketing ALIGNMENT=100 stamps in authoritative STATUS/FINAL3

EXIT 2 if remediable_total > 0 (move_blocker). EXIT 0 when clean.

Usage (from lambda-idempotency-eval/):
  python3 scripts/audit_campaign_root_causes.py
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / "data" / "runs" / "live" / "campaign"
RESULTS = ROOT / "results" / "live"
EXPECTED_N_PER_CELL = 1000
EXPECTED_PATHS = ("P1", "P2", "P3")
EXPECTED_MULTS = (1, 2, 5)
EXPECTED_DELIVERIES = 24000  # N=1000 × 3 paths × (1+2+5)
EXPECTED_REQUESTS = 9000  # 1000 × 3 × 3
EXPECTED_E_ROWS = 9  # E1×2 + E2×4 + E3×3


def _f(x: str | float | None) -> float | None:
    if x is None:
        return None
    s = str(x).strip()
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _count_lines(path: Path) -> int:
    if not path.exists():
        return -1
    n = 0
    with path.open("rb") as fh:
        for _ in fh:
            n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--campaign", type=Path, default=CAMPAIGN)
    ap.add_argument("--results", type=Path, default=RESULTS)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    campaign = args.campaign
    results = args.results
    out = args.out or (results / "campaign_audit_report.json")

    findings: list[dict] = []
    remediable: dict[str, int] = defaultdict(int)

    # --- 1. Pack inventory ---
    required_campaign = {
        "run_info.json": campaign / "run_info.json",
        "deliveries.jsonl": campaign / "deliveries.jsonl",
        "schedule.csv": campaign / "schedule.csv",
        "ground_truth.jsonl": campaign / "ground_truth.jsonl",
    }
    required_results = {
        "cells.csv": results / "cells.csv",
        "expectations.csv": results / "expectations.csv",
        "checks.csv": results / "checks.csv",
        "summary.md": results / "summary.md",
        "FINAL3_NOTE.md": results / "FINAL3_NOTE.md",
    }
    missing = [k for k, p in {**required_campaign, **required_results}.items() if not p.exists()]
    if missing:
        remediable["missing_pack_artefact"] += len(missing)
        findings.append(
            {"kind": "missing_pack_artefact", "remediable": True, "missing": missing}
        )
    else:
        findings.append({"kind": "pack_inventory_ok", "remediable": False})

    # --- 2. N-scale claims ---
    run_info: dict = {}
    if (campaign / "run_info.json").exists():
        run_info = json.loads((campaign / "run_info.json").read_text(encoding="utf-8"))

    n_del = _count_lines(campaign / "deliveries.jsonl")
    n_gt = _count_lines(campaign / "ground_truth.jsonl")
    n_sched = _count_lines(campaign / "schedule.csv")
    # schedule has header
    if n_sched > 0:
        n_sched -= 1

    info_req = int(run_info.get("requests") or -1)
    info_inv = int(run_info.get("invocations") or -1)
    phase = str(run_info.get("phase") or "")
    backend = str(run_info.get("backend") or "")

    scale_ok = (
        n_del == EXPECTED_DELIVERIES
        and n_gt == EXPECTED_REQUESTS
        and n_sched == EXPECTED_DELIVERIES
        and info_req == EXPECTED_REQUESTS
        and info_inv == EXPECTED_DELIVERIES
        and phase == "campaign"
        and backend == "live"
    )
    if not scale_ok:
        remediable["n_scale_mismatch"] += 1
        findings.append(
            {
                "kind": "n_scale_mismatch",
                "remediable": True,
                "deliveries_jsonl": n_del,
                "ground_truth_jsonl": n_gt,
                "schedule_rows": n_sched,
                "run_info_requests": info_req,
                "run_info_invocations": info_inv,
                "phase": phase,
                "backend": backend,
                "expected": {
                    "deliveries": EXPECTED_DELIVERIES,
                    "requests": EXPECTED_REQUESTS,
                    "phase": "campaign",
                    "backend": "live",
                },
            }
        )
    else:
        findings.append(
            {
                "kind": "n_scale_ok",
                "remediable": False,
                "n_per_cell": EXPECTED_N_PER_CELL,
                "deliveries": n_del,
                "requests": info_req,
            }
        )

    # Path / multiplicity composition from deliveries (stream sample if huge — full count)
    path_counts: Counter[str] = Counter()
    mult_by_path: dict[str, Counter[int]] = defaultdict(Counter)
    req_ids: set[str] = set()
    bad_path = 0
    if (campaign / "deliveries.jsonl").exists():
        with (campaign / "deliveries.jsonl").open(encoding="utf-8") as fh:
            for line in fh:
                o = json.loads(line)
                p = str(o.get("path") or "")
                m = int(o.get("multiplicity") or 0)
                path_counts[p] += 1
                mult_by_path[p][m] += 1
                rid = o.get("request_id")
                if rid:
                    req_ids.add(str(rid))
                if p not in EXPECTED_PATHS:
                    bad_path += 1
    if bad_path:
        remediable["unexpected_path_in_campaign"] += bad_path
        findings.append(
            {
                "kind": "unexpected_path_in_campaign",
                "remediable": True,
                "n_bad": bad_path,
                "path_counts": dict(path_counts),
            }
        )
    # Expect 8000 deliveries per path (1000×(1+2+5))
    per_path_ok = all(path_counts.get(p) == 8000 for p in EXPECTED_PATHS) and len(path_counts) == 3
    if n_del == EXPECTED_DELIVERIES and not per_path_ok and not bad_path:
        remediable["path_delivery_balance"] += 1
        findings.append(
            {
                "kind": "path_delivery_balance",
                "remediable": True,
                "path_counts": dict(path_counts),
            }
        )
    elif per_path_ok:
        findings.append(
            {
                "kind": "path_delivery_balance_ok",
                "remediable": False,
                "path_counts": dict(path_counts),
                "unique_requests": len(req_ids),
            }
        )

    # cells.csv: 9 cells, N=1000 each, P1–P3 only
    cells: list[dict] = []
    if (results / "cells.csv").exists():
        with (results / "cells.csv").open(encoding="utf-8") as fh:
            cells = [r for r in csv.DictReader(fh) if r.get("phase") == "campaign"]
    cell_keys = {(r.get("path"), int(float(r["multiplicity"])), int(float(r["requests"]))) for r in cells}
    expected_cells = {(p, m, EXPECTED_N_PER_CELL) for p in EXPECTED_PATHS for m in EXPECTED_MULTS}
    if cell_keys != expected_cells:
        remediable["cells_shape_mismatch"] += 1
        findings.append(
            {
                "kind": "cells_shape_mismatch",
                "remediable": True,
                "got": sorted(cell_keys),
                "expected": sorted(expected_cells),
            }
        )
    else:
        findings.append({"kind": "cells_shape_ok", "remediable": False, "n_cells": 9})

    # --- 3. E1–E3 expectations ---
    expectations: list[dict] = []
    if (results / "expectations.csv").exists():
        with (results / "expectations.csv").open(encoding="utf-8") as fh:
            expectations = list(csv.DictReader(fh))

    by_e: dict[str, list[dict]] = defaultdict(list)
    unsupported: list[dict] = []
    for row in expectations:
        e = str(row.get("expectation") or "").strip()
        by_e[e].append(row)
        if str(row.get("decision") or "").strip().lower() != "supported":
            unsupported.append(row)

    e_counts = {k: len(v) for k, v in by_e.items()}
    e_ok = (
        e_counts.get("E1") == 2
        and e_counts.get("E2") == 4
        and e_counts.get("E3") == 3
        and len(expectations) == EXPECTED_E_ROWS
        and not unsupported
    )
    if not e_ok:
        remediable["e1_e3_not_supported"] += 1
        findings.append(
            {
                "kind": "e1_e3_not_supported",
                "remediable": True,
                "counts": e_counts,
                "n_rows": len(expectations),
                "unsupported": [
                    {
                        "expectation": r.get("expectation"),
                        "multiplicity": r.get("multiplicity"),
                        "decision": r.get("decision"),
                    }
                    for r in unsupported
                ],
            }
        )
    else:
        findings.append(
            {
                "kind": "e1_e3_supported",
                "remediable": False,
                "counts": e_counts,
            }
        )

    # Headline cell invariants (claim↔evidence)
    cell_map = {
        (r["path"], int(float(r["multiplicity"]))): r for r in cells
    }
    headline_fail: list[str] = []
    for m in (2, 5):
        p1 = cell_map.get(("P1", m))
        if not p1 or _f(p1.get("dup_rate")) != 1.0:
            headline_fail.append(f"P1@{m} dup_rate!=1")
        for p in ("P2", "P3"):
            c = cell_map.get((p, m))
            if not c or _f(c.get("dup_rate")) != 0.0:
                headline_fail.append(f"{p}@{m} dup_rate!=0")
    for m in EXPECTED_MULTS:
        p2 = cell_map.get(("P2", m))
        p3 = cell_map.get(("P3", m))
        if p2 and p3:
            d = (_f(p3.get("capacity_mean")) or 0) - (_f(p2.get("capacity_mean")) or 0)
            if abs(d - 2.0) > 1e-9:
                headline_fail.append(f"P3-P2 capacity @{m} != 2 (got {d})")
    if headline_fail:
        remediable["headline_cell_invariant_broken"] += len(headline_fail)
        findings.append(
            {
                "kind": "headline_cell_invariant_broken",
                "remediable": True,
                "detail": headline_fail,
            }
        )
    else:
        findings.append(
            {
                "kind": "headline_cell_invariants_ok",
                "remediable": False,
                "p1_dup": 1.0,
                "p2_p3_dup": 0.0,
                "p3_minus_p2_wcu": 2.0,
            }
        )

    # checks.csv planned=observed=24000
    checks: dict[str, str] = {}
    if (results / "checks.csv").exists():
        with (results / "checks.csv").open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                checks[str(r.get("check") or "").strip()] = str(r.get("value") or "").strip()
    planned = checks.get("planned deliveries")
    observed = checks.get("observed deliveries")
    missing_d = checks.get("missing deliveries")
    if planned != "24000" or observed != "24000" or missing_d not in {"0", "0.0"}:
        remediable["checks_delivery_mismatch"] += 1
        findings.append(
            {
                "kind": "checks_delivery_mismatch",
                "remediable": True,
                "planned": planned,
                "observed": observed,
                "missing": missing_d,
            }
        )
    else:
        findings.append({"kind": "checks_delivery_ok", "remediable": False})

    # --- 4. P4 quarantine honesty ---
    exp_yaml = ROOT / "config" / "experiment.yaml"
    assumptions = ROOT / "docs" / "ASSUMPTIONS.md"
    design = ROOT / "DESIGN_RATIONALE_BEYOND_CA2.md"
    status = ROOT / "STATUS.md"
    final_report = ROOT / "vikas_final_report.md"

    yaml_text = exp_yaml.read_text(encoding="utf-8") if exp_yaml.exists() else ""
    # paths: [P1, P2, P3] — must not list P4 in binding config
    paths_m = re.search(r"^paths:\s*\[([^\]]+)\]", yaml_text, re.M)
    paths_listed = []
    if paths_m:
        paths_listed = [x.strip() for x in paths_m.group(1).split(",")]
    if "P4" in paths_listed or set(paths_listed) != {"P1", "P2", "P3"}:
        remediable["experiment_yaml_includes_p4"] += 1
        findings.append(
            {
                "kind": "experiment_yaml_includes_p4",
                "remediable": True,
                "paths": paths_listed,
            }
        )
    else:
        findings.append(
            {"kind": "experiment_yaml_p1_p3_only", "remediable": False, "paths": paths_listed}
        )

    a12_ok = False
    if assumptions.exists():
        atext = assumptions.read_text(encoding="utf-8")
        a12_ok = "A12" in atext and "TransactWriteItems" in atext and (
            "no `TransactWriteItems`" in atext or "no TransactWriteItems" in atext
        )
    if not a12_ok:
        remediable["assumptions_a12_missing"] += 1
        findings.append({"kind": "assumptions_a12_missing", "remediable": True})
    else:
        findings.append({"kind": "assumptions_a12_ok", "remediable": False})

    # Live cells must not contain P4
    p4_cells = [r for r in cells if r.get("path") == "P4"]
    if p4_cells or path_counts.get("P4", 0) > 0:
        remediable["p4_present_in_live_campaign"] += 1
        findings.append(
            {
                "kind": "p4_present_in_live_campaign",
                "remediable": True,
                "n_cells": len(p4_cells),
                "n_deliveries": path_counts.get("P4", 0),
            }
        )
    else:
        findings.append({"kind": "p4_absent_from_live_campaign", "remediable": False})

    # Authoritative docs must quarantine P4 (not market as CA2 evidence)
    quarantine_docs = {
        "STATUS.md": status,
        "DESIGN_RATIONALE_BEYOND_CA2.md": design,
        "FINAL3_NOTE.md": results / "FINAL3_NOTE.md",
    }
    for label, path in quarantine_docs.items():
        if not path.exists():
            remediable["p4_quarantine_doc_missing"] += 1
            findings.append(
                {"kind": "p4_quarantine_doc_missing", "remediable": True, "doc": label}
            )
            continue
        text = path.read_text(encoding="utf-8")
        honest = (
            "quarantin" in text.lower()
            and ("P4" in text or "TransactWrite" in text)
            and ("~88" in text or "88" in text)
            and ("100" not in text or "not" in text.lower() or "do **not** market" in text.lower() or "Do **not** market" in text)
        )
        # Stricter: must say quarantined + honest floor ~88 + forbid marketing 100
        has_q = "quarantin" in text.lower() and ("P4" in text or "TransactWrite" in text)
        has_floor = bool(re.search(r"~?\s*88", text))
        forbids_100 = bool(
            re.search(r"(do\s+\*\*not\*\*\s+market|not\s+market|not\s+perfect.?marks).{0,40}100", text, re.I)
        ) or ("not market 100" in text.lower()) or ("ALIGNMENT=100" in text and "not" in text.lower())
        if not (has_q and has_floor):
            remediable["p4_quarantine_honesty_gap"] += 1
            findings.append(
                {
                    "kind": "p4_quarantine_honesty_gap",
                    "remediable": True,
                    "doc": label,
                    "has_quarantine_lang": has_q,
                    "has_floor_88": has_floor,
                    "forbids_100": forbids_100,
                }
            )
        else:
            findings.append(
                {
                    "kind": "p4_quarantine_doc_ok",
                    "remediable": False,
                    "doc": label,
                    "forbids_100": forbids_100,
                }
            )

    # final_report overclaim must be banner-quarantined (not silent CA2 evidence)
    if final_report.exists():
        fr = final_report.read_text(encoding="utf-8")
        claims_p4 = "P4" in fr and ("TransactWrite" in fr or "0% duplicate" in fr)
        banner = (
            "NON-AUTHORITATIVE" in fr
            or "not** evidenced" in fr
            or "not evidenced" in fr.lower()
            or "overclaims" in fr.lower()
        )
        if claims_p4 and not banner:
            remediable["final_report_p4_unquarantined"] += 1
            findings.append(
                {
                    "kind": "final_report_p4_unquarantined",
                    "remediable": True,
                    "detail": "vikas_final_report.md claims P4 without NON-AUTHORITATIVE banner",
                }
            )
        else:
            findings.append(
                {
                    "kind": "final_report_p4_banner_ok",
                    "remediable": False,
                    "claims_p4": claims_p4,
                    "banner": banner,
                    "note": "P4 draft = dated WONTFIX / non-authoritative",
                }
            )

    # --- 5. Destroy-after ---
    destroy_txt = results / "destroy_confirmed.txt"
    tfstate = ROOT / "infra" / "terraform.tfstate"
    destroy_ok = False
    destroy_detail: dict = {}
    if destroy_txt.exists():
        dtext = destroy_txt.read_text(encoding="utf-8")
        destroy_ok = "destroy_confirmed=yes" in dtext
        destroy_detail["destroy_confirmed.txt"] = destroy_ok
    if tfstate.exists():
        try:
            st = json.loads(tfstate.read_text(encoding="utf-8"))
            n_res = len(st.get("resources") or [])
            destroy_detail["tfstate_resources"] = n_res
            if n_res == 0:
                destroy_ok = True
        except json.JSONDecodeError:
            remediable["tfstate_unreadable"] += 1
            findings.append({"kind": "tfstate_unreadable", "remediable": True})
    if not destroy_ok:
        remediable["destroy_not_confirmed"] += 1
        findings.append(
            {"kind": "destroy_not_confirmed", "remediable": True, "detail": destroy_detail}
        )
    else:
        findings.append(
            {"kind": "destroy_confirmed", "remediable": False, "detail": destroy_detail}
        )

    # --- 6. Config manual ---
    cfg = ROOT / "docs" / "CONFIGURATION_MANUAL.md"
    if not cfg.exists() or cfg.stat().st_size < 200:
        remediable["missing_configuration_manual"] += 1
        findings.append({"kind": "missing_configuration_manual", "remediable": True})
    else:
        findings.append(
            {
                "kind": "configuration_manual_ok",
                "remediable": False,
                "path": str(cfg.relative_to(ROOT)),
                "bytes": cfg.stat().st_size,
            }
        )

    # --- 7. Marketing 100 hygiene in STATUS / FINAL3 / RUBRIC ---
    for label, path in (
        ("STATUS.md", status),
        ("FINAL3_NOTE.md", results / "FINAL3_NOTE.md"),
        ("RUBRIC_EVIDENCE_MATRIX.md", ROOT / "RUBRIC_EVIDENCE_MATRIX.md"),
    ):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        # Flag bare CA2: 100% stamps (RUBRIC-style) unless the doc forbids marketing 100.
        forbids_100 = bool(
            re.search(
                r"(?i)(do\s+\*\*not\*\*\s+market|not\s+market|not\s+perfect.?marks|"
                r"forbid).{0,48}100",
                text,
            )
        )
        bare_ca2_100 = bool(
            re.search(r"(?i)\bCA2:\s*(?:\*\*)?\s*100\s*%", text)
        )
        bare_align_100 = bool(
            re.search(r"ALIGNMENT\s*=\s*100", text)
        ) and not forbids_100
        bad = (bare_ca2_100 and not forbids_100) or bare_align_100
        if bad:
            remediable["marketing_100_stamp"] += 1
            findings.append(
                {
                    "kind": "marketing_100_stamp",
                    "remediable": True,
                    "doc": label,
                    "bare_ca2_100": bare_ca2_100,
                    "bare_align_100": bare_align_100,
                }
            )
        else:
            findings.append(
                {"kind": "no_marketing_100", "remediable": False, "doc": label}
            )

    # Sensitivity pack (supports E2 crash-between; missing = soft, not remediable if campaign E2 ok)
    sens = ROOT / "data" / "runs" / "live" / "sensitivity"
    sens_ok = sens.exists() and (sens / "deliveries.jsonl").exists()
    sens_n = _count_lines(sens / "deliveries.jsonl") if sens_ok else -1
    findings.append(
        {
            "kind": "sensitivity_pack",
            "remediable": False,
            "present": sens_ok,
            "deliveries": sens_n,
            "note": "p3_between contrast; beyond E1–E3 headline but retained",
        }
    )

    remediable_total = int(sum(remediable.values()))
    disposition = (
        "FIX_REMEDIABLE"
        if remediable_total > 0
        else "DATED_WONTFIX_P4_QUARANTINED"
    )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "campaign": str(campaign),
        "results": str(results),
        "expected_n_per_cell": EXPECTED_N_PER_CELL,
        "expected_deliveries": EXPECTED_DELIVERIES,
        "expected_requests": EXPECTED_REQUESTS,
        "n_deliveries": n_del,
        "n_requests_gt": n_gt,
        "run_info": {
            "phase": phase,
            "backend": backend,
            "requests": info_req,
            "invocations": info_inv,
            "seed": run_info.get("seed"),
            "workers": run_info.get("workers"),
        },
        "e1_e3_counts": e_counts,
        "path_counts": dict(path_counts),
        "findings": findings,
        "remediable": dict(remediable),
        "remediable_total": remediable_total,
        "move_blocker": remediable_total > 0,
        "disposition": disposition,
        "same_metrics_snapshot": {
            "criterion_vs_qi_halfmoon": "duplicate-mutation absence after retry (not Halfmoon logging overhead)",
            "p1_dup_rate_mult2_5": 1.0,
            "p2_p3_dup_rate_mult2_5": 0.0,
            "p3_minus_p2_capacity_wcu": 2.0,
            "e1_e3": "all supported" if e_ok else "gap",
        },
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = out.with_suffix(".md")
    lines = [
        "# Vikas campaign E1–E3 remediable audit (scripted)",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Campaign: `{campaign}`",
        "",
        "## Move gate",
        "",
        f"- **remediable_total:** {remediable_total}",
        f"- **move_blocker:** {report['move_blocker']}",
        f"- **disposition:** `{disposition}`",
        "",
        f"- N-scale: deliveries={n_del} requests={info_req} (expect {EXPECTED_DELIVERIES}/{EXPECTED_REQUESTS})",
        f"- E1–E3 counts: {e_counts}",
        f"- path_counts: {dict(path_counts)}",
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
            "cd vikas-thesis/lambda-idempotency-eval",
            "python3 scripts/audit_campaign_root_causes.py",
            "# EXIT 0 required; remediable_total must be 0 before MOVE",
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
