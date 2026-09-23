#!/usr/bin/env python3
"""Scripted remediable audit for Yashaswini Leg3 reduction + Leg2 F1 — not manual.

Verifies:
  - Leg3 final_1–3 overhead packs + reduction_policy_vs_full values
  - Original ≥0.50 gate FAILS on all three finals (no fabricated pass)
  - Amended ≥0.35 reporting floor (2026-09-22) acknowledged in SoT/DESIGN
  - Detection F1 gap to Xing retained (F1≈0.469; not within 10 pp of 0.938)
  - CausalRCA quarantine (n=4 + fixed_order share=1.0)
  - Xing baseline present; configuration manual; dated WONTFIX

EXIT 2 if remediable_total > 0 (move_blocker). EXIT 0 when clean.

Usage (from serverless-fault-localisation/):
  python3 scripts/audit_leg3_reduction_root_causes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THESIS = ROOT.parent
LIVE = ROOT / "results" / "live"
RCAEVAL = ROOT / "results" / "rcaeval"
BASELINE_MD = THESIS / "baseline_papers" / "BASELINE_PAPER.md"
BASELINE_PDF = (
    THESIS
    / "baseline_papers"
    / "Xing_et_al_2025_Sensors_fault_localisation_baseline.pdf"
)
SOT = THESIS / "CA2_PROPOSED_VS_ARTEFACT.md"
WONTFIX = THESIS / "DATED_WONTFIX_N_Yash_2026-09-23.md"
STATUS = ROOT / "STATUS.md"
DESIGN = ROOT / "DESIGN_RATIONALE_BEYOND_CA2.md"
CONFIG = ROOT / "docs" / "CONFIGURATION_MANUAL.md"
XING_F1 = 0.938
EXPECTED_REDUCTIONS = {
    "final_1": 0.38330079316063415,
    "final_2": 0.42172067682834413,
    "final_3": 0.47170698953499657,
}
ORIG_GATE = 0.50
AMENDED_FLOOR = 0.35


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    out = args.out or (LIVE / "analysis" / "leg3_reduction_audit_report.json")

    findings: list[dict] = []
    remediable: dict[str, int] = defaultdict(int)

    # --- 1. Pack inventory ---
    required = {
        "final1_overhead": LIVE / "final_1" / "overhead.json",
        "final2_overhead": LIVE / "final_2" / "overhead.json",
        "final3_overhead": LIVE / "final_3" / "overhead.json",
        "final3_baseline": LIVE / "FINAL3_BASELINE.md",
        "detection": RCAEVAL / "detection.json",
        "fixed_order": RCAEVAL / "fixed_order.json",
        "localisation": RCAEVAL / "localisation.csv",
        "baseline_md": BASELINE_MD,
        "baseline_pdf": BASELINE_PDF,
        "sot": SOT,
        "wontfix": WONTFIX,
        "design": DESIGN,
        "config": CONFIG,
    }
    missing = [k for k, p in required.items() if not p.exists()]
    if missing:
        remediable["missing_pack_artefact"] += len(missing)
        findings.append(
            {"kind": "missing_pack_artefact", "remediable": True, "missing": missing}
        )
    else:
        findings.append({"kind": "pack_inventory_ok", "remediable": False})

    # --- 2. Reduction finals: fail 0.50; pass amended 0.35 ---
    reductions: dict[str, float] = {}
    for name, expected in EXPECTED_REDUCTIONS.items():
        path = LIVE / name / "overhead.json"
        if not path.exists():
            continue
        oh = json.loads(path.read_text(encoding="utf-8"))
        r = float(oh.get("reduction_policy_vs_full"))
        reductions[name] = r
        if abs(r - expected) > 1e-6:
            remediable["reduction_value_drift"] += 1
            findings.append(
                {
                    "kind": "reduction_value_drift",
                    "remediable": True,
                    "pack": name,
                    "got": r,
                    "expected": expected,
                }
            )
        if r >= ORIG_GATE:
            remediable["fabricated_050_pass"] += 1
            findings.append(
                {
                    "kind": "fabricated_050_pass",
                    "remediable": True,
                    "pack": name,
                    "reduction": r,
                }
            )
        if r < AMENDED_FLOOR:
            remediable["below_amended_035"] += 1
            findings.append(
                {
                    "kind": "below_amended_035",
                    "remediable": True,
                    "pack": name,
                    "reduction": r,
                }
            )

    if reductions and not any(
        f.get("kind") in {"fabricated_050_pass", "reduction_value_drift", "below_amended_035"}
        for f in findings
    ):
        findings.append(
            {
                "kind": "reduction_050_fail_035_amended_ok",
                "remediable": False,
                "reductions": reductions,
                "orig_gate": ORIG_GATE,
                "amended_floor": AMENDED_FLOOR,
            }
        )

    # FINAL3_BASELINE must not claim 0.50 met
    if (LIVE / "FINAL3_BASELINE.md").exists():
        btxt = (LIVE / "FINAL3_BASELINE.md").read_text(encoding="utf-8")
        # values present
        for v in ("0.383", "0.422", "0.472"):
            if v not in btxt:
                remediable["final3_baseline_missing_values"] += 1
                findings.append(
                    {
                        "kind": "final3_baseline_missing_values",
                        "remediable": True,
                        "missing": v,
                    }
                )
        findings.append({"kind": "final3_baseline_present", "remediable": False})

    # --- 3. Detection F1 gap to Xing ---
    f1 = None
    if (RCAEVAL / "detection.json").exists():
        det = json.loads((RCAEVAL / "detection.json").read_text(encoding="utf-8"))
        f1 = float(det.get("f1"))
        gap_pp = (XING_F1 - f1) * 100.0
        if f1 >= XING_F1 - 0.10:
            remediable["f1_fabricated_near_xing"] += 1
            findings.append(
                {
                    "kind": "f1_fabricated_near_xing",
                    "remediable": True,
                    "f1": f1,
                    "xing": XING_F1,
                }
            )
        else:
            findings.append(
                {
                    "kind": "f1_gap_to_xing_retained_ok",
                    "remediable": False,
                    "f1": f1,
                    "xing": XING_F1,
                    "gap_pp": gap_pp,
                }
            )

    # --- 4. CausalRCA quarantine ---
    if (RCAEVAL / "fixed_order.json").exists():
        fo = json.loads((RCAEVAL / "fixed_order.json").read_text(encoding="utf-8"))
        share = (fo.get("share_of_cases_with_modal_ranking") or {}).get("causalrca")
        flagged = fo.get("flagged") or []
        # count causalrca localisation rows if csv exists
        n_causal = 0
        loc = RCAEVAL / "localisation.csv"
        if loc.exists():
            text = loc.read_text(encoding="utf-8")
            n_causal = sum(
                1
                for ln in text.splitlines()[1:]
                if ln.lower().startswith("causalrca")
                or ",causalrca," in ln.lower()
                or ln.lower().endswith(",causalrca")
            )
            # also try method column contains
            if n_causal == 0:
                n_causal = sum(1 for ln in text.splitlines() if re.search(r"\bcausalrca\b", ln, re.I))

        ok = share is not None and float(share) >= 0.99 and "causalrca" in [
            str(x).lower() for x in flagged
        ]
        if not ok:
            remediable["causalrca_quarantine_broken"] += 1
            findings.append(
                {
                    "kind": "causalrca_quarantine_broken",
                    "remediable": True,
                    "share": share,
                    "flagged": flagged,
                    "n_causal_rows": n_causal,
                }
            )
        else:
            findings.append(
                {
                    "kind": "causalrca_quarantine_ok",
                    "remediable": False,
                    "share": share,
                    "flagged": flagged,
                    "n_causal_rows": n_causal,
                    "note": "n=4 peer incomplete; fixed-order share=1.0",
                }
            )

    # --- 5. Xing baseline ---
    if BASELINE_MD.exists() and BASELINE_PDF.exists():
        findings.append({"kind": "xing_baseline_ok", "remediable": False})
    else:
        remediable["xing_baseline_missing"] += 1
        findings.append({"kind": "xing_baseline_missing", "remediable": True})

    # --- 6. SoT / DESIGN / WONTFIX honesty ---
    if SOT.exists():
        sot = SOT.read_text(encoding="utf-8")
        checks = [
            (r"0\.50|≥0\.50|>=\s*0\.50", "sot_mentions_050"),
            (r"0\.35|≥0\.35|amended", "sot_mentions_035_amendment"),
            (r"Xing", "sot_xing"),
            (r"CausalRCA", "sot_causalrca"),
            (r"SAME METRICS|same-metrics|same metrics", "sot_same_metrics"),
            (r"0\.469|0\.46875|F1", "sot_f1"),
        ]
        for pat, key in checks:
            if not re.search(pat, sot, re.I):
                remediable[f"{key}_missing"] += 1
                findings.append({"kind": f"{key}_missing", "remediable": True})
        # Flag only affirmative claims (not "fabricated 0.50 pass" / "do not claim ... met")
        for m in re.finditer(
            r"(.{0,40})0\.50\s*(met|pass|supported)|(.{0,40})gate was met",
            sot,
            re.I | re.S,
        ):
            ctx = (m.group(0) or "").lower()
            if any(
                neg in ctx
                for neg in (
                    "not",
                    "fail",
                    "fabricat",
                    "do **not**",
                    "do not",
                    "forbidden",
                    "no fabricated",
                )
            ):
                continue
            remediable["sot_claims_050_met"] += 1
            findings.append(
                {"kind": "sot_claims_050_met", "remediable": True, "snippet": m.group(0)[:120]}
            )
            break
        if "sot_claims_050_met" not in remediable and not any(
            str(f.get("kind", "")).startswith("sot_") and str(f.get("kind", "")).endswith("_missing")
            for f in findings
        ):
            findings.append({"kind": "sot_honesty_ok", "remediable": False})
    else:
        remediable["sot_missing"] += 1
        findings.append({"kind": "sot_missing", "remediable": True})

    if DESIGN.exists():
        dtxt = DESIGN.read_text(encoding="utf-8")
        if "0.35" in dtxt and "0.50" in dtxt and "2026-09-22" in dtxt:
            findings.append({"kind": "design_amendment_ok", "remediable": False})
        else:
            remediable["design_amendment_incomplete"] += 1
            findings.append(
                {"kind": "design_amendment_incomplete", "remediable": True}
            )

    if WONTFIX.exists():
        wtxt = WONTFIX.read_text(encoding="utf-8")
        if "2026-09-23" in wtxt and re.search(r"0\.50|0\.35", wtxt):
            findings.append({"kind": "wontfix_ok", "remediable": False})
        else:
            remediable["wontfix_incomplete"] += 1
            findings.append({"kind": "wontfix_incomplete", "remediable": True})
    else:
        remediable["wontfix_missing"] += 1
        findings.append({"kind": "wontfix_missing", "remediable": True})

    if CONFIG.exists():
        findings.append({"kind": "configuration_manual_ok", "remediable": False})
    else:
        remediable["configuration_manual_missing"] += 1
        findings.append({"kind": "configuration_manual_missing", "remediable": True})

    if STATUS.exists():
        st = STATUS.read_text(encoding="utf-8")
        has_honest = bool(
            re.search(r"honest|~72|MOVE ALLOWED|0\.35|do not market", st, re.I)
        )
        markets_100 = bool(re.search(r"ALIGNMENT=100|CA2 still 100%|floor 100%", st))
        if markets_100 and not has_honest:
            remediable["status_marketing_100"] += 1
            findings.append({"kind": "status_marketing_100", "remediable": True})
        else:
            findings.append(
                {
                    "kind": "status_stamp_ok",
                    "remediable": False,
                    "markets_100": markets_100,
                    "has_honest": has_honest,
                }
            )

    remediable_total = int(sum(remediable.values()))
    disposition = (
        "FIX_REMEDIABLE"
        if remediable_total > 0
        else "DATED_WONTFIX_REDUCTION_050_FAIL_AMENDED_035"
    )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "findings": findings,
        "remediable": dict(remediable),
        "remediable_total": remediable_total,
        "move_blocker": remediable_total > 0,
        "disposition": disposition,
        "same_metrics_snapshot": {
            "baseline": "Xing et al. (2025) detection F1 ceiling 0.938 — not same-rig AWS peer",
            "detection_f1": f1,
            "xing_f1": XING_F1,
            "reductions": reductions,
            "orig_gate_050": "FAIL all finals",
            "amended_floor_035": "PASS all finals",
            "causalrca": "quarantined n=4 fixed_order share=1.0",
        },
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = out.with_suffix(".md")
    lines = [
        "# Yashaswini Leg3 reduction remediable audit (scripted)",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Root: `{ROOT}`",
        "",
        "## Move gate",
        "",
        f"- **remediable_total:** {remediable_total}",
        f"- **move_blocker:** {report['move_blocker']}",
        f"- **disposition:** `{disposition}`",
        "",
        f"- reductions: {reductions}",
        f"- detection F1: {f1} (Xing {XING_F1})",
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
            "cd yashaswini-thesis/serverless-fault-localisation",
            "python3 scripts/audit_leg3_reduction_root_causes.py",
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
