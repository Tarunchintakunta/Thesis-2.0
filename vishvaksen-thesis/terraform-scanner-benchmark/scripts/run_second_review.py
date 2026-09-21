#!/usr/bin/env python3
"""Provisional same-author dual-pass on a 20% stratified subsample.

Formal CA2 asks for an independent second reviewer. When no second human is
available, this script records an honest *provisional* dual-pass:

  - Reviewer A = generator oracle labels in corpus/labels.csv
  - Reviewer B = same author, blind to the CSV label column, applying the
    documented checklist heuristics to main.tf only

κ is computed and stored. STATUS must mark this PROVISIONAL — not independent.
"""

from __future__ import annotations

import csv
import json
import math
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_checklist import apply_checklist  # noqa: E402
from src.common import CATEGORIES  # noqa: E402
from src.io_util import CORPUS, RESULTS, load_labels  # noqa: E402

SEED = 20260921
PER_CATEGORY = 12  # 20% of 60


def cohen_kappa(pairs: list[tuple[str, str]]) -> dict:
    """Binary insecure-vs-secure Cohen's κ."""
    labels = ("secure", "insecure")
    n = len(pairs)
    if n == 0:
        return {"n": 0, "kappa": None, "agreement": None}
    matrix = {(a, b): 0 for a in labels for b in labels}
    for a, b in pairs:
        matrix[(a, b)] += 1
    po = sum(matrix[(l, l)] for l in labels) / n
    row = {l: sum(matrix[(l, x)] for x in labels) / n for l in labels}
    col = {l: sum(matrix[(x, l)] for x in labels) / n for l in labels}
    pe = sum(row[l] * col[l] for l in labels)
    kappa = None if math.isclose(1.0, pe) else (po - pe) / (1.0 - pe)
    return {
        "n": n,
        "po": po,
        "pe": pe,
        "kappa": kappa,
        "agreement": po,
        "confusion": {
            "a_secure_b_secure": matrix[("secure", "secure")],
            "a_secure_b_insecure": matrix[("secure", "insecure")],
            "a_insecure_b_secure": matrix[("insecure", "secure")],
            "a_insecure_b_insecure": matrix[("insecure", "insecure")],
        },
    }


def draw_sample(rows: list[dict]) -> list[dict]:
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_cat[row["category"]].append(row)
    rng = random.Random(SEED)
    sample: list[dict] = []
    for cat in CATEGORIES:
        pool = list(by_cat[cat])
        if len(pool) < PER_CATEGORY:
            raise SystemExit(f"{cat}: need {PER_CATEGORY}, have {len(pool)}")
        sample.extend(rng.sample(pool, PER_CATEGORY))
    sample.sort(key=lambda r: (r["category"], r["module_id"]))
    return sample


def main() -> int:
    rows = load_labels()
    sample = draw_sample(rows)
    records = []
    pairs: list[tuple[str, str]] = []

    for row in sample:
        # Blind to CSV label: score HCL with checklist heuristics only.
        text = (CORPUS / row["rel_path"]).read_text(encoding="utf-8")
        hits = apply_checklist(text, row["category"])
        b_label = "insecure" if hits else "secure"
        a_label = row["label"]
        pairs.append((a_label, b_label))
        records.append(
            {
                "module_id": row["module_id"],
                "category": row["category"],
                "pattern_id": row["pattern_id"],
                "severity": row.get("severity", ""),
                "rel_path": row["rel_path"],
                "reviewer_a_oracle_label": a_label,
                "reviewer_b_provisional_label": b_label,
                "reviewer_b_method": "same_author_checklist_heuristics_blind_to_csv_label",
                "reviewer_b_hits": hits[:8],
                "agree": a_label == b_label,
            }
        )

    stats = cohen_kappa(pairs)
    payload = {
        "protocol": "provisional_same_author_dual_pass",
        "independent_second_human": False,
        "provisional": True,
        "seed": SEED,
        "per_category": PER_CATEGORY,
        "n_sample": len(records),
        "n_corpus": len(rows),
        "sample_fraction": len(records) / len(rows),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "reviewer_a": "generator_oracle_labels_csv",
        "reviewer_b": "same_author_blind_checklist_pass",
        "honesty": (
            "Not an independent human second reviewer. Same-author provisional "
            "dual-pass using checklist heuristics on main.tf without reading the "
            "CSV label column. Formal CA2 still requires a second human for "
            "definitive κ."
        ),
        "cohen_kappa": stats,
        "modules": records,
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS / "second_review_subsample.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    csv_path = RESULTS / "second_review_sample.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        fields = [
            "module_id",
            "category",
            "pattern_id",
            "severity",
            "rel_path",
            "reviewer_a_oracle_label",
            "reviewer_b_provisional_label",
            "agree",
        ]
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for rec in records:
            w.writerow({k: rec[k] for k in fields})

    status = RESULTS / "second_review_STATUS.md"
    kappa = stats["kappa"]
    kappa_s = "n/a" if kappa is None else f"{kappa:.4f}"
    status.write_text(
        f"""# Second-reviewer subsample

**Status:** PROVISIONAL (same-author dual-pass) — **not** an independent human  
**Sample:** {len(records)} / {len(rows)} ({PER_CATEGORY}/category, seed={SEED})  
**Cohen's κ (oracle vs blind checklist pass):** {kappa_s}  
**Agreement (po):** {stats['agreement']:.4f}

Artefacts:
- `results/second_review_subsample.json`
- `results/second_review_sample.csv`

Honesty: no second human was available. This records a same-author provisional
dual-pass so the protocol is exercised and measurable. Replace with an
independent reviewer before claiming definitive inter-rater reliability.
""",
        encoding="utf-8",
    )
    print(
        f"wrote {json_path.name} n={len(records)} kappa={kappa_s} "
        f"agree={stats['agreement']:.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
