#!/usr/bin/env python3
"""Generate the labelled AWS Terraform corpus (formal N = 240).

Writes one module directory per row plus corpus/labels.csv and corpus/catalog.json.
Does not call terraform apply. Evaluation-only.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common import (  # noqa: E402
    CATEGORIES,
    CATEGORY_PREFIX,
    REGIONS,
    VARIANTS,
    ModuleSpec,
)
from src.patterns_enc import PATTERNS as ENC_PATTERNS  # noqa: E402
from src.patterns_log import PATTERNS as LOG_PATTERNS  # noqa: E402
from src.patterns_oa import PATTERNS as OA_PATTERNS  # noqa: E402
from src.patterns_ps import PATTERNS as PS_PATTERNS  # noqa: E402

CATEGORY_PATTERNS = {
    "public_storage": PS_PATTERNS,
    "overpermissive_access": OA_PATTERNS,
    "encryption_at_rest": ENC_PATTERNS,
    "weak_logging": LOG_PATTERNS,
}


def build_specs() -> list[ModuleSpec]:
    specs: list[ModuleSpec] = []
    for category in CATEGORIES:
        prefix = CATEGORY_PREFIX[category]
        patterns = CATEGORY_PATTERNS[category]
        if len(patterns) != 12:
            raise SystemExit(f"{category}: expected 12 patterns, got {len(patterns)}")
        seq = 0
        for pattern_id, title, severity, defect_attr, _renderer in patterns:
            family: dict[str, str] = {}
            for variant_id, label, mode in VARIANTS:
                seq += 1
                module_id = f"{prefix}-{seq:03d}-{pattern_id}-{variant_id}"
                family[variant_id] = module_id
                region = REGIONS[(seq - 1) % len(REGIONS)]
                sibling = family["s01"]
                specs.append(
                    ModuleSpec(
                        module_id=module_id,
                        category=category,
                        pattern_id=pattern_id,
                        pattern_title=title,
                        variant_id=variant_id,
                        label=label,
                        mode=mode,
                        region=region,
                        severity=severity if label == "insecure" else "none",
                        defect_attribute=defect_attr if label == "insecure" else "",
                        sibling_id=sibling,
                        description=(
                            f"{title} ({label}, {mode}). "
                            "Synthetic evaluation module; do not apply."
                        ),
                    )
                )
            if seq % 5 != 0:
                raise SystemExit(f"variant count drift at {pattern_id}")
        if seq != 60:
            raise SystemExit(f"{category}: expected 60 modules, got {seq}")
    if len(specs) != 240:
        raise SystemExit(f"expected 240 modules, got {len(specs)}")
    return specs


def render(spec: ModuleSpec) -> str:
    patterns = CATEGORY_PATTERNS[spec.category]
    for pattern_id, _title, _sev, _attr, renderer in patterns:
        if pattern_id == spec.pattern_id:
            return renderer(spec)
    raise KeyError(spec.pattern_id)


def write_corpus(out_dir: Path) -> list[ModuleSpec]:
    specs = build_specs()
    corpus = out_dir
    if corpus.exists():
        for leftover in corpus.glob("*"):
            if leftover.name in {"labels.csv", "catalog.json", "README.md"}:
                continue
            if leftover.is_dir():
                for child in leftover.rglob("*"):
                    if child.is_file():
                        child.unlink()
                for child in sorted(leftover.rglob("*"), reverse=True):
                    if child.is_dir():
                        child.rmdir()
                leftover.rmdir()
    for spec in specs:
        mod_dir = corpus / spec.category / spec.module_id
        mod_dir.mkdir(parents=True, exist_ok=True)
        (mod_dir / "main.tf").write_text(render(spec), encoding="utf-8")
        (mod_dir / "EVALUATION_ONLY.txt").write_text(
            "Do not terraform apply. Synthetic labelled evaluation module.\n",
            encoding="utf-8",
        )

    labels_path = corpus / "labels.csv"
    fieldnames = [
        "module_id",
        "category",
        "pattern_id",
        "pattern_title",
        "variant_id",
        "label",
        "mode",
        "region",
        "severity",
        "defect_attribute",
        "sibling_id",
        "rel_path",
        "description",
    ]
    with labels_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for spec in specs:
            rel = f"{spec.category}/{spec.module_id}/main.tf"
            writer.writerow(
                {
                    "module_id": spec.module_id,
                    "category": spec.category,
                    "pattern_id": spec.pattern_id,
                    "pattern_title": spec.pattern_title,
                    "variant_id": spec.variant_id,
                    "label": spec.label,
                    "mode": spec.mode,
                    "region": spec.region,
                    "severity": spec.severity,
                    "defect_attribute": spec.defect_attribute,
                    "sibling_id": spec.sibling_id,
                    "rel_path": rel,
                    "description": spec.description,
                }
            )

    catalog = {
        "n_modules": len(specs),
        "n_per_category": 60,
        "defective_fraction_target": 0.60,
        "categories": list(CATEGORIES),
        "ethics": "evaluation_only_no_apply",
        "scale_note": (
            "(36 insecure + 24 secure per category)."
        ),
        "counts": {},
    }
    for category in CATEGORIES:
        rows = [s for s in specs if s.category == category]
        insecure = sum(1 for s in rows if s.label == "insecure")
        catalog["counts"][category] = {
            "n": len(rows),
            "insecure": insecure,
            "secure": len(rows) - insecure,
            "defective_fraction": insecure / len(rows),
        }
    (corpus / "catalog.json").write_text(
        json.dumps(catalog, indent=2) + "\n", encoding="utf-8"
    )
    return specs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "corpus",
        help="Corpus output directory",
    )
    args = parser.parse_args()
    specs = write_corpus(args.out)
    insecure = sum(1 for s in specs if s.label == "insecure")
    print(f"wrote {len(specs)} modules ({insecure} insecure) -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
