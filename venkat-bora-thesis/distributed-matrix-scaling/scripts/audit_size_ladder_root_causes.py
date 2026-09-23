#!/usr/bin/env python3
"""Scripted remediable audit for Venkat size-ladder / finals — not manual.

Verifies time finals ×3, rss_size_final ×3, size_ladder_ladder1 packs,
anti-crossover honesty (scale-up ≪ multi at every live order), destroy-after,
and remediable packaging gaps (stale config denying AWS; fabricated crossover).

Full live 200–2000 six-point EC2 ladder is dated WONTFIX when Free-Tier
subset + local ladder + DESIGN amendment are present (not remediable).

Usage (from distributed-matrix-scaling/):
  python3 scripts/audit_size_ladder_root_causes.py
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
LIVE = ROOT / "results" / "live"
THESIS = ROOT.parent
DESIGN = ROOT / "DESIGN_RATIONALE_BEYOND_CA2.md"
CONFIG = THESIS / "CONFIGURATION_MANUAL.md"
EXPECTED_TIME = ("final_1", "final_2", "final_3")
EXPECTED_RSS = ("rss_size_final_1", "rss_size_final_2", "rss_size_final_3")
EXPECTED_SIZES = (100, 250, 500)
# scale-up must be strictly faster; allow tiny float noise only
CROSSOVER_RATIO_MIN = 2.0  # multi/scale_up >= 2 → clear anti-crossover
TOL = 1e-4


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _destroy_ok(pack: Path) -> bool:
    p = pack / "destroy_confirmed.txt"
    if not p.exists():
        return False
    return "destroy_confirmed=yes" in p.read_text(encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", type=Path, default=LIVE)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    live = args.live
    ladder = live / "size_ladder_ladder1"
    out = args.out or (ladder / "analysis" / "size_ladder_audit_report.json")

    findings: list[dict] = []
    remediable: dict[str, int] = defaultdict(int)

    # --- time finals (elapsed only) ---
    time_rows: list[dict] = []
    for name in EXPECTED_TIME:
        pack = live / name
        summary = pack / "summary.json"
        if not summary.exists():
            remediable["missing_time_final"] += 1
            findings.append(
                {"kind": "missing_time_final", "remediable": True, "pack": name}
            )
            continue
        data = _load(summary)
        multi = data.get("scale_out_multi_instance") or {}
        status = multi.get("status") or multi.get("dask_array_matmul")
        elapsed = multi.get("elapsed_s")
        if status != "ok" or elapsed is None:
            remediable["time_final_multi_not_ok"] += 1
            findings.append(
                {
                    "kind": "time_final_multi_not_ok",
                    "remediable": True,
                    "pack": name,
                    "status": status,
                    "elapsed_s": elapsed,
                }
            )
        else:
            time_rows.append({"pack": name, "elapsed_s": float(elapsed)})
            findings.append(
                {
                    "kind": "time_final_ok",
                    "remediable": False,
                    "pack": name,
                    "elapsed_s": float(elapsed),
                }
            )
        if not _destroy_ok(pack):
            remediable["destroy_not_confirmed"] += 1
            findings.append(
                {"kind": "destroy_not_confirmed", "remediable": True, "pack": name}
            )
        else:
            findings.append(
                {"kind": "destroy_confirmed", "remediable": False, "pack": name}
            )

    if len(time_rows) == 3:
        findings.append(
            {
                "kind": "time_final3_complete",
                "remediable": False,
                "elapsed_range": [
                    min(r["elapsed_s"] for r in time_rows),
                    max(r["elapsed_s"] for r in time_rows),
                ],
            }
        )

    # --- RSS/CPU finals ---
    rss_rows: list[dict] = []
    for name in EXPECTED_RSS:
        pack = live / name
        summary = pack / "summary.json"
        if not summary.exists():
            remediable["missing_rss_final"] += 1
            findings.append(
                {"kind": "missing_rss_final", "remediable": True, "pack": name}
            )
            continue
        data = _load(summary)
        multi = data.get("scale_out_multi_instance") or {}
        su = data.get("scale_up") or {}
        status = multi.get("status") or multi.get("dask_array_matmul")
        elapsed = multi.get("elapsed_s")
        peak = multi.get("peak_rss_mb")
        cpu = multi.get("avg_cpu_percent")
        su_elapsed = su.get("elapsed_s")
        missing_limb = peak is None or cpu is None or elapsed is None
        if status != "ok" or missing_limb or float(peak) <= 0:
            remediable["rss_final_metrics_gap"] += 1
            findings.append(
                {
                    "kind": "rss_final_metrics_gap",
                    "remediable": True,
                    "pack": name,
                    "status": status,
                    "peak_rss_mb": peak,
                    "avg_cpu_percent": cpu,
                    "elapsed_s": elapsed,
                }
            )
        else:
            row = {
                "pack": name,
                "scale_up_elapsed_s": float(su_elapsed) if su_elapsed is not None else None,
                "multi_elapsed_s": float(elapsed),
                "multi_peak_rss_mb": float(peak),
                "multi_avg_cpu_percent": float(cpu),
            }
            rss_rows.append(row)
            findings.append(
                {"kind": "rss_final_ok", "remediable": False, **row}
            )
            # anti-crossover honesty on rss packs (n=250)
            if su_elapsed is not None and float(su_elapsed) > 0:
                ratio = float(elapsed) / float(su_elapsed)
                if ratio < CROSSOVER_RATIO_MIN:
                    remediable["rss_anti_crossover_broken"] += 1
                    findings.append(
                        {
                            "kind": "rss_anti_crossover_broken",
                            "remediable": True,
                            "pack": name,
                            "ratio_multi_over_scaleup": ratio,
                        }
                    )
                else:
                    findings.append(
                        {
                            "kind": "rss_anti_crossover_ok",
                            "remediable": False,
                            "pack": name,
                            "ratio_multi_over_scaleup": ratio,
                        }
                    )
        if not _destroy_ok(pack):
            remediable["destroy_not_confirmed"] += 1
            findings.append(
                {"kind": "destroy_not_confirmed", "remediable": True, "pack": name}
            )
        else:
            findings.append(
                {"kind": "destroy_confirmed", "remediable": False, "pack": name}
            )

    if len(rss_rows) == 3:
        findings.append(
            {
                "kind": "rss_final3_complete",
                "remediable": False,
                "multi_peak_rss_range_mb": [
                    min(r["multi_peak_rss_mb"] for r in rss_rows),
                    max(r["multi_peak_rss_mb"] for r in rss_rows),
                ],
            }
        )

    # --- size ladder ---
    campaign = ladder / "campaign_summary.json"
    ladder_rows: list[dict] = []
    if not campaign.exists():
        remediable["missing_size_ladder_campaign"] += 1
        findings.append(
            {"kind": "missing_size_ladder_campaign", "remediable": True}
        )
    else:
        camp = _load(campaign)
        sizes = list(camp.get("sizes") or [])
        rows = list(camp.get("rows") or [])
        if sizes != list(EXPECTED_SIZES) and [r.get("matrix_size") for r in rows] != list(
            EXPECTED_SIZES
        ):
            remediable["size_ladder_orders_mismatch"] += 1
            findings.append(
                {
                    "kind": "size_ladder_orders_mismatch",
                    "remediable": True,
                    "sizes": sizes,
                    "expected": list(EXPECTED_SIZES),
                }
            )
        anti = bool(camp.get("anti_crossover_retained"))
        crossover = camp.get("crossover_order_descriptive")
        if not anti or crossover is not None:
            remediable["fabricated_or_missing_anti_crossover_flag"] += 1
            findings.append(
                {
                    "kind": "fabricated_or_missing_anti_crossover_flag",
                    "remediable": True,
                    "anti_crossover_retained": anti,
                    "crossover_order_descriptive": crossover,
                }
            )
        else:
            findings.append(
                {
                    "kind": "anti_crossover_flag_ok",
                    "remediable": False,
                    "anti_crossover_retained": True,
                }
            )

        for expected_n in EXPECTED_SIZES:
            n_summary = ladder / f"n_{expected_n}" / "summary.json"
            row = next(
                (r for r in rows if int(r.get("matrix_size", -1)) == expected_n),
                None,
            )
            if row is None or not n_summary.exists():
                remediable["missing_size_ladder_order"] += 1
                findings.append(
                    {
                        "kind": "missing_size_ladder_order",
                        "remediable": True,
                        "n": expected_n,
                        "in_campaign": row is not None,
                        "n_summary": n_summary.exists(),
                    }
                )
                continue
            su_e = float(row["scale_up_elapsed_s"])
            mu_e = float(row["multi_elapsed_s"])
            mu_status = row.get("multi_status")
            mu_rss = row.get("multi_peak_rss_mb")
            mu_cpu = row.get("multi_avg_cpu_percent")
            if mu_status != "ok" or mu_rss is None or mu_cpu is None:
                remediable["size_ladder_row_incomplete"] += 1
                findings.append(
                    {
                        "kind": "size_ladder_row_incomplete",
                        "remediable": True,
                        "n": expected_n,
                        "multi_status": mu_status,
                    }
                )
                continue
            ratio = mu_e / su_e if su_e > 0 else float("inf")
            if ratio < CROSSOVER_RATIO_MIN:
                remediable["size_ladder_anti_crossover_broken"] += 1
                findings.append(
                    {
                        "kind": "size_ladder_anti_crossover_broken",
                        "remediable": True,
                        "n": expected_n,
                        "scale_up_elapsed_s": su_e,
                        "multi_elapsed_s": mu_e,
                        "ratio": ratio,
                    }
                )
            else:
                ladder_rows.append(
                    {
                        "n": expected_n,
                        "scale_up_elapsed_s": su_e,
                        "multi_elapsed_s": mu_e,
                        "multi_peak_rss_mb": float(mu_rss),
                        "multi_avg_cpu_percent": float(mu_cpu),
                        "ratio_multi_over_scaleup": ratio,
                    }
                )
                findings.append(
                    {
                        "kind": "size_ladder_order_ok",
                        "remediable": False,
                        "n": expected_n,
                        "ratio_multi_over_scaleup": ratio,
                    }
                )

            # per-order summary must agree with campaign (same metrics)
            nd = _load(n_summary)
            n_multi = nd.get("scale_out_multi_instance") or {}
            n_su = nd.get("scale_up") or {}
            if abs(float(n_multi.get("elapsed_s", -1)) - mu_e) > TOL:
                remediable["size_ladder_summary_drift"] += 1
                findings.append(
                    {
                        "kind": "size_ladder_summary_drift",
                        "remediable": True,
                        "n": expected_n,
                        "campaign_multi_elapsed_s": mu_e,
                        "n_summary_elapsed_s": n_multi.get("elapsed_s"),
                    }
                )
            if abs(float(n_su.get("elapsed_s", -1)) - su_e) > TOL:
                remediable["size_ladder_summary_drift"] += 1
                findings.append(
                    {
                        "kind": "size_ladder_summary_drift",
                        "remediable": True,
                        "n": expected_n,
                        "field": "scale_up_elapsed_s",
                    }
                )

        if not _destroy_ok(ladder):
            remediable["destroy_not_confirmed"] += 1
            findings.append(
                {
                    "kind": "destroy_not_confirmed",
                    "remediable": True,
                    "pack": "size_ladder_ladder1",
                }
            )
        else:
            findings.append(
                {
                    "kind": "destroy_confirmed",
                    "remediable": False,
                    "pack": "size_ladder_ladder1",
                }
            )

        if len(ladder_rows) == 3:
            findings.append(
                {
                    "kind": "size_ladder_complete",
                    "remediable": False,
                    "orders": list(EXPECTED_SIZES),
                    "min_ratio_multi_over_scaleup": min(
                        r["ratio_multi_over_scaleup"] for r in ladder_rows
                    ),
                }
            )

    # --- baseline MD honesty (no fabricated crossover) ---
    size_md = live / "SIZE_LADDER_BASELINE.md"
    if size_md.exists():
        txt = size_md.read_text(encoding="utf-8")
        claims_crossover_win = bool(
            re.search(
                r"(?i)crossover\s+(found|observed|at\s+n|occurs)|distribution\s+beats|scale-out\s+faster",
                txt,
            )
        ) and "anti-crossover" not in txt.lower()
        # positive win claim without anti-crossover language
        if claims_crossover_win or (
            re.search(r"(?i)\bcrossover\b", txt)
            and "no crossover" not in txt.lower()
            and "anti-crossover" not in txt.lower()
        ):
            remediable["fabricated_crossover_in_baseline_md"] += 1
            findings.append(
                {
                    "kind": "fabricated_crossover_in_baseline_md",
                    "remediable": True,
                    "path": str(size_md),
                }
            )
        elif "anti-crossover" in txt.lower() or "no crossover" in txt.lower():
            findings.append(
                {
                    "kind": "size_ladder_baseline_anti_crossover_honest",
                    "remediable": False,
                }
            )
        else:
            remediable["size_ladder_baseline_missing_anti_crossover"] += 1
            findings.append(
                {
                    "kind": "size_ladder_baseline_missing_anti_crossover",
                    "remediable": True,
                }
            )
    else:
        remediable["missing_size_ladder_baseline_md"] += 1
        findings.append(
            {"kind": "missing_size_ladder_baseline_md", "remediable": True}
        )

    # --- config must not deny live AWS once packs exist ---
    if CONFIG.exists():
        cfg = CONFIG.read_text(encoding="utf-8")
        denies_aws = bool(
            re.search(
                r"(?i)AWS EC2 is not configured or executed|treat all published numbers as \*\*local proxy evidence only\*\*|Until then, treat all published",
                cfg,
            )
        )
        if denies_aws and (live / "size_ladder_ladder1").exists():
            remediable["stale_config_denies_live_aws"] += 1
            findings.append(
                {
                    "kind": "stale_config_denies_live_aws",
                    "remediable": True,
                    "path": str(CONFIG),
                    "detail": "CONFIGURATION_MANUAL still claims local-only while live packs exist",
                }
            )
        else:
            findings.append(
                {"kind": "config_aws_scope_ok", "remediable": False, "path": str(CONFIG)}
            )
    else:
        remediable["missing_configuration_manual"] += 1
        findings.append(
            {"kind": "missing_configuration_manual", "remediable": True}
        )

    # --- full live 200–2000: WONTFIX if design amendment present ---
    design_txt = DESIGN.read_text(encoding="utf-8") if DESIGN.exists() else ""
    design_ok = DESIGN.exists() and (
        "200–2000" in design_txt or "200-2000" in design_txt
    ) and (
        "not required" in design_txt.lower()
        or "free-tier subset" in design_txt.lower()
        or "disclosed" in design_txt.lower()
    )
    full_live_markers = []
    if live.exists():
        for p in live.rglob("*"):
            if not p.is_file():
                continue
            low = p.name.lower()
            if any(
                tok in low
                for tok in (
                    "full_200_2000",
                    "six_point_live",
                    "live_order_2000",
                    "crossover_found",
                )
            ):
                full_live_markers.append(str(p.relative_to(ROOT)))
    if full_live_markers:
        remediable["undeclared_full_live_ladder_artefact"] += len(full_live_markers)
        findings.append(
            {
                "kind": "undeclared_full_live_ladder_artefact",
                "remediable": True,
                "paths": full_live_markers,
                "detail": "full live 200–2000 amended out — remove or reclassify",
            }
        )
    elif design_ok:
        findings.append(
            {
                "kind": "full_live_200_2000_absent_as_amended",
                "remediable": False,
                "amendment": str(DESIGN),
            }
        )
    else:
        remediable["missing_full_ladder_scope_amendment"] += 1
        findings.append(
            {
                "kind": "missing_full_ladder_scope_amendment",
                "remediable": True,
                "path": str(DESIGN),
            }
        )

    remediable_total = int(sum(remediable.values()))
    disposition = (
        "FIX_REMEDIABLE"
        if remediable_total > 0
        else "DATED_WONTFIX_FULL_LIVE_LADDER_AMENDED"
    )

    same_metrics = {
        "elapsed_s": True,
        "peak_rss_mb": len(rss_rows) == 3 and len(ladder_rows) == 3,
        "avg_cpu_percent": len(rss_rows) == 3 and len(ladder_rows) == 3,
        "baseline_sabir_contrast": (
            "Sabir multi-threaded LU/time on shared memory; "
            "ours add matched-vCPU scale-out + RSS/CPU + growing-order limb"
        ),
        "anti_crossover_retained": len(ladder_rows) == 3
        and all(r["ratio_multi_over_scaleup"] >= CROSSOVER_RATIO_MIN for r in ladder_rows),
    }

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "live_root": str(live),
        "time_finals": time_rows,
        "rss_finals": rss_rows,
        "size_ladder_rows": ladder_rows,
        "expected_sizes": list(EXPECTED_SIZES),
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
        "# Venkat size-ladder / finals remediable audit (scripted)",
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
        f"- time finals ok: {len(time_rows)}/3",
        f"- rss finals ok: {len(rss_rows)}/3",
        f"- size ladder orders ok: {len(ladder_rows)}/3 ({list(EXPECTED_SIZES)})",
        f"- anti-crossover: {same_metrics['anti_crossover_retained']}",
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
    for f in findings:
        lines.append(f"- `{f['kind']}` remediable={f.get('remediable')}")
    lines.extend(
        [
            "",
            "```bash",
            "cd distributed-matrix-scaling",
            "python3 scripts/audit_size_ladder_root_causes.py",
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
