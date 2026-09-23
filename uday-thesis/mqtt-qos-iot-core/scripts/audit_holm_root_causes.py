#!/usr/bin/env python3
"""Scripted remediable audit for Uday Holm / d300>d60 soft limb — not manual chat.

Verifies live final_1|final_2 packs, confirmatory_1 Holm pack, Shvaika same-metrics
framing, and that d300>d60 is honestly FAIL (not fabricated reject). Intentional
lite-schedule ceiling gets dated WONTFIX when remediable_total=0.

Usage (from mqtt-qos-iot-core/):
  python3 scripts/audit_holm_root_causes.py
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "results" / "live"
EXPECTED_CELLS = 16
REQUIRED_CELL_KEYS = (
    "qos",
    "disconnect_s",
    "rate_mode",
    "loss_rate",
    "n_lost",
    "n_published",
)


def _f(x: object) -> float | None:
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _destroy_ok(pack: Path) -> bool:
    p = pack / "destroy_confirmed.txt"
    if not p.exists():
        return False
    return "destroy_confirmed=yes" in p.read_text(encoding="utf-8")


def _check_final(
    name: str,
    remediable: dict[str, int],
    findings: list[dict],
) -> list[dict]:
    pack = LIVE / name
    ev = pack / "LIVE_EVIDENCE.json"
    if not pack.exists() or not ev.exists():
        remediable[f"missing_{name}"] += 1
        findings.append({"kind": f"missing_{name}", "remediable": True})
        return []
    data = json.loads(ev.read_text(encoding="utf-8"))
    cells = data.get("cells") or []
    if len(cells) != EXPECTED_CELLS:
        remediable[f"cell_count_mismatch_{name}"] += 1
        findings.append(
            {
                "kind": f"cell_count_mismatch_{name}",
                "remediable": True,
                "n": len(cells),
                "expected": EXPECTED_CELLS,
            }
        )
    missing = []
    for c in cells:
        for k in REQUIRED_CELL_KEYS:
            if k not in c:
                missing.append(k)
    if missing:
        remediable[f"missing_metrics_{name}"] += 1
        findings.append(
            {
                "kind": f"missing_metrics_{name}",
                "remediable": True,
                "keys": sorted(set(missing)),
            }
        )
    if not _destroy_ok(pack):
        remediable[f"destroy_not_confirmed_{name}"] += 1
        findings.append({"kind": f"destroy_not_confirmed_{name}", "remediable": True})
    else:
        findings.append(
            {"kind": f"pack_ok_{name}", "remediable": False, "n": len(cells)}
        )
    return cells


def _scan_fabricated(remediable: dict[str, int], findings: list[dict]) -> None:
    patterns = [
        (
            re.compile(r"d300\s*>\s*d60.{0,40}(reject|significant|supported|pass)", re.I | re.S),
            "fabricated_d300_gt_d60_win",
        ),
        (
            re.compile(r"Holm.{0,40}d300.{0,20}(reject H0|significant)", re.I | re.S),
            "fabricated_holm_d300_reject",
        ),
        (
            re.compile(r"ALIGNMENT\s*=\s*100", re.I),
            "fabricated_alignment_100",
        ),
        (
            re.compile(r"formal\s+(N|5.?rep|80.?cell).{0,40}(complete|met|done)", re.I | re.S),
            "fabricated_formal_n_complete",
        ),
    ]
    scan = [
        ROOT / "STATUS.md",
        ROOT / "GENAI_HANDOFF.md",
        LIVE / "confirmatory_1" / "CONFIRMATORY.md",
        ROOT.parent / "CA2_PROPOSED_VS_ARTEFACT.md",
        ROOT.parent / "DATED_WONTFIX_N_Uday_2026-09-23.md",
    ]
    hits: dict[str, list[str]] = defaultdict(list)
    for path in scan:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for cre, kind in patterns:
            for m in cre.finditer(text):
                start = max(0, m.start() - 120)
                window = text[start : m.end() + 60].lower()
                if any(
                    tok in window
                    for tok in (
                        "fail",
                        "not met",
                        "wontfix",
                        "do not",
                        "don't",
                        "forbidden",
                        "not claim",
                        "cannot",
                        "identical",
                        "≡",
                        "rejected",
                        "overstated",
                        "honest",
                        "not market",
                        "dated wontfix",
                        "soft n",
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
        help="JSON report path (default: results/live/confirmatory_1/holm_audit_report.json)",
    )
    args = ap.parse_args()
    out = args.out or (LIVE / "confirmatory_1" / "holm_audit_report.json")

    findings: list[dict] = []
    remediable: dict[str, int] = defaultdict(int)

    final_cells: dict[str, list[dict]] = {}
    for name in ("final_1", "final_2"):
        final_cells[name] = _check_final(name, remediable, findings)

    # confirmatory_1 pack
    conf_dir = LIVE / "confirmatory_1"
    holm_path = conf_dir / "holm_stats.json"
    if not conf_dir.exists() or not holm_path.exists():
        remediable["missing_confirmatory_1"] += 1
        findings.append({"kind": "missing_confirmatory_1", "remediable": True})
        conf = {}
    else:
        conf = json.loads(holm_path.read_text(encoding="utf-8"))
        limb = conf.get("holm_d300_gt_d60_limb") or {}
        if limb.get("status") != "FAIL":
            remediable["d300_gt_d60_not_marked_fail"] += 1
            findings.append(
                {
                    "kind": "d300_gt_d60_not_marked_fail",
                    "remediable": True,
                    "got": limb.get("status"),
                }
            )
        by_rate = limb.get("by_rate") or {}
        for rate, row in by_rate.items():
            d60 = _f(row.get("d60_loss_rate"))
            d300 = _f(row.get("d300_loss_rate"))
            if d60 is None or d300 is None:
                remediable["missing_d300_d60_rates"] += 1
                findings.append(
                    {"kind": "missing_d300_d60_rates", "remediable": True, "rate": rate}
                )
            elif abs(d60 - d300) > 1e-9:
                # Evidence separated — then FAIL status would be wrong
                if limb.get("status") == "FAIL":
                    remediable["d300_d60_separated_but_marked_fail"] += 1
                    findings.append(
                        {
                            "kind": "d300_d60_separated_but_marked_fail",
                            "remediable": True,
                            "rate": rate,
                            "d60": d60,
                            "d300": d300,
                        }
                    )
            else:
                findings.append(
                    {
                        "kind": f"d300_equiv_d60_{rate}",
                        "remediable": False,
                        "loss": d60,
                    }
                )
        sources = set(conf.get("source_packs") or [])
        if not {"final_1", "final_2"}.issubset(sources):
            remediable["confirmatory_source_mismatch"] += 1
            findings.append(
                {
                    "kind": "confirmatory_source_mismatch",
                    "remediable": True,
                    "got": sorted(sources),
                }
            )
        snap = conf.get("same_metrics_snapshot") or {}
        if "Shvaika" not in str(snap.get("baseline_literature") or ""):
            remediable["missing_shvaika_baseline_framing"] += 1
            findings.append(
                {"kind": "missing_shvaika_baseline_framing", "remediable": True}
            )
        else:
            findings.append({"kind": "shvaika_framing_ok", "remediable": False})
        findings.append(
            {
                "kind": "confirmatory_1_ok",
                "remediable": False,
                "n_pooled_cells": conf.get("n_pooled_cells"),
            }
        )

    # Cross-check finals: QoS0 d60≡d300 and QoS1 loss=0
    for name, cells in final_cells.items():
        if not cells:
            continue
        by = {
            (int(c["qos"]), int(c["disconnect_s"]), str(c["rate_mode"])): _f(c.get("loss_rate"))
            for c in cells
        }
        for rate in ("steady", "bursty"):
            a = by.get((0, 60, rate))
            b = by.get((0, 300, rate))
            if a is None or b is None:
                remediable[f"missing_qos0_d60_d300_{name}"] += 1
                findings.append(
                    {
                        "kind": f"missing_qos0_d60_d300_{name}",
                        "remediable": True,
                        "rate": rate,
                    }
                )
            elif abs(a - b) > 1e-9:
                # Separated in data — fine; do not force FAIL
                findings.append(
                    {
                        "kind": f"d60_d300_separated_{name}_{rate}",
                        "remediable": False,
                        "d60": a,
                        "d300": b,
                    }
                )
            else:
                findings.append(
                    {
                        "kind": f"d60_equiv_d300_{name}_{rate}",
                        "remediable": False,
                        "loss": a,
                    }
                )
        qos1_losses = [_f(c.get("loss_rate")) for c in cells if int(c.get("qos", -1)) == 1]
        if qos1_losses and any(v is None or not math.isfinite(v) or v > 1e-12 for v in qos1_losses):
            remediable[f"qos1_nonzero_loss_{name}"] += 1
            findings.append(
                {
                    "kind": f"qos1_nonzero_loss_{name}",
                    "remediable": True,
                    "losses": qos1_losses,
                }
            )
        else:
            findings.append({"kind": f"qos1_loss_zero_{name}", "remediable": False})

    _scan_fabricated(remediable, findings)

    # Soft: final_3 / formal N are beyond-floor — missing is NOT remediable if DESIGN documents it
    design = ROOT.parent / "DESIGN_RATIONALE_BEYOND_CA2.md"
    if design.exists():
        findings.append(
            {
                "kind": "beyond_floor_design_present",
                "remediable": False,
                "note": "formal N / d60≠d300 separation / final_3 optional beyond disclosed lite",
            }
        )

    remediable_total = int(sum(remediable.values()))
    disposition = (
        "FIX_REMEDIABLE"
        if remediable_total > 0
        else "DATED_WONTFIX_HOLM_D300_GT_D60"
    )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "thesis": "uday",
        "artefact": "mqtt-qos-iot-core",
        "findings": findings,
        "remediable": dict(remediable),
        "remediable_total": remediable_total,
        "move_blocker": remediable_total > 0,
        "disposition": disposition,
        "n_uday_close": disposition.startswith("DATED_WONTFIX"),
        "soft_limbs": {
            "holm_d300_gt_d60": "FAIL under lite schedule (identical loss 0.68)",
            "formal_n_5rep_80cell": "beyond-floor / Free-Tier-blocked",
            "final_3": "absent on disk; confirmatory_1 pools final_1+final_2",
            "shvaika_prose_fold": "soft packaging",
        },
        "same_metrics_snapshot": (conf.get("same_metrics_snapshot") if conf else {}),
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = out.with_suffix(".md")
    lines = [
        "# Uday Holm / d300>d60 remediable audit (scripted)",
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
        "- Holm d300>d60: **FAIL** (lite schedule ceiling; d60≡d300 loss 0.68)",
        "- Formal N / 80-cell: **beyond-floor**",
        "- final_3: absent; confirmatory_1 = final_1+final_2 pool",
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
            "cd uday-thesis/mqtt-qos-iot-core",
            "python3 scripts/audit_holm_root_causes.py",
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
