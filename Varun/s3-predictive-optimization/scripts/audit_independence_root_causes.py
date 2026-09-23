#!/usr/bin/env python3
"""Scripted remediable audit for Varun r4+r5 independence — not manual.

Verifies confirmatory live packs evaluation_r4 / evaluation_r5:
  - distinct raw_costs SHAs (independence vs each other and vs archival r1–r3)
  - rebuilt_from_run_log=false
  - meets_ca2_two_of_three=true with consistent Wilcoxon flags
  - destroy evidence (empty terraform state + destroy_after / note)
  - allocation-accuracy limb honesty (offline oracle vs Lifecycle)

EXIT 2 if remediable_total > 0 (MOVE blocked). Intentional weak alloc-acc
is DATED_WONTFIX when evidenced and not remediable in-code.

Usage (from s3-predictive-optimization/):
  python3 scripts/audit_independence_root_causes.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "results" / "live"
TFSTATE = ROOT / "terraform" / "terraform.tfstate"
WONTFIX_ALLOC = LIVE / "analysis" / "DATED_WONTFIX_N_Varun_alloc_acc_2026-09-23.md"
WORKLOADS = ("static_archival", "mixed_access", "high_churn")
ARCHIVAL = (1, 2, 3)
INDEP = (4, 5)
# Expected shasums from FINAL3_NOTE (binding confirmatory hashes)
EXPECTED_SHA = {
    4: "7babd39cee64656b34bc876a34b645e2b460c3a5",
    5: "53bec5e526389e479ef524c67be2a7dafe65cfd5",
}
ARCHIVAL_SHA = "dbc3c0f1d944b644a052e641d53195d6f9a1a505"


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha1(path: Path) -> str:
    h = hashlib.sha1()
    h.update(path.read_bytes())
    return h.hexdigest()


def _wilcoxon_greater_zero(diffs: list[float]) -> dict:
    """Exact Wilcoxon signed-rank for paired diffs (two-sided p via scipy if present).

    Falls back to counting positive/zero and matching summary flags without
    requiring scipy for the remediable gate (p-value cross-check is best-effort).
    """
    nonzero = [d for d in diffs if d != 0.0]
    n = len(nonzero)
    n_pos = sum(1 for d in nonzero if d > 0)
    n_neg = n - n_pos
    out = {
        "n": len(diffs),
        "n_nonzero": n,
        "n_pos": n_pos,
        "n_neg": n_neg,
        "mean_diff": float(sum(diffs) / len(diffs)) if diffs else float("nan"),
        "all_nonneg_or_tie": n_neg == 0,
    }
    try:
        from scipy.stats import wilcoxon  # type: ignore

        if n >= 1 and n_pos != n_neg:
            stat, p = wilcoxon(diffs, alternative="greater", zero_method="wilcox")
            out["statistic"] = float(stat)
            out["p_value"] = float(p)
        elif n >= 1:
            out["statistic"] = float("nan")
            out["p_value"] = 1.0
        else:
            out["statistic"] = float("nan")
            out["p_value"] = float("nan")
    except Exception as exc:  # noqa: BLE001
        out["scipy_error"] = str(exc)
    return out


def _pack_paths(eval_id: int) -> tuple[Path, Path]:
    d = LIVE / f"evaluation_r{eval_id}"
    return d / "summary.json", d / "raw_costs.json"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out",
        type=Path,
        default=LIVE / "analysis" / "independence_audit_report.json",
    )
    args = ap.parse_args()
    out: Path = args.out

    findings: list[dict] = []
    remediable: dict[str, int] = defaultdict(int)
    sha_by_eval: dict[int, str] = {}
    pack_meta: dict[int, dict] = {}

    # --- 1. Pack presence + SHA independence ---
    for eid in ARCHIVAL + INDEP:
        summary_p, raw_p = _pack_paths(eid)
        if not summary_p.exists() or not raw_p.exists():
            remediable["missing_pack"] += 1
            findings.append(
                {
                    "kind": "missing_pack",
                    "remediable": True,
                    "evaluation": eid,
                    "summary": str(summary_p),
                    "raw": str(raw_p),
                }
            )
            continue
        sha = _sha1(raw_p)
        sha_by_eval[eid] = sha
        summary = _load_json(summary_p)
        raw = _load_json(raw_p)
        pack_meta[eid] = {"summary": summary, "raw": raw, "sha": sha}

    archival_shas = {sha_by_eval[e] for e in ARCHIVAL if e in sha_by_eval}
    if len(archival_shas) == 1 and next(iter(archival_shas)) == ARCHIVAL_SHA:
        findings.append(
            {
                "kind": "archival_r1_r3_identical_ok",
                "remediable": False,
                "sha": ARCHIVAL_SHA,
                "note": "history only — not confirmatory independence",
            }
        )
    elif archival_shas:
        # Unexpected divergence among archival packs is not a move blocker, but note it
        findings.append(
            {
                "kind": "archival_sha_unexpected",
                "remediable": False,
                "shas": {str(e): sha_by_eval.get(e) for e in ARCHIVAL},
            }
        )

    for eid in INDEP:
        meta = pack_meta.get(eid)
        if not meta:
            continue
        sha = meta["sha"]
        expected = EXPECTED_SHA.get(eid)
        if expected and sha != expected:
            remediable["indep_sha_mismatch_vs_final3"] += 1
            findings.append(
                {
                    "kind": "indep_sha_mismatch_vs_final3",
                    "remediable": True,
                    "evaluation": eid,
                    "got": sha,
                    "expected": expected,
                }
            )
        else:
            findings.append(
                {
                    "kind": "indep_sha_ok",
                    "remediable": False,
                    "evaluation": eid,
                    "sha": sha,
                }
            )

    if 4 in sha_by_eval and 5 in sha_by_eval:
        if sha_by_eval[4] == sha_by_eval[5]:
            remediable["r4_r5_not_independent"] += 1
            findings.append(
                {
                    "kind": "r4_r5_not_independent",
                    "remediable": True,
                    "sha": sha_by_eval[4],
                    "detail": "confirmatory packs share identical raw_costs",
                }
            )
        else:
            findings.append(
                {
                    "kind": "r4_r5_distinct_sha",
                    "remediable": False,
                    "sha_r4": sha_by_eval[4],
                    "sha_r5": sha_by_eval[5],
                }
            )
        for eid in INDEP:
            if eid in sha_by_eval and sha_by_eval[eid] in archival_shas:
                remediable["indep_sha_equals_archival"] += 1
                findings.append(
                    {
                        "kind": "indep_sha_equals_archival",
                        "remediable": True,
                        "evaluation": eid,
                        "sha": sha_by_eval[eid],
                    }
                )

    # --- 2. rebuilt_from_run_log + meets_ca2 + workload flags ---
    for eid in INDEP:
        meta = pack_meta.get(eid)
        if not meta:
            continue
        summary = meta["summary"]
        rebuilt = bool(summary.get("rebuilt_from_run_log", True))
        if rebuilt:
            remediable["rebuilt_from_run_log_true"] += 1
            findings.append(
                {
                    "kind": "rebuilt_from_run_log_true",
                    "remediable": True,
                    "evaluation": eid,
                    "detail": "confirmatory pack must be fresh, not log-rebuild",
                }
            )
        else:
            findings.append(
                {
                    "kind": "rebuilt_from_run_log_false",
                    "remediable": False,
                    "evaluation": eid,
                }
            )

        meets = bool(summary.get("meets_ca2_two_of_three"))
        success = list(summary.get("success_workloads_vs_both_natives") or [])
        n_success = len(success)
        if not meets:
            remediable["meets_ca2_false"] += 1
            findings.append(
                {
                    "kind": "meets_ca2_false",
                    "remediable": True,
                    "evaluation": eid,
                    "success_workloads": success,
                }
            )
        elif n_success < 2:
            remediable["meets_ca2_flag_inconsistent"] += 1
            findings.append(
                {
                    "kind": "meets_ca2_flag_inconsistent",
                    "remediable": True,
                    "evaluation": eid,
                    "n_success": n_success,
                    "success_workloads": success,
                }
            )
        else:
            findings.append(
                {
                    "kind": "meets_ca2_ok",
                    "remediable": False,
                    "evaluation": eid,
                    "n_success": n_success,
                    "success_workloads": success,
                }
            )

        # Consistency: flag vs per-workload significant_cost_cut_vs_both_natives
        workloads = summary.get("workloads") or {}
        recomputed_success: list[str] = []
        for wl in WORKLOADS:
            w = workloads.get(wl) or {}
            both = bool(w.get("significant_cost_cut_vs_both_natives"))
            if both:
                recomputed_success.append(wl)
            # Cross-check Wilcoxon flags vs raw costs
            raw_wl = (meta["raw"] or {}).get(wl) or {}
            our = list(raw_wl.get("our_costs") or [])
            lc = list(raw_wl.get("lifecycle_costs") or [])
            it = list(raw_wl.get("intelligent_tiering_costs") or [])
            if len(our) != 10 or len(lc) != 10 or len(it) != 10:
                remediable["raw_trial_count_mismatch"] += 1
                findings.append(
                    {
                        "kind": "raw_trial_count_mismatch",
                        "remediable": True,
                        "evaluation": eid,
                        "workload": wl,
                        "n_our": len(our),
                        "n_lc": len(lc),
                        "n_it": len(it),
                    }
                )
                continue
            d_lc = [lc[i] - our[i] for i in range(10)]
            d_it = [it[i] - our[i] for i in range(10)]
            wl_lc = _wilcoxon_greater_zero(d_lc)
            wl_it = _wilcoxon_greater_zero(d_it)
            stored_lc = (w.get("wilcoxon_vs_lifecycle") or {}).get("significant")
            stored_it = (w.get("wilcoxon_vs_intelligent_tiering") or {}).get("significant")
            # Directional consistency without requiring exact p match
            dir_lc_ok = (wl_lc["n_pos"] >= 8 and bool(stored_lc)) or (
                wl_lc["n_pos"] <= 2 and stored_lc is False
            ) or (stored_lc is True and wl_lc.get("p_value") is not None and wl_lc["p_value"] < 0.05) or (
                stored_lc is False and wl_lc.get("p_value") is not None and wl_lc["p_value"] >= 0.05
            )
            # Prefer p-value check when scipy available
            if "p_value" in wl_lc and math.isfinite(wl_lc["p_value"]):
                dir_lc_ok = bool(stored_lc) == (wl_lc["p_value"] < 0.05)
            if "p_value" in wl_it and math.isfinite(wl_it["p_value"]):
                dir_it_ok = bool(stored_it) == (wl_it["p_value"] < 0.05)
            else:
                dir_it_ok = (wl_it["n_pos"] >= 8 and bool(stored_it)) or (
                    wl_it["n_pos"] <= 2 and stored_it is False
                )
            both_re = bool(stored_lc) and bool(stored_it)
            if both_re != both:
                remediable["workload_flag_inconsistent"] += 1
                findings.append(
                    {
                        "kind": "workload_flag_inconsistent",
                        "remediable": True,
                        "evaluation": eid,
                        "workload": wl,
                        "stored_both": both,
                        "from_wilcoxon_flags": both_re,
                    }
                )
            if not dir_lc_ok or not dir_it_ok:
                remediable["wilcoxon_recompute_mismatch"] += 1
                findings.append(
                    {
                        "kind": "wilcoxon_recompute_mismatch",
                        "remediable": True,
                        "evaluation": eid,
                        "workload": wl,
                        "stored_lc_sig": stored_lc,
                        "stored_it_sig": stored_it,
                        "recompute_lc": wl_lc,
                        "recompute_it": wl_it,
                    }
                )
            else:
                findings.append(
                    {
                        "kind": "wilcoxon_consistent",
                        "remediable": False,
                        "evaluation": eid,
                        "workload": wl,
                        "p_lc": wl_lc.get("p_value"),
                        "p_it": wl_it.get("p_value"),
                        "mean_delta_lc": wl_lc["mean_diff"],
                        "mean_delta_it": wl_it["mean_diff"],
                    }
                )

        if set(recomputed_success) != set(success):
            remediable["success_list_mismatch"] += 1
            findings.append(
                {
                    "kind": "success_list_mismatch",
                    "remediable": True,
                    "evaluation": eid,
                    "stored": success,
                    "from_flags": recomputed_success,
                }
            )

    # --- 3. Destroy evidence ---
    destroy_ok = False
    destroy_detail: dict = {}
    if TFSTATE.exists():
        state = _load_json(TFSTATE)
        n_res = len(state.get("resources") or [])
        destroy_detail["terraform_resources"] = n_res
        destroy_detail["terraform_serial"] = state.get("serial")
        empty_state = n_res == 0
    else:
        empty_state = False
        remediable["missing_terraform_state"] += 1
        findings.append({"kind": "missing_terraform_state", "remediable": True})

    destroy_after_flags = []
    for eid in INDEP:
        meta = pack_meta.get(eid)
        if not meta:
            continue
        flag = bool(meta["summary"].get("destroy_after"))
        destroy_after_flags.append(flag)
        if not flag:
            remediable["destroy_after_missing"] += 1
            findings.append(
                {
                    "kind": "destroy_after_missing",
                    "remediable": True,
                    "evaluation": eid,
                }
            )

    note = LIVE / "FINAL3_NOTE.md"
    note_mentions_destroy = False
    if note.exists():
        text = note.read_text(encoding="utf-8").lower()
        note_mentions_destroy = "destroy" in text and ("removed" in text or "completed" in text)
    else:
        remediable["missing_final3_note"] += 1
        findings.append({"kind": "missing_final3_note", "remediable": True})

    destroy_confirmed = LIVE / "destroy_confirmed.txt"
    if destroy_confirmed.exists():
        dc = destroy_confirmed.read_text(encoding="utf-8")
        destroy_detail["destroy_confirmed_txt"] = dc.strip()[:200]
        txt_ok = "destroy_confirmed=yes" in dc.lower() or "destroy_confirmed=yes" in dc
    else:
        txt_ok = False

    # Accept: empty TF state AND (destroy_after on r4+r5) AND (note or destroy_confirmed.txt)
    if empty_state and all(destroy_after_flags) and (note_mentions_destroy or txt_ok):
        destroy_ok = True
        findings.append(
            {
                "kind": "destroy_confirmed",
                "remediable": False,
                "terraform_resources": 0,
                "destroy_after_r4_r5": True,
                "final3_note_destroy": note_mentions_destroy,
                "destroy_confirmed_txt": txt_ok,
            }
        )
    elif empty_state and all(destroy_after_flags):
        # Remediable hygiene: write destroy_confirmed.txt from evidence
        remediable["destroy_confirmed_txt_missing"] += 1
        findings.append(
            {
                "kind": "destroy_confirmed_txt_missing",
                "remediable": True,
                "detail": "empty terraform + destroy_after present; add results/live/destroy_confirmed.txt",
            }
        )
    else:
        remediable["destroy_not_confirmed"] += 1
        findings.append(
            {
                "kind": "destroy_not_confirmed",
                "remediable": True,
                "empty_terraform": empty_state,
                "destroy_after_flags": destroy_after_flags,
                "final3_note_destroy": note_mentions_destroy,
            }
        )

    # --- 4. Allocation-accuracy limb (intentional weak / WONTFIX) ---
    alloc_path = LIVE / "allocation_accuracy_r4_r5_offline.json"
    alloc_weak = False
    alloc_detail: dict = {}
    if not alloc_path.exists():
        remediable["missing_alloc_acc_artefact"] += 1
        findings.append({"kind": "missing_alloc_acc_artefact", "remediable": True})
    else:
        alloc = _load_json(alloc_path)
        for key in ("r4", "r5"):
            block = alloc.get(key) or {}
            prop = float((block.get("proposed") or {}).get("accuracy", float("nan")))
            lc_acc = float((block.get("lifecycle") or {}).get("accuracy", float("nan")))
            delta = float(block.get("delta_proposed_minus_lifecycle", prop - lc_acc))
            alloc_detail[key] = {
                "proposed_acc": prop,
                "lifecycle_acc": lc_acc,
                "delta": delta,
            }
            if math.isfinite(prop) and math.isfinite(lc_acc) and prop < lc_acc:
                alloc_weak = True
        if alloc_weak:
            findings.append(
                {
                    "kind": "alloc_acc_weaker_than_lifecycle",
                    "remediable": False,
                    "detail": alloc_detail,
                    "note": "intentional RQ limb — not a cost Wilcoxon remediable gap",
                }
            )
            if not WONTFIX_ALLOC.exists():
                remediable["missing_dated_wontfix_alloc_acc"] += 1
                findings.append(
                    {
                        "kind": "missing_dated_wontfix_alloc_acc",
                        "remediable": True,
                        "path": str(WONTFIX_ALLOC),
                        "detail": "write dated WONTFIX for intentional weak alloc-acc limb",
                    }
                )
            else:
                findings.append(
                    {
                        "kind": "dated_wontfix_alloc_acc_present",
                        "remediable": False,
                        "path": str(WONTFIX_ALLOC),
                    }
                )
        else:
            findings.append(
                {
                    "kind": "alloc_acc_not_weaker",
                    "remediable": False,
                    "detail": alloc_detail,
                }
            )

    # Dry-run improved arm also weak (supporting evidence, not remediable)
    improved = ROOT / "results" / "data" / "improved_results.json"
    if improved.exists():
        imp = _load_json(improved)
        acc = float(
            ((imp.get("evaluation") or {}).get("classification") or {}).get("accuracy", float("nan"))
        )
        findings.append(
            {
                "kind": "dryrun_improved_alloc_acc",
                "remediable": False,
                "accuracy": acc,
                "weak": bool(math.isfinite(acc) and acc < 0.5),
            }
        )

    remediable_total = int(sum(remediable.values()))
    if remediable_total > 0:
        disposition = "FIX_REMEDIABLE"
    elif alloc_weak:
        disposition = "DATED_WONTFIX_ALLOC_ACC"
    else:
        disposition = "INDEPENDENCE_OK"

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "live_root": str(LIVE),
        "sha_by_eval": {str(k): v for k, v in sha_by_eval.items()},
        "expected_indep_sha": EXPECTED_SHA,
        "destroy": {
            "ok": destroy_ok,
            **destroy_detail,
            "note_mentions_destroy": note_mentions_destroy,
        },
        "alloc_acc": alloc_detail,
        "alloc_acc_weak_vs_lifecycle": alloc_weak,
        "findings": findings,
        "remediable": dict(remediable),
        "remediable_total": remediable_total,
        "move_blocker": remediable_total > 0,
        "disposition": disposition,
        "same_metrics_snapshot": {
            "protocol": "ca2_three_workload_wilcoxon",
            "baselines": ["aws_lifecycle_policies", "aws_intelligent_tiering"],
            "metrics": [
                "modeled_monthly_usd_delta",
                "wilcoxon_p",
                "meets_ca2_two_of_three",
                "allocation_accuracy_offline_oracle",
                "forecast_mape_vs_naive_dryrun",
            ],
            "binding_baseline_paper": "Shen et al. 2025 TierBase (workload-driven cost-optimised placement)",
        },
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = out.with_suffix(".md")
    lines = [
        "# Varun r4+r5 independence remediable audit (scripted)",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Live root: `{LIVE}`",
        "",
        "## Move gate",
        "",
        f"- **remediable_total:** {remediable_total}",
        f"- **move_blocker:** {report['move_blocker']}",
        f"- **disposition:** `{disposition}`",
        f"- **alloc_acc_weak_vs_lifecycle:** {alloc_weak}",
        f"- **destroy_ok:** {destroy_ok}",
        "",
        "## SHA inventory",
        "",
        "```json",
        json.dumps({str(k): v for k, v in sha_by_eval.items()}, indent=2),
        "```",
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
        lines.append(f"- `{f['kind']}` remediable={f.get('remediable')} eval={f.get('evaluation', '-')}")
    lines.extend(
        [
            "",
            "```bash",
            "cd Varun/s3-predictive-optimization",
            "python3 scripts/audit_independence_root_causes.py",
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
                "destroy_ok": destroy_ok,
                "alloc_acc_weak_vs_lifecycle": alloc_weak,
                "remediable": dict(remediable),
            },
            indent=2,
        )
    )
    return 2 if remediable_total > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
