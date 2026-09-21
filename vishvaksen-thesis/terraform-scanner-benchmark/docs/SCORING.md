# Scoring

Ground truth: `corpus/labels.csv` (`label=insecure` → y=1).

A stage **predicts positive** if:

| Stage | Positive rule |
|-------|----------------|
| checklist | Any checklist regex/absence item hits HCL text |
| checkov | ≥1 **failed** Checkov check whose ID is in `mappings/checkov_ids.json` for the module’s category |
| tfsec | ≥1 result whose rule id/long_id is in `mappings/tfsec_ids.json` for that category |
| static_union | checkov OR tfsec positive (formal “static scanning” stage) |
| opa | Category package `deny` is non-empty |

Findings whose check IDs are **not** in the category map are recorded in
`unmatched_check_ids` and are **not** counted. That avoids scoring missing
tags / versioning as if they were the labelled defect. The map is a priori
from shipped catalogs; after a first scan it may be extended only to
**classify catalog IDs**, not to retune labels.

Secure modules can still emit unrelated Checkov/tfsec noise; those IDs do
not count unless they sit in the same category map (possible false positives).

Metrics (per stage × category, and ALL): precision, recall, F1, false-negative
rate, Wilson 95% CI on recall. RQ “percentage identified” = recall × 100 on
labelled insecure modules.

Scan time: Checkov/tfsec **batch** wall-clock for the corpus plus mean
per-module seconds on a stratified sample (2 insecure + 1 secure per
category) because full 240× process start-up is not the interesting quantity.
OPA and checklist time every module.

Remediation effort: unified-diff line count between each insecure module and
its `sibling_id` secure variant.

McNemar: discordant insecure-module detections between paired stages
(stdlib binomial two-sided). Holm–Bonferroni (α=0.05) across the four
pre-registered pairs is written to `results/holm_bonferroni.csv` by
`scripts/evaluate.py`. Prose: `docs/VERDET_COMPARISON.md` and
`../latex/verdet_comparison.tex`.
