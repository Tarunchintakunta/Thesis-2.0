#!/usr/bin/env python3
"""Score stages against labels; write per-category metrics. No terraform apply."""

from __future__ import annotations

import csv
import difflib
import json
import platform
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.io_util import CORPUS, RESULTS, load_labels  # noqa: E402
from src.metrics import (  # noqa: E402
    confusion,
    holm_bonferroni,
    mcnemar,
    rates,
    wilson_ci,
)

STAGES = (
    ("checklist", "checklist_verdicts.json", "manual_checklist_scripted"),
    ("checkov", "checkov_verdicts.json", "checkov"),
    ("tfsec", "tfsec_verdicts.json", "tfsec"),
    ("static_union", None, "checkov_union_tfsec"),
    ("opa", "opa_verdicts.json", "opa_rego_gate"),
)


def load_verdict_map(filename: str) -> dict[str, dict]:
    raw = json.loads((RESULTS / filename).read_text(encoding="utf-8"))
    return {v["module_id"]: v for v in raw["verdicts"]}, raw


def remediation_loc(rows: list[dict]) -> list[dict]:
    by_id = {r["module_id"]: r for r in rows}
    out = []
    for r in rows:
        if r["label"] != "insecure":
            continue
        sib = by_id[r["sibling_id"]]
        a = (CORPUS / r["rel_path"]).read_text(encoding="utf-8").splitlines(True)
        b = (CORPUS / sib["rel_path"]).read_text(encoding="utf-8").splitlines(True)
        diff = list(difflib.unified_diff(a, b, lineterm=""))
        changed = sum(1 for line in diff if line.startswith("+") or line.startswith("-"))
        changed -= sum(1 for line in diff if line.startswith("+++") or line.startswith("---"))
        out.append(
            {
                "module_id": r["module_id"],
                "category": r["category"],
                "sibling_id": r["sibling_id"],
                "severity": r["severity"],
                "diff_lines": max(0, changed),
            }
        )
    return out


def stage_predictions(rows, checkov, tfsec, checklist, opa):
    preds = {
        "checklist": {},
        "checkov": {},
        "tfsec": {},
        "static_union": {},
        "opa": {},
    }
    for r in rows:
        mid = r["module_id"]
        preds["checklist"][mid] = int(checklist[mid]["predicted"])
        preds["checkov"][mid] = int(checkov[mid]["predicted"])
        preds["tfsec"][mid] = int(tfsec[mid]["predicted"])
        preds["static_union"][mid] = int(
            checkov[mid]["predicted"] or tfsec[mid]["predicted"]
        )
        preds["opa"][mid] = int(opa[mid]["predicted"])
    return preds


def score(rows, preds, stage: str, category: str | None) -> dict:
    subset = [r for r in rows if category is None or r["category"] == category]
    y_true = [1 if r["label"] == "insecure" else 0 for r in subset]
    y_pred = [preds[stage][r["module_id"]] for r in subset]
    c = confusion(y_true, y_pred)
    r = rates(c)
    rec_lo, rec_hi = wilson_ci(c["tp"], c["tp"] + c["fn"])
    row = {
        "stage": stage,
        "category": category or "ALL",
        **c,
        **r,
        "recall_ci95_lo": rec_lo,
        "recall_ci95_hi": rec_hi,
    }
    return row


def severity_coverage(rows, preds, stage: str) -> list[dict]:
    out = []
    for sev in ("HIGH", "MEDIUM", "LOW"):
        insecure = [
            r for r in rows if r["label"] == "insecure" and r["severity"] == sev
        ]
        if not insecure:
            continue
        caught = sum(preds[stage][r["module_id"]] for r in insecure)
        out.append(
            {
                "stage": stage,
                "severity": sev,
                "n_insecure": len(insecure),
                "detected": caught,
                "coverage": caught / len(insecure),
            }
        )
    return out


def paired_mcnemar(rows, preds, stage_a: str, stage_b: str) -> dict:
    """Compare recall on insecure modules only (caught vs missed)."""
    insecure = [r for r in rows if r["label"] == "insecure"]
    b = c = 0  # a-only, b-only
    for r in insecure:
        a = preds[stage_a][r["module_id"]]
        bb = preds[stage_b][r["module_id"]]
        if a and not bb:
            b += 1
        elif bb and not a:
            c += 1
    stats = mcnemar(b, c)
    stats.update({"stage_a": stage_a, "stage_b": stage_b, "n_insecure": len(insecure)})
    return stats


