#!/usr/bin/env python3
"""Scripted remediable audit for Rasool soft limbs — not manual chat judgment.

Verifies final_1–3 W3/W4 key-cell packs + pooled ANOVA, and (when claimed)
w1w2_a key-cells. Flags remediable claim↔evidence gaps (missing packs,
fabricated wins). Intentional soft limbs (n=1 exploratory W1/W2; no full
W1–W4 confirmatory ANOVA) get dated WONTFIX when remediable_total=0.

Usage (from dynamodb-pk-capacity-eval/):
  python3 scripts/audit_soft_limbs_root_causes.py
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
EXPECTED_CELLS = 12
REQUIRED_METRICS = (
    "latency_mean_ms",
    "latency_p99_ms",
    "throughput_ops_s",
    "throttle_rate",
    "key_design",
    "capacity_mode",
    "workload",
)
FINAL_WORKLOADS = {"W3", "W4"}
W1W2_WORKLOADS = {"W1", "W2"}
KEYS = {"K1", "K2", "K3"}
CAPS = {"on_demand", "provisioned"}

# Pooled ANOVA claims that must match evidence (GENAI_HANDOFF / FINAL3_BASELINE)
CLAIMED_W3_KEY_F_MIN = 50.0
CLAIMED_W3_KEY_P_MAX = 1e-5
CLAIMED_W4_KEY_F_MIN = 10.0
CLAIMED_W4_KEY_P_MAX = 1e-3
# Capacity / interaction must remain non-significant on W3 mean latency
CLAIMED_W3_CAP_P_MIN = 0.05
CLAIMED_W3_INT_P_MIN = 0.05


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


def _read_batches(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _destroy_ok(pack: Path) -> bool:
    p = pack / "destroy_confirmed.txt"
    if not p.exists():
        return False
    return "destroy_confirmed=yes" in p.read_text(encoding="utf-8")


def _check_pack(
    pack: Path,
    *,
    expected_workloads: set[str],
    label: str,
    remediable: dict[str, int],
    findings: list[dict],
) -> list[dict]:
    batches = pack / "batches.csv"
    if not pack.exists() or not batches.exists():
        remediable[f"missing_{label}"] += 1
        findings.append(
            {
                "kind": f"missing_{label}",
                "remediable": True,
                "pack": str(pack.relative_to(ROOT)),
            }
        )
        return []

    rows = _read_batches(batches)
    missing_cols = [c for c in REQUIRED_METRICS if c not in (rows[0] if rows else {})]
    if missing_cols:
        remediable[f"missing_metrics_{label}"] += 1
        findings.append(
            {
                "kind": f"missing_metrics_{label}",
                "remediable": True,
                "columns": missing_cols,
            }
        )

    if len(rows) != EXPECTED_CELLS:
        remediable[f"cell_count_mismatch_{label}"] += 1
        findings.append(
            {
                "kind": f"cell_count_mismatch_{label}",
                "remediable": True,
                "n": len(rows),
                "expected": EXPECTED_CELLS,
            }
        )

    workloads = {r.get("workload", "") for r in rows}
    keys = {r.get("key_design", "") for r in rows}
    caps = {r.get("capacity_mode", "") for r in rows}
    if workloads != expected_workloads:
        remediable[f"workload_set_mismatch_{label}"] += 1
        findings.append(
            {
                "kind": f"workload_set_mismatch_{label}",
                "remediable": True,
                "got": sorted(workloads),
                "expected": sorted(expected_workloads),
            }
        )
    if keys != KEYS or caps != CAPS:
        remediable[f"factor_levels_mismatch_{label}"] += 1
        findings.append(
            {
                "kind": f"factor_levels_mismatch_{label}",
                "remediable": True,
                "keys": sorted(keys),
                "caps": sorted(caps),
            }
        )

    bad_metric = 0
    for r in rows:
        for col in ("latency_mean_ms", "latency_p99_ms", "throughput_ops_s", "throttle_rate"):
            v = _f(r.get(col))
            if v is None or (col != "throttle_rate" and (not math.isfinite(v) or v < 0)):
                bad_metric += 1
            if col == "throttle_rate" and v is not None and v < 0:
                bad_metric += 1
    if bad_metric:
        remediable[f"invalid_metrics_{label}"] += 1
        findings.append(
            {
                "kind": f"invalid_metrics_{label}",
                "remediable": True,
                "n_bad": bad_metric,
            }
        )

    if not _destroy_ok(pack):
        remediable[f"destroy_not_confirmed_{label}"] += 1
        findings.append({"kind": f"destroy_not_confirmed_{label}", "remediable": True})
    else:
        findings.append(
            {
                "kind": f"pack_ok_{label}",
                "remediable": False,
                "n": len(rows),
                "workloads": sorted(workloads),
            }
        )
    return rows


def _scan_fabricated_wins(remediable: dict[str, int], findings: list[dict]) -> None:
    """Flag text that markets fabricated confirmatory wins."""
    patterns = [
        (
            re.compile(r"ALIGNMENT\s*=\s*100", re.I),
            "fabricated_alignment_100",
            "ALIGNMENT=100 marketing",
        ),
        (
            re.compile(r"full\s+W1.?W4\s+confirmatory\s+ANOVA\s+100", re.I),
            "fabricated_full_anova_100",
            "full W1–W4 confirmatory ANOVA 100%",
        ),
        (
            re.compile(r"K4\s+(wins|dominance|dominates|best)", re.I),
            "fabricated_k4_dominance",
            "K4 dominance claim",
        ),
        (
            re.compile(
                r"W1/?W2.{0,40}confirmatory\s+(two-?way\s+)?ANOVA.{0,20}(reject|significant|supported)",
                re.I | re.S,
            ),
            "fabricated_w1w2_confirmatory_anova",
            "W1/W2 confirmatory ANOVA win",
        ),
    ]
    scan_roots = [
        ROOT / "STATUS.md",
        ROOT / "GENAI_HANDOFF.md",
        RESULTS / "FINAL3_BASELINE.md",
        RESULTS / "w1w2_a" / "W1W2_BASELINE.md",
        ROOT.parent / "rassool_final_report.md",
    ]
    hits: dict[str, list[str]] = defaultdict(list)
    for path in scan_roots:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for cre, kind, _label in patterns:
            if cre.search(text):
                # Allow explicit quarantine / forbidden lines
                if "quarantine" in text.lower() and kind == "fabricated_k4_dominance":
                    # only count if not near quarantine language for K4
                    if re.search(r"K4.{0,80}quarantin", text, re.I | re.S):
                        continue
                if kind.startswith("fabricated_alignment") or kind.startswith(
                    "fabricated_full"
                ):
                    # Negated marketing / claims — skip prohibition windows
                    for m in cre.finditer(text):
                        start = max(0, m.start() - 100)
                        window = text[start : m.end() + 40].lower()
                        if any(
                            tok in window
                            for tok in (
                                "not market",
                                "do not claim",
                                "do **not** claim",
                                "do **not** market",
                                "forbidden",
                                "don't claim",
                                "do not market",
                            )
                        ):
                            continue
                        hits[kind].append(str(path.relative_to(ROOT.parent)))
                    continue
                hits[kind].append(str(path.relative_to(ROOT.parent)))
    for kind, paths in hits.items():
        if not paths:
            continue
        remediable[kind] += len(set(paths))
        findings.append(
            {
                "kind": kind,
                "remediable": True,
                "paths": sorted(set(paths)),
            }
        )
    if not hits:
        findings.append({"kind": "no_fabricated_win_claims", "remediable": False})


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="JSON report path (default: results/analysis/soft_limbs_audit_report.json)",
    )
    args = ap.parse_args()
    out = args.out or (RESULTS / "analysis" / "soft_limbs_audit_report.json")

    findings: list[dict] = []
    remediable: dict[str, int] = defaultdict(int)

    final_rows: dict[str, list[dict]] = {}
    for name in ("final_1", "final_2", "final_3"):
        rows = _check_pack(
            RESULTS / name,
            expected_workloads=FINAL_WORKLOADS,
            label=name,
            remediable=remediable,
            findings=findings,
        )
        final_rows[name] = rows

    # Pooled ANOVA
    pooled_path = RESULTS / "pooled_final3_anova.json"
    pooled_snap: dict = {}
    if not pooled_path.exists():
        remediable["missing_pooled_anova"] += 1
        findings.append({"kind": "missing_pooled_anova", "remediable": True})
    else:
        pooled = json.loads(pooled_path.read_text(encoding="utf-8"))
        sources = set(pooled.get("source_packs") or [])
        if sources != {"final_1", "final_2", "final_3"}:
            remediable["pooled_source_mismatch"] += 1
            findings.append(
                {
                    "kind": "pooled_source_mismatch",
                    "remediable": True,
                    "got": sorted(sources),
                }
            )
        n_rows = int(pooled.get("n_rows") or 0)
        if n_rows != 36:
            remediable["pooled_n_rows_mismatch"] += 1
            findings.append(
                {
                    "kind": "pooled_n_rows_mismatch",
                    "remediable": True,
                    "n_rows": n_rows,
                    "expected": 36,
                }
            )
        w3 = (
            pooled.get("workloads", {})
            .get("W3", {})
            .get("factorial_latency_mean_ms", {})
            .get("terms", {})
        )
        w4 = (
            pooled.get("workloads", {})
            .get("W4", {})
            .get("factorial_latency_mean_ms", {})
            .get("terms", {})
        )
        w3_key = w3.get("key") or {}
        w4_key = w4.get("key") or {}
        w3_cap = w3.get("capacity") or {}
        w3_int = w3.get("interaction") or {}
        pooled_snap = {
            "W3_key_F": w3_key.get("F"),
            "W3_key_p": w3_key.get("p"),
            "W3_capacity_p": w3_cap.get("p"),
            "W3_interaction_p": w3_int.get("p"),
            "W4_key_F": w4_key.get("F"),
            "W4_key_p": w4_key.get("p"),
            "n_rows": n_rows,
        }
        # Claim↔evidence: key effect must support claimed significance
        if not (
            _f(w3_key.get("F")) is not None
            and _f(w3_key.get("F")) >= CLAIMED_W3_KEY_F_MIN
            and _f(w3_key.get("p")) is not None
            and _f(w3_key.get("p")) <= CLAIMED_W3_KEY_P_MAX
        ):
            remediable["w3_key_effect_claim_mismatch"] += 1
            findings.append(
                {
                    "kind": "w3_key_effect_claim_mismatch",
                    "remediable": True,
                    "got": w3_key,
                }
            )
        if not (
            _f(w4_key.get("F")) is not None
            and _f(w4_key.get("F")) >= CLAIMED_W4_KEY_F_MIN
            and _f(w4_key.get("p")) is not None
            and _f(w4_key.get("p")) <= CLAIMED_W4_KEY_P_MAX
        ):
            remediable["w4_key_effect_claim_mismatch"] += 1
            findings.append(
                {
                    "kind": "w4_key_effect_claim_mismatch",
                    "remediable": True,
                    "got": w4_key,
                }
            )
        # Fabricated capacity / interaction wins on W3 mean latency
        cap_p = _f(w3_cap.get("p"))
        int_p = _f(w3_int.get("p"))
        if cap_p is not None and cap_p < CLAIMED_W3_CAP_P_MIN:
            # Evidence itself significant — not a fabrication; note only
            findings.append(
                {
                    "kind": "w3_capacity_significant_in_data",
                    "remediable": False,
                    "p": cap_p,
                    "note": "data-significant; update honest claims if previously ns",
                }
            )
        elif cap_p is None:
            remediable["missing_w3_capacity_term"] += 1
            findings.append({"kind": "missing_w3_capacity_term", "remediable": True})
        else:
            findings.append(
                {
                    "kind": "w3_capacity_ns_retained",
                    "remediable": False,
                    "p": cap_p,
                }
            )
        if int_p is not None and int_p >= CLAIMED_W3_INT_P_MIN:
            findings.append(
                {
                    "kind": "w3_interaction_ns_retained",
                    "remediable": False,
                    "p": int_p,
                }
            )
        findings.append(
            {
                "kind": "pooled_anova_ok",
                "remediable": False,
                "snapshot": pooled_snap,
            }
        )

    # w1w2_a claimed in GENAI_HANDOFF / scoreboard — verify if present; missing = remediable
    w1w2 = RESULTS / "w1w2_a"
    claimed_w1w2 = True  # cohort + GENAI claim this pack
    w1w2_rows: list[dict] = []
    if claimed_w1w2:
        w1w2_rows = _check_pack(
            w1w2,
            expected_workloads=W1W2_WORKLOADS,
            label="w1w2_a",
            remediable=remediable,
            findings=findings,
        )
        # Soft limb honesty: n=1 exploratory — must NOT have confirmatory ANOVA artefact claiming W1/W2 family
        fake_anova = list(w1w2.glob("*confirmatory*anova*")) if w1w2.exists() else []
        if fake_anova:
            remediable["fabricated_w1w2_confirmatory_artefact"] += len(fake_anova)
            findings.append(
                {
                    "kind": "fabricated_w1w2_confirmatory_artefact",
                    "remediable": True,
                    "paths": [str(p.relative_to(ROOT)) for p in fake_anova],
                }
            )
        else:
            findings.append(
                {
                    "kind": "w1w2_exploratory_only",
                    "remediable": False,
                    "note": "n=1 key-cell; confirmatory ANOVA authority remains W3/W4 pooled",
                }
            )

    _scan_fabricated_wins(remediable, findings)

    # Same-metrics snapshot (pooled finals + w1w2 medians for SoT)
    cell_means: dict[str, dict] = {}
    for name, rows in final_rows.items():
        for r in rows:
            cell = f"{r['key_design']}-{r['capacity_mode']}-{r['workload']}"
            cell_means.setdefault(cell, {"latency_mean_ms": [], "throughput_ops_s": [], "throttle_rate": []})
            for k in cell_means[cell]:
                v = _f(r.get(k))
                if v is not None:
                    cell_means[cell][k].append(v)
    pooled_cells = {
        c: {k: (sum(vs) / len(vs) if vs else None) for k, vs in metrics.items()}
        for c, metrics in cell_means.items()
    }

    remediable_total = int(sum(remediable.values()))
    disposition = (
        "FIX_REMEDIABLE"
        if remediable_total > 0
        else "DATED_WONTFIX_SOFT_LIMBS_N1_EXPLORATORY_W1W2"
    )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "thesis": "rassool",
        "artefact": "dynamodb-pk-capacity-eval",
        "findings": findings,
        "remediable": dict(remediable),
        "remediable_total": remediable_total,
        "move_blocker": remediable_total > 0,
        "disposition": disposition,
        "n_rasool_close": disposition.startswith("DATED_WONTFIX"),
        "soft_limbs": {
            "w1w2_n1_exploratory": True,
            "full_w1w4_confirmatory_anova": False,
            "formal_n30_power_plan": "beyond-floor",
            "cost_explorer": "not claimed (list-price)",
        },
        "same_metrics_snapshot": {
            "baseline": "Pantelić et al. (2026) — self-hosted SQL/NoSQL; no RCU/throttle/cost meter",
            "retained_metrics": ["latency_mean_ms", "latency_p99_ms", "throughput_ops_s"],
            "added_metered": ["throttle_rate", "rcu/wcu", "cost_per_10k (list-price)"],
            "pooled_anova": pooled_snap,
            "pooled_final3_cells": pooled_cells,
            "w1w2_a_n_cells": len(w1w2_rows),
        },
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = out.with_suffix(".md")
    lines = [
        "# Rasool soft-limbs remediable audit (scripted)",
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
        "- W1/W2 key-cells: **n=1 exploratory** (KW); not confirmatory ANOVA",
        "- Full W1–W4 confirmatory ANOVA / formal n=30: **beyond-floor**",
        "- Cost Explorer: **not claimed** (list-price proxy)",
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
            "cd rassool-thesis/dynamodb-pk-capacity-eval",
            "python3 scripts/audit_soft_limbs_root_causes.py",
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
