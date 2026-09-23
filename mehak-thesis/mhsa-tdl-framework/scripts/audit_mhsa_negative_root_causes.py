#!/usr/bin/env python3
"""Scripted remediable audit for Mehak MHSA-vs-Aldomi/RF negative result — not manual.

Verifies:
  - final_1–3 + hard_verify_1–5 packs with Acc/P/R/F1/AUC
  - mhsa_beats_aldomi_acc=false and mhsa_beats_rf_acc=false on every hv pack
  - Aldomi binding baseline paper (not Thapliyal as CA2 baseline)
  - net-bytes dated WONTFIX + CHANNEL_HONESTY (net≠bytes)
  - SoT present with same-metrics Acc/P/R/F1/AUC

EXIT 2 if remediable_total > 0 (move_blocker). EXIT 0 when clean.

Usage (from mhsa-tdl-framework/):
  python3 scripts/audit_mhsa_negative_root_causes.py
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
GCT = ROOT / "results" / "gct"
EXPECTED_FINALS = ("final_1", "final_2", "final_3")
EXPECTED_HV = tuple(f"hard_verify_{i}" for i in range(1, 6))
REQUIRED_METRICS = ("Accuracy", "Precision", "Recall", "Macro-F1", "ROC-AUC")


def _load_summary(pack: Path) -> dict | None:
    p = pack / "hard_verify_summary.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def _csv_means(pack: Path) -> dict[str, dict[str, float]] | None:
    csv_path = pack / "results_summary.csv"
    if not csv_path.exists():
        return None
    try:
        import pandas as pd

        s = pd.read_csv(csv_path, index_col=0, header=[0, 1])

        def m(model: str, col: str) -> float:
            return float(s.loc[model, (col, "mean")])

        out = {}
        for model in ("MHSA-Fused", "Aldomi GRU-RF", "RF (classical)"):
            out[model] = {col: m(model, col) for col in REQUIRED_METRICS}
            if ("Fail-F1", "mean") in s.columns or ("Fail-F1", "mean") in getattr(
                s.columns, "values", []
            ):
                try:
                    out[model]["Fail-F1"] = m(model, "Fail-F1")
                except Exception:
                    pass
        return out
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gct", type=Path, default=GCT)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    gct = args.gct
    out = args.out or (gct / "analysis" / "mhsa_negative_audit_report.json")

    findings: list[dict] = []
    remediable: dict[str, int] = defaultdict(int)

    # --- finals ---
    final_snap: dict[str, dict] = {}
    for name in EXPECTED_FINALS:
        pack = gct / name
        means = _csv_means(pack)
        if means is None:
            remediable["missing_final_pack"] += 1
            findings.append(
                {"kind": "missing_final_pack", "remediable": True, "pack": name}
            )
            continue
        missing_m = [
            m
            for m, cols in means.items()
            for c in REQUIRED_METRICS
            if cols.get(c) is None
        ]
        if missing_m:
            remediable["final_metric_hole"] += 1
            findings.append(
                {
                    "kind": "final_metric_hole",
                    "remediable": True,
                    "pack": name,
                    "missing": missing_m,
                }
            )
        else:
            final_snap[name] = means
            findings.append({"kind": "final_pack_ok", "remediable": False, "pack": name})

    # --- hard_verify 1–5 ---
    hv_ok = 0
    for name in EXPECTED_HV:
        pack = gct / name
        summary = _load_summary(pack)
        means = _csv_means(pack)
        if summary is None and means is None and not (pack / "run.log").exists():
            remediable["missing_hard_verify"] += 1
            findings.append(
                {"kind": "missing_hard_verify", "remediable": True, "pack": name}
            )
            continue
        if summary is None and means is not None:
            # synthesize check fields from CSV
            mhsa, ald, rf = (
                means["MHSA-Fused"],
                means["Aldomi GRU-RF"],
                means["RF (classical)"],
            )
            summary = {
                "mhsa_fused": mhsa,
                "aldomi_gru_rf": ald,
                "rf": rf,
                "mhsa_beats_aldomi_acc": mhsa["Accuracy"] > ald["Accuracy"],
                "mhsa_beats_rf_acc": mhsa["Accuracy"] > rf["Accuracy"],
                "same_metrics_present": True,
            }
        if summary is None:
            remediable["missing_hard_verify_summary"] += 1
            findings.append(
                {
                    "kind": "missing_hard_verify_summary",
                    "remediable": True,
                    "pack": name,
                    "hint": "python3 scripts/write_hard_verify_summary.py " + name,
                }
            )
            continue

        if not summary.get("same_metrics_present", False):
            remediable["hv_same_metrics_missing"] += 1
            findings.append(
                {"kind": "hv_same_metrics_missing", "remediable": True, "pack": name}
            )

        beats_a = bool(summary.get("mhsa_beats_aldomi_acc"))
        beats_r = bool(summary.get("mhsa_beats_rf_acc"))
        if beats_a or beats_r:
            remediable["fabricated_mhsa_win"] += 1
            findings.append(
                {
                    "kind": "fabricated_mhsa_win",
                    "remediable": True,
                    "pack": name,
                    "mhsa_beats_aldomi_acc": beats_a,
                    "mhsa_beats_rf_acc": beats_r,
                }
            )
        else:
            hv_ok += 1
            findings.append(
                {
                    "kind": "hv_negative_ok",
                    "remediable": False,
                    "pack": name,
                    "mhsa_acc": (summary.get("mhsa_fused") or {}).get("Accuracy"),
                    "aldomi_acc": (summary.get("aldomi_gru_rf") or {}).get("Accuracy"),
                    "rf_acc": (summary.get("rf") or {}).get("Accuracy"),
                }
            )

    if hv_ok < 5:
        # already counted per-pack; ensure blocker if short
        findings.append(
            {
                "kind": "hard_verify_count",
                "remediable": hv_ok < 5,
                "ok_packs": hv_ok,
                "expected": 5,
            }
        )
        if hv_ok < 5 and remediable["missing_hard_verify"] == 0:
            remediable["hard_verify_incomplete"] += max(0, 5 - hv_ok)

    # --- baseline Aldomi ---
    baseline = THESIS / "baseline_papers" / "BASELINE_PAPER.md"
    if not baseline.exists():
        remediable["missing_baseline_paper"] += 1
        findings.append({"kind": "missing_baseline_paper", "remediable": True})
    else:
        text = baseline.read_text(encoding="utf-8")
        aldomi_ok = bool(re.search(r"Aldomi", text, re.I))
        thapliyal_as_binding = bool(
            re.search(r"(?i)binding.*Thapliyal|Thapliyal.*binding|Citation:.*Thapliyal", text)
        ) and not aldomi_ok
        # Fail if Thapliyal is still the sole Citation baseline
        cite_thap = bool(re.search(r"(?m)^\*\*Citation:\*\*.*Thapliyal", text))
        cite_ald = bool(re.search(r"(?m)^\*\*Citation:\*\*.*Aldomi", text))
        if cite_thap and not cite_ald:
            remediable["baseline_still_thapliyal"] += 1
            findings.append(
                {
                    "kind": "baseline_still_thapliyal",
                    "remediable": True,
                    "path": str(baseline.relative_to(THESIS.parent)),
                }
            )
        elif not aldomi_ok or thapliyal_as_binding:
            remediable["baseline_not_aldomi"] += 1
            findings.append({"kind": "baseline_not_aldomi", "remediable": True})
        else:
            findings.append({"kind": "baseline_aldomi_ok", "remediable": False})

    # --- net-bytes WONTFIX ---
    honesty = ROOT / "data" / "gct" / "CHANNEL_HONESTY.md"
    wontfix = list(THESIS.glob("DATED_WONTFIX*M2*")) + list(
        THESIS.glob("**/DATED_WONTFIX*M2*")
    )
    wontfix += list(ROOT.glob("**/DATED_WONTFIX*net*"))
    wontfix += list(THESIS.glob("DATED_WONTFIX_M2_M3*.md"))
    if not honesty.exists():
        remediable["missing_channel_honesty"] += 1
        findings.append({"kind": "missing_channel_honesty", "remediable": True})
    else:
        htxt = honesty.read_text(encoding="utf-8")
        if "no network-byte" not in htxt.lower() and "not" not in htxt.lower():
            remediable["channel_honesty_weak"] += 1
            findings.append({"kind": "channel_honesty_weak", "remediable": True})
        else:
            findings.append({"kind": "channel_honesty_ok", "remediable": False})

    if not wontfix:
        remediable["missing_netbytes_wontfix"] += 1
        findings.append(
            {
                "kind": "missing_netbytes_wontfix",
                "remediable": True,
                "hint": "DATED_WONTFIX_M2_M3_2026-09-23.md",
            }
        )
    else:
        findings.append(
            {
                "kind": "netbytes_wontfix_ok",
                "remediable": False,
                "paths": [str(p) for p in wontfix],
            }
        )

    # gct_load_meta net flag
    meta_paths = [
        gct / "gct_load_meta.json",
        gct / "final_1" / "gct_load_meta.json",
        gct / "initial_eval_1" / "gct_load_meta.json",
    ]
    meta_ok = False
    for mp in meta_paths:
        if not mp.exists():
            continue
        meta = json.loads(mp.read_text(encoding="utf-8"))
        if meta.get("net_channel_is_network_bytes") is False:
            meta_ok = True
            findings.append(
                {
                    "kind": "net_channel_flag_ok",
                    "remediable": False,
                    "path": str(mp.relative_to(ROOT)),
                }
            )
            break
    if not meta_ok:
        remediable["net_channel_flag_missing"] += 1
        findings.append({"kind": "net_channel_flag_missing", "remediable": True})

    # --- SoT ---
    sot = THESIS / "CA2_PROPOSED_VS_ARTEFACT.md"
    if not sot.exists():
        remediable["missing_sot"] += 1
        findings.append({"kind": "missing_sot", "remediable": True})
    else:
        st = sot.read_text(encoding="utf-8")
        need = ["Accuracy", "Precision", "Recall", "Aldomi", "MHSA"]
        # F1 / AUC variants
        has_f1 = bool(re.search(r"F1|Macro-F1", st))
        has_auc = bool(re.search(r"AUC|ROC-AUC", st))
        missing = [k for k in need if k not in st]
        if missing or not has_f1 or not has_auc:
            remediable["sot_same_metrics_incomplete"] += 1
            findings.append(
                {
                    "kind": "sot_same_metrics_incomplete",
                    "remediable": True,
                    "missing": missing,
                    "has_f1": has_f1,
                    "has_auc": has_auc,
                }
            )
        else:
            findings.append({"kind": "sot_ok", "remediable": False})

    # config manual (Outstanding cell)
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

    # fabricated MHSA win in STATUS
    for stamp in (THESIS / "STATUS.md", ROOT / "STATUS.md", gct / "FINAL3_BASELINE.md"):
        if not stamp.exists():
            continue
        t = stamp.read_text(encoding="utf-8")
        if re.search(r"(?i)MHSA.*(beats|outperforms|wins).*Aldomi", t) or re.search(
            r"(?i)MHSA.*(beats|outperforms).*RF", t
        ):
            remediable["status_claims_mhsa_win"] += 1
            findings.append(
                {
                    "kind": "status_claims_mhsa_win",
                    "remediable": True,
                    "path": str(stamp),
                }
            )

    remediable_total = int(sum(remediable.values()))
    # Same-metrics snapshot for SoT from final_1 or gct root
    snap_src = final_snap.get("final_1") or _csv_means(gct) or {}
    disposition = (
        "FIX_REMEDIABLE" if remediable_total > 0 else "DATED_WONTFIX_NET_BYTES_SCHEMA"
    )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "thesis": "mehak",
        "artefact": "mhsa-tdl-framework",
        "findings": findings,
        "remediable": dict(remediable),
        "remediable_total": remediable_total,
        "move_blocker": remediable_total > 0,
        "disposition": disposition,
        "hard_verify_negative_ok": hv_ok,
        "same_metrics_snapshot": {
            model: snap_src.get(model, {})
            for model in ("MHSA-Fused", "Aldomi GRU-RF", "RF (classical)")
        },
        "n_mehak_close": disposition.startswith("DATED_WONTFIX"),
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = out.with_suffix(".md")
    lines = [
        "# Mehak MHSA-negative remediable audit",
        "",
        f"- generated_at: `{report['generated_at']}`",
        f"- remediable_total: **{remediable_total}**",
        f"- move_blocker: `{report['move_blocker']}`",
        f"- disposition: `{disposition}`",
        f"- hard_verify packs with mhsa_beats_*=false: **{hv_ok}/5**",
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

    print(json.dumps({"remediable_total": remediable_total, "disposition": disposition, "out": str(out)}, indent=2))
    return 2 if remediable_total > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