def tool_versions() -> dict:
    versions = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    for name, extra in (
        ("terraform", None),
        ("checkov", str(Path.home() / "Library/Python/3.14/bin/checkov")),
        ("tfsec", str(Path.home() / ".local/bin/tfsec")),
        ("opa", str(Path.home() / ".local/bin/opa")),
    ):
        bin_path = shutil.which(name) or extra
        if not bin_path or not Path(bin_path).exists():
            versions[name] = "NOT_FOUND"
            continue
        try:
            cmd = [bin_path, "version"] if name in {"terraform", "opa"} else [bin_path, "--version"]
            out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
            versions[name] = out.strip().splitlines()[0]
        except (OSError, subprocess.CalledProcessError) as exc:
            versions[name] = f"error:{exc}"
    return versions


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def main() -> int:
    rows = load_labels()
    checkov, checkov_raw = load_verdict_map("checkov_verdicts.json")
    tfsec, tfsec_raw = load_verdict_map("tfsec_verdicts.json")
    checklist, checklist_raw = load_verdict_map("checklist_verdicts.json")
    opa, opa_raw = load_verdict_map("opa_verdicts.json")
    preds = stage_predictions(rows, checkov, tfsec, checklist, opa)

    metric_rows = []
    categories = sorted({r["category"] for r in rows})
    for stage, _, _ in STAGES:
        metric_rows.append(score(rows, preds, stage, None))
        for cat in categories:
            metric_rows.append(score(rows, preds, stage, cat))

    loc_rows = remediation_loc(rows)
    loc_by_cat = defaultdict(list)
    for item in loc_rows:
        loc_by_cat[item["category"]].append(item["diff_lines"])
    loc_summary = []
    for cat, vals in sorted(loc_by_cat.items()):
        loc_summary.append(
            {
                "category": cat,
                "n_insecure": len(vals),
                "mean_diff_lines": mean(vals),
                "min_diff_lines": min(vals),
                "max_diff_lines": max(vals),
            }
        )
    loc_summary.append(
        {
            "category": "ALL",
            "n_insecure": len(loc_rows),
            "mean_diff_lines": mean([x["diff_lines"] for x in loc_rows]),
            "min_diff_lines": min(x["diff_lines"] for x in loc_rows),
            "max_diff_lines": max(x["diff_lines"] for x in loc_rows),
        }
    )

    time_rows = []
    for raw in (checklist_raw, checkov_raw, tfsec_raw, opa_raw):
        tool = raw["tool"]
        samples = raw.get("sample_times") or []
        by_cat = defaultdict(list)
        for s in samples:
            by_cat[s["category"]].append(float(s["seconds"]))
        for cat, vals in sorted(by_cat.items()):
            time_rows.append(
                {
                    "tool": tool,
                    "category": cat,
                    "n_timed": len(vals),
                    "mean_seconds": mean(vals),
                    "min_seconds": min(vals),
                    "max_seconds": max(vals),
                    "batch_seconds": raw.get("batch_seconds"),
                }
            )

    sev_rows = []
    for stage, _, _ in STAGES:
        sev_rows.extend(severity_coverage(rows, preds, stage))

    mcnemar_rows = [
        paired_mcnemar(rows, preds, "checkov", "tfsec"),
        paired_mcnemar(rows, preds, "static_union", "opa"),
        paired_mcnemar(rows, preds, "checklist", "static_union"),
        paired_mcnemar(rows, preds, "checklist", "opa"),
    ]
    holm_rows = holm_bonferroni(mcnemar_rows, alpha=0.05)

    insecure_n = sum(1 for r in rows if r["label"] == "insecure")
    rq = {
        "n_modules": len(rows),
        "n_insecure": insecure_n,
        "checkov_identified_pct": next(
            m["identified_pct"] for m in metric_rows if m["stage"] == "checkov" and m["category"] == "ALL"
        ),
        "tfsec_identified_pct": next(
            m["identified_pct"] for m in metric_rows if m["stage"] == "tfsec" and m["category"] == "ALL"
        ),
        "static_union_identified_pct": next(
            m["identified_pct"]
            for m in metric_rows
            if m["stage"] == "static_union" and m["category"] == "ALL"
        ),
        "opa_identified_pct": next(
            m["identified_pct"] for m in metric_rows if m["stage"] == "opa" and m["category"] == "ALL"
        ),
        "checklist_identified_pct": next(
            m["identified_pct"]
            for m in metric_rows
            if m["stage"] == "checklist" and m["category"] == "ALL"
        ),
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    write_csv(RESULTS / "metrics_per_category.csv", metric_rows)
    write_csv(RESULTS / "remediation_loc.csv", loc_rows)
    write_csv(RESULTS / "remediation_loc_summary.csv", loc_summary)
    write_csv(RESULTS / "scan_times.csv", time_rows)
    write_csv(RESULTS / "severity_coverage.csv", sev_rows)
    write_csv(RESULTS / "mcnemar_pairs.csv", mcnemar_rows)
    write_csv(RESULTS / "holm_bonferroni.csv", holm_rows)

    versions = tool_versions()
    (RESULTS / "tool_versions.json").write_text(
        json.dumps(versions, indent=2) + "\n", encoding="utf-8"
    )
    (RESULTS / "rq_summary.json").write_text(
        json.dumps(rq, indent=2) + "\n", encoding="utf-8"
    )

    verdict_rows = []
    for r in rows:
        mid = r["module_id"]
        verdict_rows.append(
            {
                "module_id": mid,
                "category": r["category"],
                "label": r["label"],
                "severity": r["severity"],
                "mode": r["mode"],
                "y_true": 1 if r["label"] == "insecure" else 0,
                "checklist": preds["checklist"][mid],
                "checkov": preds["checkov"][mid],
                "tfsec": preds["tfsec"][mid],
                "static_union": preds["static_union"][mid],
                "opa": preds["opa"][mid],
            }
        )
    write_csv(RESULTS / "verdicts.csv", verdict_rows)

    print("metrics_per_category.csv")
    print(f"RQ insecure identified: checkov={rq['checkov_identified_pct']:.1f}% "
          f"tfsec={rq['tfsec_identified_pct']:.1f}% "
          f"union={rq['static_union_identified_pct']:.1f}% "
          f"opa={rq['opa_identified_pct']:.1f}% "
          f"checklist={rq['checklist_identified_pct']:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
