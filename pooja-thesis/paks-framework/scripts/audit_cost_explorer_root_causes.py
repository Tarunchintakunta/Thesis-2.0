#!/usr/bin/env python3
"""Scripted remediable audit for Pooja Cost Explorer soft limb — not manual.

Verifies:
  - live k3s final_1–3 HPA vs PAKS with destroy_confirmed
  - final3_latency_summary same-metrics (scale latency mean/p50)
  - TRACE prediction: LSTM MAE worse than persistence (retained negative)
  - cost = LIST_PRICE / SIMULATED ($/pod-hour); Cost Explorer not claimed measured
  - dated WONTFIX for Cost Explorer; HPA baseline binding
  - config + STATUS honesty

EXIT 2 if remediable_total > 0 (move_blocker). EXIT 0 when clean
(disposition DATED_WONTFIX_COST_EXPLORER).

Usage (from paks-framework/):
  python3 scripts/audit_cost_explorer_root_causes.py
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
LIVE = ROOT / "results" / "live"
RESULTS = ROOT / "results"
DESIGN = THESIS / "DESIGN_RATIONALE_BEYOND_CA2.md"
WONTFIX = THESIS / "DATED_WONTFIX_N_Pooja_2026-09-23.md"
CONFIG = ROOT / "docs" / "CONFIGURATION_MANUAL.md"
STATUS = THESIS / "STATUS.md"
BASELINE = THESIS / "baseline_papers" / "BASELINE_PAPER.md"
SOT = THESIS / "CA2_PROPOSED_VS_ARTEFACT.md"
METRICS_PY = ROOT / "src" / "eval" / "metrics.py"
PRED_CSV = RESULTS / "formal_prediction_metrics.csv"
EXPECTED = ("final_1", "final_2", "final_3")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def _destroy_ok(pack: Path) -> bool:
    p = pack / "aws_destroy_verify.json"
    if not p.exists():
        return False
    data = _load(p)
    return bool(data.get("destroy_confirmed"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", type=Path, default=LIVE)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    live = args.live
    out = args.out or (live / "analysis" / "cost_explorer_audit_report.json")

    findings: list[dict] = []
    remediable: dict[str, int] = defaultdict(int)

    # --- live finals ×3 ---
    live_rows: list[dict] = []
    for name in EXPECTED:
        pack = live / name
        formal = pack / "formal_k8s_live_aws.json"
        if not formal.exists():
            remediable["missing_live_final"] += 1
            findings.append(
                {"kind": "missing_live_final", "remediable": True, "pack": name}
            )
            continue
        data = _load(formal)
        hpa = data.get("hpa_metrics") or {}
        paks = data.get("paks_metrics") or {}
        evidence = data.get("evidence") or {}
        row = {
            "pack": name,
            "hpa_cost_usd": hpa.get("cost_usd") if isinstance(hpa, dict) else None,
            "paks_cost_usd": paks.get("cost_usd") if isinstance(paks, dict) else None,
            "evidence_cost": evidence.get("cost"),
            "live_apply": data.get("live_apply"),
            "aws_deployed": data.get("aws_deployed"),
        }
        if not data.get("live_apply") or not data.get("aws_deployed"):
            remediable["live_final_not_live"] += 1
            findings.append(
                {"kind": "live_final_not_live", "remediable": True, "pack": name}
            )
        else:
            live_rows.append(row)
            findings.append(
                {"kind": "live_final_ok", "remediable": False, "pack": name, **row}
            )
        if evidence.get("cost") not in {"SIMULATED", "LIST_PRICE", "list_price"}:
            remediable["live_cost_not_list_price_simulated"] += 1
            findings.append(
                {
                    "kind": "live_cost_not_list_price_simulated",
                    "remediable": True,
                    "pack": name,
                    "evidence_cost": evidence.get("cost"),
                }
            )
        else:
            findings.append(
                {
                    "kind": "live_cost_list_price_simulated_ok",
                    "remediable": False,
                    "pack": name,
                }
            )
        if not _destroy_ok(pack):
            remediable["destroy_not_confirmed"] += 1
            findings.append(
                {"kind": "destroy_not_confirmed", "remediable": True, "pack": name}
            )
        else:
            findings.append(
                {"kind": "destroy_ok", "remediable": False, "pack": name}
            )

    # --- latency summary ---
    lat_path = live / "final3_latency_summary.json"
    latency_rows: list[dict] = []
    if not lat_path.exists():
        remediable["missing_final3_latency_summary"] += 1
        findings.append(
            {"kind": "missing_final3_latency_summary", "remediable": True}
        )
    else:
        rows = json.loads(lat_path.read_text(encoding="utf-8"))
        if not isinstance(rows, list) or len(rows) < 3:
            remediable["latency_summary_incomplete"] += 1
            findings.append(
                {
                    "kind": "latency_summary_incomplete",
                    "remediable": True,
                    "n": len(rows) if isinstance(rows, list) else None,
                }
            )
        else:
            for r in rows:
                for col in (
                    "hpa_lat_mean",
                    "paks_lat_mean",
                    "hpa_p50",
                    "paks_p50",
                    "n_steps",
                ):
                    if _f(r.get(col)) is None:
                        remediable["latency_metric_hole"] += 1
                        findings.append(
                            {
                                "kind": "latency_metric_hole",
                                "remediable": True,
                                "round": r.get("round"),
                                "col": col,
                            }
                        )
                latency_rows.append(r)
                if not r.get("destroy_confirmed"):
                    remediable["latency_destroy_flag_false"] += 1
                    findings.append(
                        {
                            "kind": "latency_destroy_flag_false",
                            "remediable": True,
                            "round": r.get("round"),
                        }
                    )
            findings.append(
                {
                    "kind": "final3_latency_summary_ok",
                    "remediable": False,
                    "n": len(latency_rows),
                }
            )

    baseline_md = live / "FINAL3_BASELINE.md"
    if baseline_md.exists() and re.search(
        r"(?i)hpa", baseline_md.read_text(encoding="utf-8")
    ):
        findings.append({"kind": "final3_baseline_hpa_present", "remediable": False})
    else:
        remediable["missing_final3_baseline_hpa"] += 1
        findings.append(
            {"kind": "missing_final3_baseline_hpa", "remediable": True}
        )

    # --- LSTM < persistence (retained negative) ---
    pred_rows: list[dict] = []
    if not PRED_CSV.exists():
        remediable["missing_prediction_metrics"] += 1
        findings.append(
            {"kind": "missing_prediction_metrics", "remediable": True}
        )
    else:
        with PRED_CSV.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                mae = _f(r.get("mae_test"))
                persist = _f(r.get("mae_persistence_test"))
                if mae is None or persist is None:
                    remediable["prediction_metric_hole"] += 1
                    findings.append(
                        {
                            "kind": "prediction_metric_hole",
                            "remediable": True,
                            "dataset": r.get("dataset"),
                        }
                    )
                    continue
                worse = mae > persist
                pred_rows.append(
                    {
                        "dataset": r.get("dataset"),
                        "mae_test": mae,
                        "mae_persistence_test": persist,
                        "lstm_worse_than_persistence": worse,
                    }
                )
                if not worse:
                    remediable["lstm_not_worse_than_persistence_claim_drift"] += 1
                    findings.append(
                        {
                            "kind": "lstm_not_worse_than_persistence_claim_drift",
                            "remediable": True,
                            "dataset": r.get("dataset"),
                            "detail": "SoT/STATUS claim LSTM<persistence; evidence disagrees — fix claim or re-run",
                        }
                    )
                else:
                    findings.append(
                        {
                            "kind": "lstm_worse_than_persistence_ok",
                            "remediable": False,
                            "dataset": r.get("dataset"),
                            "mae_test": mae,
                            "mae_persistence_test": persist,
                        }
                    )

    # --- LIST_PRICE constant in metrics.py ---
    if METRICS_PY.exists():
        mtxt = METRICS_PY.read_text(encoding="utf-8")
        if "USD_PER_POD_HOUR" in mtxt and re.search(r"0\.04", mtxt):
            findings.append(
                {"kind": "list_price_constant_present", "remediable": False}
            )
        else:
            remediable["missing_list_price_constant"] += 1
            findings.append(
                {"kind": "missing_list_price_constant", "remediable": True}
            )
        if re.search(r"(?i)cost.?explorer", mtxt) and re.search(
            r"(?i)(measured|live bill|get.?cost.?and.?usage)", mtxt
        ):
            remediable["metrics_claims_cost_explorer_measured"] += 1
            findings.append(
                {
                    "kind": "metrics_claims_cost_explorer_measured",
                    "remediable": True,
                }
            )
    else:
        remediable["missing_metrics_py"] += 1
        findings.append({"kind": "missing_metrics_py", "remediable": True})

    # --- no Cost Explorer success artefact ---
    # Exclude this audit's own reports and dated-WONTFIX docs (name contains cost_explorer).
    ce_hits = []
    skip_parts = {"analysis", "docs"}
    skip_name_substrings = (
        "audit_report",
        "dated_wontfix",
        "wontfix",
        "audit_cost_explorer",
    )
    for p in RESULTS.rglob("*") if RESULTS.exists() else []:
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT)
        if any(part in skip_parts for part in rel.parts):
            continue
        low = p.name.lower()
        if any(s in low for s in skip_name_substrings):
            continue
        if any(
            tok in low
            for tok in (
                "cost_explorer",
                "getcostandusage",
                "ce_bill_validated",
                "billing_linked_cost_live",
            )
        ):
            ce_hits.append(str(rel))
    if ce_hits:
        remediable["undeclared_cost_explorer_artefact"] += len(ce_hits)
        findings.append(
            {
                "kind": "undeclared_cost_explorer_artefact",
                "remediable": True,
                "paths": ce_hits,
            }
        )
    else:
        findings.append(
            {"kind": "no_cost_explorer_success_pack", "remediable": False}
        )

    # --- dated WONTFIX / DESIGN ---
    design_txt = DESIGN.read_text(encoding="utf-8") if DESIGN.exists() else ""
    wont_txt = WONTFIX.read_text(encoding="utf-8") if WONTFIX.exists() else ""
    design_ok = DESIGN.exists() and (
        "cost explorer" in design_txt.lower()
        or "billing-linked cost" in design_txt.lower()
        or "$/pod-hour" in design_txt.lower()
        or "assumed" in design_txt.lower()
    )
    wont_ok = WONTFIX.exists() and (
        "cost explorer" in wont_txt.lower() or "list_price" in wont_txt.lower()
    )
    if design_ok or wont_ok:
        findings.append(
            {
                "kind": "cost_explorer_amendment_present",
                "remediable": False,
                "design": str(DESIGN) if design_ok else None,
                "wontfix": str(WONTFIX) if wont_ok else None,
            }
        )
    else:
        remediable["missing_cost_explorer_amendment"] += 1
        findings.append(
            {
                "kind": "missing_cost_explorer_amendment",
                "remediable": True,
                "expected": [str(DESIGN), str(WONTFIX)],
            }
        )

    # --- HPA baseline ---
    if BASELINE.exists():
        btxt = BASELINE.read_text(encoding="utf-8")
        if re.search(r"(?i)horizontal pod autoscaler|\bhpa\b", btxt):
            findings.append({"kind": "hpa_baseline_present", "remediable": False})
        else:
            remediable["baseline_missing_hpa"] += 1
            findings.append({"kind": "baseline_missing_hpa", "remediable": True})
    else:
        remediable["missing_baseline_paper"] += 1
        findings.append({"kind": "missing_baseline_paper", "remediable": True})

    # --- SoT ---
    if SOT.exists():
        stxt = SOT.read_text(encoding="utf-8")
        ok = (
            ("SAME METRICS" in stxt or "same-metrics" in stxt.lower())
            and re.search(r"(?i)\bhpa\b", stxt)
            and (
                "LIST_PRICE" in stxt
                or "list-price" in stxt.lower()
                or "$0.04" in stxt
                or "pod-hour" in stxt.lower()
            )
        )
        if ok:
            findings.append({"kind": "sot_same_metrics_present", "remediable": False})
        else:
            remediable["sot_missing_same_metrics"] += 1
            findings.append(
                {"kind": "sot_missing_same_metrics", "remediable": True}
            )
    else:
        remediable["missing_sot"] += 1
        findings.append({"kind": "missing_sot", "remediable": True, "path": str(SOT)})

    # --- config / STATUS ---
    if CONFIG.exists():
        cfg = CONFIG.read_text(encoding="utf-8")
        has_list = bool(
            re.search(
                r"(?i)(list.?price|usd_per_pod_hour|\$0\.04|pod-hour|SIMULATED)",
                cfg,
            )
        )
        claims_ce = bool(
            re.search(
                r"(?i)cost explorer.{0,40}(measured|validated|live bill|closed)",
                cfg,
            )
        )
        if not has_list:
            remediable["config_missing_list_price_disclosure"] += 1
            findings.append(
                {
                    "kind": "config_missing_list_price_disclosure",
                    "remediable": True,
                }
            )
        elif claims_ce:
            remediable["config_claims_cost_explorer_measured"] += 1
            findings.append(
                {
                    "kind": "config_claims_cost_explorer_measured",
                    "remediable": True,
                }
            )
        else:
            findings.append(
                {"kind": "config_cost_disclosure_ok", "remediable": False}
            )
    else:
        remediable["missing_configuration_manual"] += 1
        findings.append(
            {"kind": "missing_configuration_manual", "remediable": True}
        )

    if STATUS.exists():
        st = STATUS.read_text(encoding="utf-8")
        if re.search(
            r"(?i)cost explorer.{0,30}(done|measured|validated|yes)", st
        ) and not re.search(r"(?i)(not|simulated|assumed|scoped)", st):
            remediable["status_claims_cost_explorer_done"] += 1
            findings.append(
                {
                    "kind": "status_claims_cost_explorer_done",
                    "remediable": True,
                }
            )
        else:
            findings.append(
                {"kind": "status_cost_honesty_ok", "remediable": False}
            )
        if not re.search(r"(?i)persistence", st):
            remediable["status_missing_lstm_persistence_negative"] += 1
            findings.append(
                {
                    "kind": "status_missing_lstm_persistence_negative",
                    "remediable": True,
                }
            )
        else:
            findings.append(
                {
                    "kind": "status_lstm_persistence_negative_ok",
                    "remediable": False,
                }
            )
    else:
        remediable["missing_status"] += 1
        findings.append({"kind": "missing_status", "remediable": True})

    remediable_total = int(sum(remediable.values()))
    disposition = (
        "FIX_REMEDIABLE"
        if remediable_total > 0
        else "DATED_WONTFIX_COST_EXPLORER"
    )

    same_metrics = {
        "scaling_latency_mean_s": len(latency_rows) == 3,
        "scaling_latency_p50_s": len(latency_rows) == 3,
        "mae_rmse_vs_persistence": len(pred_rows) >= 2
        and all(r["lstm_worse_than_persistence"] for r in pred_rows),
        "cost_usd_list_price": True,
        "baseline_hpa_contrast": (
            "Binding baseline = Kubernetes HPA (reactive); "
            "ours add predictive PAKS Scale + TRACE MAE/RMSE + LIST_PRICE $/pod-hour "
            "(Cost Explorer bill validation dated WONTFIX)"
        ),
        "live_finals_n": len(live_rows),
    }

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "live_root": str(live),
        "live_finals": live_rows,
        "latency_rows": latency_rows,
        "prediction_rows": pred_rows,
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
        "# Pooja Cost Explorer / LIST_PRICE remediable audit (scripted)",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Live root: `{live}`",
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
        f"- latency rows: {len(latency_rows)}/3",
        f"- prediction rows (LSTM>persistence): {len(pred_rows)}",
        f"- cost: LIST_PRICE / SIMULATED ($0.04/pod-hour)",
        f"- baseline contrast: {same_metrics['baseline_hpa_contrast']}",
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

    print(
        json.dumps(
            {
                "remediable_total": remediable_total,
                "disposition": disposition,
                "out": str(out),
            },
            indent=2,
        )
    )
    return 2 if remediable_total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
