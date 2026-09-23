#!/usr/bin/env python3
"""Scripted remediable audit for Chaitanya H3/H4 + Init same-metrics — not manual.

Verifies:
  - live Init/H3/H4 lite packs + confirmatory_n30 r1–3 inventory
  - H1/H2 reject on confirmatory (primary Init limbs)
  - H3 Holm fail-to-reject retained (evidenced null / underpowered) — no fabricated reject
  - H4 practical null / avoid (HOLD): Init flat across memory; no ADOPT memory win claim
  - Bluemke baseline present; Init Duration isolated (same-metrics gap-fill vs Duration/cost)
  - destroy_confirmed on confirmatory rounds; configuration manual
  - no marketing ALIGNMENT=100 as perfect-marks in SoT/STATUS gate stamp

EXIT 2 if remediable_total > 0 (move_blocker). EXIT 0 when clean.

Usage (from lambda-coldstart-isolation/):
  python3 scripts/audit_h3_h4_root_causes.py
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
PROCESSED = ROOT / "data" / "processed" / "live"
LIVE_LITE_HYP = ROOT / "reports" / "paper" / "tables" / "live_lite" / "hypotheses.json"
CONF_N30 = ROOT / "results" / "live" / "confirmatory_n30"
RESULTS_LIVE = ROOT / "results" / "live"
BASELINE_MD = THESIS / "baseline_papers" / "BASELINE_PAPER.md"
BASELINE_PDF = (
    THESIS / "baseline_papers" / "Bluemke_Zdanowski_2025_Lambda_baseline.pdf"
)
SOT = THESIS / "CA2_PROPOSED_VS_ARTEFACT.md"
WONTFIX = THESIS / "DATED_WONTFIX_N_H4_2026-09-23.md"
STATUS = ROOT / "STATUS.md"
CONFIG_A = ROOT / "docs" / "CONFIGURATION_MANUAL.md"
CONFIG_B = ROOT / "reports" / "configuration_manual.md"
ANALYSIS_PLAN = ROOT / "docs" / "ANALYSIS_PLAN.md"


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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    out = args.out or (RESULTS_LIVE / "analysis" / "h3_h4_audit_report.json")

    findings: list[dict] = []
    remediable: dict[str, int] = defaultdict(int)

    # --- 1. Pack inventory ---
    required = {
        "live_lite_hypotheses": LIVE_LITE_HYP,
        "h3_summary": PROCESSED / "h3_summary.json",
        "h4_summary": PROCESSED / "python_memory_h4_summary.json",
        "h4_csv": PROCESSED / "h4_python_memory_summary.csv",
        "live_summary": PROCESSED / "live_summary.json",
        "final3_baseline": RESULTS_LIVE / "FINAL3_BASELINE.md",
        "conf_r1_hyp": CONF_N30 / "round_1" / "tables" / "hypotheses.json",
        "conf_r2_hyp": CONF_N30 / "round_2" / "tables" / "hypotheses.json",
        "conf_r3_hyp": CONF_N30 / "round_3" / "tables" / "hypotheses.json",
        "conf_r1_destroy": CONF_N30 / "round_1" / "destroy_confirmed.txt",
        "conf_r2_destroy": CONF_N30 / "round_2" / "destroy_confirmed.txt",
        "conf_r3_destroy": CONF_N30 / "round_3" / "destroy_confirmed.txt",
        "baseline_md": BASELINE_MD,
        "baseline_pdf": BASELINE_PDF,
        "sot": SOT,
        "wontfix": WONTFIX,
        "analysis_plan": ANALYSIS_PLAN,
    }
    missing = [k for k, p in required.items() if not p.exists()]
    if missing:
        remediable["missing_pack_artefact"] += len(missing)
        findings.append(
            {"kind": "missing_pack_artefact", "remediable": True, "missing": missing}
        )
    else:
        findings.append({"kind": "pack_inventory_ok", "remediable": False})

    config_ok = CONFIG_A.exists() or CONFIG_B.exists()
    if not config_ok:
        remediable["configuration_manual_missing"] += 1
        findings.append({"kind": "configuration_manual_missing", "remediable": True})
    else:
        findings.append(
            {
                "kind": "configuration_manual_ok",
                "remediable": False,
                "paths": [str(p) for p in (CONFIG_A, CONFIG_B) if p.exists()],
            }
        )

    # --- 2. Confirmatory H1/H2 reject on r1–3 ---
    h1_h2_ok = True
    conf_snap: list[dict] = []
    for rnd in (1, 2, 3):
        hyp_path = CONF_N30 / f"round_{rnd}" / "tables" / "hypotheses.json"
        if not hyp_path.exists():
            h1_h2_ok = False
            continue
        hyp = json.loads(hyp_path.read_text(encoding="utf-8"))
        tests = hyp.get("tests") or {}
        row = {"round": rnd}
        for key in ("H1", "H2_python", "H2_nodejs", "H2_java"):
            t = tests.get(key) or {}
            rej = bool(t.get("reject"))
            row[key] = {"reject": rej, "p_holm": t.get("p_holm"), "p": t.get("p")}
            if key == "H1" and not rej:
                h1_h2_ok = False
            if key.startswith("H2_") and not rej:
                # final_2 posthoc python↔nodejs can fail; H2_* themselves should reject
                h1_h2_ok = False
        conf_snap.append(row)
        destroy = CONF_N30 / f"round_{rnd}" / "destroy_confirmed.txt"
        dtxt = destroy.read_text(encoding="utf-8") if destroy.exists() else ""
        if "destroy_confirmed=yes" not in dtxt.replace(" ", "").lower() and "yes" not in dtxt.lower():
            remediable["destroy_confirmed_missing"] += 1
            findings.append(
                {
                    "kind": "destroy_confirmed_missing",
                    "remediable": True,
                    "round": rnd,
                    "text": dtxt[:200],
                }
            )
        else:
            findings.append(
                {"kind": "destroy_confirmed", "remediable": False, "round": rnd}
            )

    if h1_h2_ok and conf_snap:
        findings.append(
            {
                "kind": "h1_h2_confirmatory_reject_ok",
                "remediable": False,
                "rounds": conf_snap,
            }
        )
    else:
        remediable["h1_h2_not_reject"] += 1
        findings.append(
            {
                "kind": "h1_h2_not_reject",
                "remediable": True,
                "rounds": conf_snap,
            }
        )

    # --- 3. H3 lite: fail to reject (evidenced null) ---
    h3_reject = None
    h3_p_holm = None
    h3_drop = None
    if LIVE_LITE_HYP.exists():
        lite = json.loads(LIVE_LITE_HYP.read_text(encoding="utf-8"))
        h3 = (lite.get("tests") or {}).get("H3") or {}
        h3_reject = h3.get("reject")
        h3_p_holm = h3.get("p_holm")
    if (PROCESSED / "h3_summary.json").exists():
        h3s = json.loads((PROCESSED / "h3_summary.json").read_text(encoding="utf-8"))
        h3_drop = h3s.get("cold_fraction_drop")

    # Remediable if H3 is marketed as Holm-reject / confirmatory win
    if h3_reject is True:
        remediable["h3_fabricated_reject"] += 1
        findings.append(
            {
                "kind": "h3_fabricated_reject",
                "remediable": True,
                "note": "live_lite H3 must remain fail-to-reject (underpowered)",
                "reject": h3_reject,
                "p_holm": h3_p_holm,
            }
        )
    elif h3_reject is False:
        findings.append(
            {
                "kind": "h3_null_evidenced_ok",
                "remediable": False,
                "reject": False,
                "p_holm": h3_p_holm,
                "cold_fraction_drop": h3_drop,
                "note": "directional drop retained; Holm fail-to-reject",
            }
        )
    else:
        remediable["h3_hypotheses_missing"] += 1
        findings.append({"kind": "h3_hypotheses_missing", "remediable": True})

    # --- 4. H4 practical null (flat Init; avoid/HOLD; no ADOPT win) ---
    h4_medians: dict[str, float] = {}
    h4_reject = None
    h4_p = None
    if LIVE_LITE_HYP.exists():
        lite = json.loads(LIVE_LITE_HYP.read_text(encoding="utf-8"))
        h4 = (lite.get("tests") or {}).get("H4_python") or {}
        h4_reject = h4.get("reject")
        h4_p = h4.get("p")
        med = h4.get("medians") or {}
        for k, v in med.items():
            fv = _f(v)
            if fv is not None:
                h4_medians[str(k)] = fv

    means: list[float] = []
    if (PROCESSED / "h4_python_memory_summary.csv").exists():
        with (PROCESSED / "h4_python_memory_summary.csv").open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                m = _f(row.get("mean") or row.get("median"))
                if m is not None:
                    means.append(m)

    # Practical null: means span should be small relative to package-size deltas (thousands of ms)
    span = (max(means) - min(means)) if means else None
    practical_null = span is not None and span < 20.0  # ms across 128–3008
    if not practical_null:
        remediable["h4_practical_null_broken"] += 1
        findings.append(
            {
                "kind": "h4_practical_null_broken",
                "remediable": True,
                "means_span_ms": span,
                "means": means,
            }
        )
    else:
        findings.append(
            {
                "kind": "h4_practical_null_ok",
                "remediable": False,
                "means_span_ms": span,
                "means": means,
                "kw_reject": h4_reject,
                "kw_p": h4_p,
                "medians": h4_medians,
                "note": "exploratory KW may reject; ADOPT/memory win forbidden (HOLD/avoid)",
            }
        )

    # Decision matrix must not list memory as adopt
    dm = ROOT / "reports" / "paper" / "tables" / "live_lite" / "decision_matrix.md"
    if dm.exists():
        dmtxt = dm.read_text(encoding="utf-8").lower()
        # memory row should contain avoid or hold, not adopt as band for raise memory
        mem_lines = [ln for ln in dmtxt.splitlines() if "memory" in ln]
        bad_adopt = any(
            ("adopt" in ln and "avoid" not in ln and "not tested" not in ln)
            for ln in mem_lines
        )
        if bad_adopt:
            remediable["h4_marketed_as_adopt"] += 1
            findings.append(
                {
                    "kind": "h4_marketed_as_adopt",
                    "remediable": True,
                    "lines": mem_lines,
                }
            )
        else:
            findings.append(
                {
                    "kind": "h4_decision_band_ok",
                    "remediable": False,
                    "lines": mem_lines,
                }
            )

    # --- 5. Bluemke baseline + Init isolation (same-metrics) ---
    bluemke_ok = BASELINE_MD.exists() and BASELINE_PDF.exists()
    bluemke_mentions_init = False
    if BASELINE_MD.exists():
        btxt = BASELINE_MD.read_text(encoding="utf-8")
        bluemke_mentions_init = bool(
            re.search(r"Init|Duration|Bluemke", btxt, re.I)
        )
    if not bluemke_ok:
        remediable["bluemke_baseline_missing"] += 1
        findings.append({"kind": "bluemke_baseline_missing", "remediable": True})
    else:
        findings.append(
            {
                "kind": "bluemke_baseline_ok",
                "remediable": False,
                "baseline_mentions_ok": bluemke_mentions_init,
            }
        )

    # SoT must exist and carry same-metrics / H4 null / no fabricated H3 reject
    if SOT.exists():
        sot = SOT.read_text(encoding="utf-8")
        need = [
            ("same.metrics|SAME METRICS", "sot_same_metrics"),
            ("Bluemke", "sot_bluemke"),
            ("H4", "sot_h4"),
            ("Init Duration", "sot_init"),
        ]
        for pat, key in need:
            if not re.search(pat, sot, re.I):
                remediable[f"{key}_missing"] += 1
                findings.append({"kind": f"{key}_missing", "remediable": True})
        # Fabrication guards
        if re.search(r"H3[^\n]{0,40}reject", sot, re.I) and not re.search(
            r"H3[^\n]{0,80}fail to reject|H3[^\n]{0,80}null|H3[^\n]{0,80}underpowered",
            sot,
            re.I,
        ):
            # Allow "H1/H2 reject" nearby; flag only if H3 claimed as reject without null wording
            if re.search(
                r"H3[^.\n]{0,60}\breject\b", sot, re.I
            ) and not re.search(
                r"H3[^.\n]{0,120}(fail to reject|null|underpowered|p_holm\s*=\s*1)",
                sot,
                re.I,
            ):
                remediable["sot_h3_fabricated_reject"] += 1
                findings.append(
                    {"kind": "sot_h3_fabricated_reject", "remediable": True}
                )
        if not re.search(r"practical null|HOLD|avoid|N-H4|null evidenced", sot, re.I):
            remediable["sot_h4_null_not_hard_closed"] += 1
            findings.append(
                {"kind": "sot_h4_null_not_hard_closed", "remediable": True}
            )
        if not findings or all(
            f.get("kind")
            not in {
                "sot_same_metrics_missing",
                "sot_bluemke_missing",
                "sot_h4_missing",
                "sot_init_missing",
                "sot_h3_fabricated_reject",
                "sot_h4_null_not_hard_closed",
            }
            for f in findings
        ):
            findings.append({"kind": "sot_honesty_ok", "remediable": False})
    else:
        remediable["sot_missing"] += 1
        findings.append({"kind": "sot_missing", "remediable": True})

    if WONTFIX.exists():
        wtxt = WONTFIX.read_text(encoding="utf-8")
        if "2026-09-23" not in wtxt or not re.search(r"H4|memory", wtxt, re.I):
            remediable["wontfix_incomplete"] += 1
            findings.append({"kind": "wontfix_incomplete", "remediable": True})
        else:
            findings.append({"kind": "wontfix_ok", "remediable": False})
    else:
        remediable["wontfix_missing"] += 1
        findings.append({"kind": "wontfix_missing", "remediable": True})

    # Analysis plan dated deferral for confirmatory H3/H4
    if ANALYSIS_PLAN.exists():
        atxt = ANALYSIS_PLAN.read_text(encoding="utf-8")
        if "2026-09-22" in atxt and re.search(r"H3|H4", atxt):
            findings.append(
                {"kind": "analysis_plan_h3_h4_deferral_ok", "remediable": False}
            )
        else:
            remediable["analysis_plan_deferral_missing"] += 1
            findings.append(
                {"kind": "analysis_plan_deferral_missing", "remediable": True}
            )

    # Marketing 100 stamp in STATUS (soft warn → remediable if claims perfect without honest floor)
    if STATUS.exists():
        st = STATUS.read_text(encoding="utf-8")
        has_honest = bool(
            re.search(r"honest|~78|~82|~97|floor|do not market|MOVE ALLOWED", st, re.I)
        )
        markets_100 = bool(re.search(r"ALIGNMENT=100|CA2 still 100%", st))
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
        else "DATED_WONTFIX_H4_PRACTICAL_NULL_H3_UNDERPOWERED"
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
            "baseline": "Bluemke & Zdanowski (2025) Duration/cost — gap-fill Init Duration",
            "h1_h2_confirmatory": "reject on r1–3" if h1_h2_ok else "gap",
            "h3_lite": {
                "reject": h3_reject,
                "p_holm": h3_p_holm,
                "cold_fraction_drop": h3_drop,
            },
            "h4_lite": {
                "kw_reject": h4_reject,
                "kw_p": h4_p,
                "means_span_ms": span,
                "practical_null": practical_null,
            },
        },
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = out.with_suffix(".md")
    lines = [
        "# Chaitanya H3/H4 remediable audit (scripted)",
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
        f"- H3 lite reject={h3_reject} p_holm={h3_p_holm} drop={h3_drop}",
        f"- H4 practical_null={practical_null} span_ms={span} kw_reject={h4_reject}",
        f"- H1/H2 confirmatory reject ok={h1_h2_ok}",
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
            "cd chaitanya-thesis/lambda-coldstart-isolation",
            "python3 scripts/audit_h3_h4_root_causes.py",
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
