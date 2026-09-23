#!/usr/bin/env python3
"""Scripted remediable audit for Nemi K8s deferral / Docker FL — not manual.

Verifies:
  - live cloud FL lite final_1–3 with destroy_status verified
  - Docker Compose multi-container FL ×3 (accuracy/F1 present; not K8s)
  - K8s/EKS not falsely claimed as executed
  - dated WONTFIX / DESIGN amendment for K8s deferral
  - Saklani baseline framing present; no marketing clone of 91.8% acc
  - config + STATUS honesty

EXIT 2 if remediable_total > 0 (move_blocker). EXIT 0 when clean
(disposition DATED_WONTFIX_K8S_DEFERRED).

Usage (from securefl-ids/):
  python3 scripts/audit_k8s_deferral_root_causes.py
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
DOCKER = ROOT / "results" / "docker_fl"
DESIGN = ROOT / "DESIGN_RATIONALE_BEYOND_CA2.md"
WONTFIX = THESIS / "DATED_WONTFIX_N_Nemi_2026-09-23.md"
CONFIG = ROOT / "docs" / "CONFIGURATION_MANUAL.md"
STATUS = THESIS / "STATUS.md"
BASELINE = THESIS / "baseline_papers" / "BASELINE_PAPER.md"
SOT = THESIS / "CA2_PROPOSED_VS_ARTEFACT.md"
EXPECTED = ("final_1", "final_2", "final_3")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _destroy_ok(summary: dict) -> bool:
    ds = summary.get("destroy_status") or {}
    if not isinstance(ds, dict):
        return False
    return (
        bool(summary.get("destroy_after"))
        and str(ds.get("terraform_destroy", "")).lower() in {"complete", "ok", "yes"}
        and bool(ds.get("verified_absent"))
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", type=Path, default=LIVE)
    ap.add_argument("--docker", type=Path, default=DOCKER)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    live = args.live
    docker = args.docker
    out = args.out or (docker / "analysis" / "k8s_deferral_audit_report.json")

    findings: list[dict] = []
    remediable: dict[str, int] = defaultdict(int)

    # --- live cloud FL finals ×3 ---
    live_rows: list[dict] = []
    for name in EXPECTED:
        pack = live / name
        summary_path = pack / "cloud_lite_summary.json"
        if not summary_path.exists():
            remediable["missing_live_final"] += 1
            findings.append(
                {"kind": "missing_live_final", "remediable": True, "pack": name}
            )
            continue
        data = _load(summary_path)
        arms = data.get("arms") or {}
        base = (arms.get("baseline") or {}).get("summary") or {}
        improved = (arms.get("improved") or {}).get("summary") or {}
        row = {
            "pack": name,
            "baseline_accuracy": base.get("accuracy"),
            "baseline_f1": base.get("f1_score"),
            "improved_accuracy": improved.get("accuracy"),
            "improved_f1": improved.get("f1_score"),
            "avg_comm_baseline": base.get("avg_communication_cost"),
            "avg_comm_improved": improved.get("avg_communication_cost"),
        }
        if row["baseline_accuracy"] is None or row["improved_accuracy"] is None:
            remediable["live_final_missing_metrics"] += 1
            findings.append(
                {
                    "kind": "live_final_missing_metrics",
                    "remediable": True,
                    "pack": name,
                }
            )
        else:
            live_rows.append(row)
            findings.append(
                {"kind": "live_final_ok", "remediable": False, "pack": name, **row}
            )
        if not _destroy_ok(data):
            remediable["live_destroy_not_confirmed"] += 1
            findings.append(
                {
                    "kind": "live_destroy_not_confirmed",
                    "remediable": True,
                    "pack": name,
                }
            )
        else:
            findings.append(
                {"kind": "live_destroy_ok", "remediable": False, "pack": name}
            )

    # --- Docker FL ×3 ---
    docker_rows: list[dict] = []
    compose = ROOT / "docker-compose.yml"
    if not compose.exists():
        remediable["missing_docker_compose"] += 1
        findings.append({"kind": "missing_docker_compose", "remediable": True})
    else:
        findings.append({"kind": "docker_compose_present", "remediable": False})

    for name in EXPECTED:
        pack = docker / name
        summary_path = pack / "docker_fl_summary.json"
        if not summary_path.exists():
            remediable["missing_docker_final"] += 1
            findings.append(
                {"kind": "missing_docker_final", "remediable": True, "pack": name}
            )
            continue
        data = _load(summary_path)
        acc = data.get("accuracy")
        f1 = data.get("f1")
        note = str(data.get("note") or "")
        mode = str(data.get("mode") or "")
        if acc is None or f1 is None:
            remediable["docker_final_missing_metrics"] += 1
            findings.append(
                {
                    "kind": "docker_final_missing_metrics",
                    "remediable": True,
                    "pack": name,
                }
            )
            continue
        claims_k8s = bool(
            re.search(r"(?i)\bkubernetes\b|\bk8s\b|\beks\b", mode + " " + note)
            and not re.search(r"(?i)not\s+k8s|not kubernetes", note)
        )
        if claims_k8s:
            remediable["docker_pack_claims_k8s"] += 1
            findings.append(
                {
                    "kind": "docker_pack_claims_k8s",
                    "remediable": True,
                    "pack": name,
                    "note": note,
                }
            )
        docker_rows.append(
            {
                "pack": name,
                "accuracy": float(acc),
                "f1": float(f1),
                "elapsed_s": data.get("elapsed_s"),
                "num_clients": data.get("num_clients"),
                "mode": mode,
            }
        )
        findings.append(
            {
                "kind": "docker_final_ok",
                "remediable": False,
                "pack": name,
                "accuracy": float(acc),
                "f1": float(f1),
            }
        )

    baseline_md = docker / "DOCKER_FINAL3_BASELINE.md"
    if baseline_md.exists():
        findings.append({"kind": "docker_final3_baseline_present", "remediable": False})
    else:
        remediable["missing_docker_final3_baseline"] += 1
        findings.append(
            {"kind": "missing_docker_final3_baseline", "remediable": True}
        )

    # --- K8s must not be falsely claimed ---
    false_k8s = []
    for p in (ROOT / "results").rglob("*") if (ROOT / "results").exists() else []:
        if not p.is_file():
            continue
        low = p.name.lower()
        if any(
            tok in low
            for tok in (
                "eks_live",
                "k8s_live_success",
                "kubernetes_deployed",
                "helm_live",
            )
        ):
            false_k8s.append(str(p.relative_to(ROOT)))
    if false_k8s:
        remediable["undeclared_k8s_success_artefact"] += len(false_k8s)
        findings.append(
            {
                "kind": "undeclared_k8s_success_artefact",
                "remediable": True,
                "paths": false_k8s,
            }
        )
    else:
        findings.append({"kind": "no_false_k8s_success_pack", "remediable": False})

    # --- dated WONTFIX / DESIGN amendment ---
    design_txt = DESIGN.read_text(encoding="utf-8") if DESIGN.exists() else ""
    wont_txt = WONTFIX.read_text(encoding="utf-8") if WONTFIX.exists() else ""
    design_ok = DESIGN.exists() and (
        "dated deferred" in design_txt.lower()
        or "k8s deferral" in design_txt.lower()
        or "kubernetes / eks" in design_txt.lower()
    )
    wont_ok = WONTFIX.exists() and (
        "k8s" in wont_txt.lower() or "kubernetes" in wont_txt.lower()
    )
    if design_ok or wont_ok:
        findings.append(
            {
                "kind": "k8s_deferral_amendment_present",
                "remediable": False,
                "design": str(DESIGN) if design_ok else None,
                "wontfix": str(WONTFIX) if wont_ok else None,
            }
        )
    else:
        remediable["missing_k8s_deferral_amendment"] += 1
        findings.append(
            {
                "kind": "missing_k8s_deferral_amendment",
                "remediable": True,
                "expected": [str(DESIGN), str(WONTFIX)],
            }
        )

    # --- Saklani baseline framing ---
    if BASELINE.exists():
        btxt = BASELINE.read_text(encoding="utf-8")
        if re.search(r"(?i)saklani", btxt):
            findings.append({"kind": "saklani_baseline_present", "remediable": False})
        else:
            remediable["baseline_missing_saklani"] += 1
            findings.append(
                {"kind": "baseline_missing_saklani", "remediable": True}
            )
    else:
        remediable["missing_baseline_paper"] += 1
        findings.append({"kind": "missing_baseline_paper", "remediable": True})

    # --- SoT present ---
    if SOT.exists():
        stxt = SOT.read_text(encoding="utf-8")
        if "Saklani" in stxt and ("same-metrics" in stxt.lower() or "SAME METRICS" in stxt):
            findings.append({"kind": "sot_same_metrics_present", "remediable": False})
        else:
            remediable["sot_missing_same_metrics"] += 1
            findings.append(
                {"kind": "sot_missing_same_metrics", "remediable": True}
            )
    else:
        remediable["missing_sot"] += 1
        findings.append({"kind": "missing_sot", "remediable": True, "path": str(SOT)})

    # --- config / STATUS honesty ---
    if CONFIG.exists():
        cfg = CONFIG.read_text(encoding="utf-8")
        claims_k8s_tested = bool(
            re.search(
                r"(?i)kubernetes.*(tested|executed|deployed|complete)|k8s.*(tested|executed|deployed)",
                cfg,
            )
        ) and not re.search(
            r"(?i)(not|never|beyond|deferred|do not treat).{0,40}(kubernetes|k8s|docker)",
            cfg,
        )
        # Allow honest "not tested" / beyond-CA2 wording
        denies_or_scopes = bool(
            re.search(
                r"(?i)(not\s+tested|beyond-ca2|do not treat.*(kubernetes|k8s|docker)|deferred)",
                cfg,
            )
        )
        if claims_k8s_tested and not denies_or_scopes:
            remediable["config_claims_k8s_tested"] += 1
            findings.append(
                {"kind": "config_claims_k8s_tested", "remediable": True}
            )
        else:
            findings.append({"kind": "config_k8s_scope_ok", "remediable": False})
    else:
        remediable["missing_configuration_manual"] += 1
        findings.append(
            {"kind": "missing_configuration_manual", "remediable": True}
        )

    if STATUS.exists():
        st = STATUS.read_text(encoding="utf-8")
        if re.search(r"(?i)kubernetes.{0,40}(yes|done|complete|executed)", st) and not re.search(
            r"(?i)(not present|not tested|beyond-ca2|deferred)", st
        ):
            remediable["status_claims_k8s_done"] += 1
            findings.append({"kind": "status_claims_k8s_done", "remediable": True})
        else:
            findings.append({"kind": "status_k8s_honesty_ok", "remediable": False})
        # Forbid marketing Saklani 91.8 as our PoC
        if re.search(r"(?i)91\.8|91–94|91-94", st) and re.search(
            r"(?i)(our|poc|synthetic|measured).{0,40}(91|accuracy)", st
        ):
            remediable["status_markets_saklani_accuracy"] += 1
            findings.append(
                {"kind": "status_markets_saklani_accuracy", "remediable": True}
            )
    else:
        remediable["missing_status"] += 1
        findings.append({"kind": "missing_status", "remediable": True})

    remediable_total = int(sum(remediable.values()))
    disposition = (
        "FIX_REMEDIABLE"
        if remediable_total > 0
        else "DATED_WONTFIX_K8S_DEFERRED"
    )

    same_metrics = {
        "accuracy": True,
        "f1_score": True,
        "avg_communication_cost_mb_round": True,
        "baseline_saklani_contrast": (
            "Saklani PP-FL-DP-IDS reports ~91.8% acc / F1>90% on their campaign; "
            "ours retain accuracy/F1/comm under Free-Tier live lite + Docker×3 "
            "and do not clone their depth numbers"
        ),
        "live_finals_n": len(live_rows),
        "docker_finals_n": len(docker_rows),
        "k8s_executed": False,
    }

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "live_root": str(live),
        "docker_root": str(docker),
        "live_finals": live_rows,
        "docker_finals": docker_rows,
        "findings": findings,
        "remediable": dict(remediable),
        "remediable_total": remediable_total,
        "move_blocker": remediable_total > 0,
        "disposition": disposition,
        "same_metrics_snapshot": same_metrics,
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = out.with_suffix(".md")
    lines = [
        "# Nemi K8s-deferral / Docker FL remediable audit (scripted)",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Live root: `{live}`",
        f"Docker root: `{docker}`",
        "",
        "## Move gate",
        "",
        f"- **remediable_total:** {remediable_total}",
        f"- **move_blocker:** {report['move_blocker']}",
        f"- **disposition:** `{disposition}`",
        "",
        "## Same-metrics snapshot",
        "",
        f"- live finals: {len(live_rows)}/3",
        f"- docker finals: {len(docker_rows)}/3",
        f"- K8s executed: **false** (dated deferred)",
        f"- baseline contrast: {same_metrics['baseline_saklani_contrast']}",
        "",
        "## Remediable counts",
        "",
    ]
    if remediable:
        for k, v in sorted(remediable.items()):
            lines.append(f"- `{k}`: {v}")
    else:
        lines.append("- (none)")
    lines.extend(["", "## Findings", ""])
    for f in findings:
        tag = "REMEDIABLE" if f.get("remediable") else "ok"
        lines.append(f"- [{tag}] `{f.get('kind')}`")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"remediable_total": remediable_total, "disposition": disposition, "out": str(out)}, indent=2))
    return 2 if remediable_total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
