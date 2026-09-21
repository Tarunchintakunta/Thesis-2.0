# Second-reviewer protocol

Formal CA2: labels prepared before tools run; **20% subsample** labelled for
inter-reviewer agreement (Cohen’s κ).

## Procedure (independent human — definitive)

1. Draw a stratified random 20% sample (12 modules per category; 48 total)
   with seed recorded in `results/second_review_sample.csv`.
2. Hide `label`, `severity`, and sibling fields. Provide only `main.tf` and
   the category name.
3. Second reviewer fills `docs/MANUAL_CHECKLIST.md` (Pass/Fail + notes).
4. Compute Cohen’s κ on insecure vs secure.
5. Disagreements go to a reconciliation log; original generator labels remain
   the scoring oracle unless a generator bug is proven.

## Provisional same-author dual-pass (this raise)

When no second human is available, `scripts/run_second_review.py` records a
**provisional** dual-pass:

| Role | Who | Method |
|------|-----|--------|
| Reviewer A | Generator oracle | `corpus/labels.csv` |
| Reviewer B | Same author | Checklist heuristics on `main.tf` only (blind to CSV label) |

Outputs:
- `results/second_review_subsample.json`
- `results/second_review_sample.csv`
- `results/second_review_STATUS.md` (**PROVISIONAL**)

**Honesty rule:** provisional κ must never be presented as independent human
agreement. Replace with a second human before claiming definitive reliability.

Human checklist sheets: use `docs/CHECKLIST_SCORING_SHEET.md` with
`docs/MANUAL_CHECKLIST.md`. Scripted sample fills are
`docs/CHECKLIST_SAMPLE_FILLED_NONINDEPENDENT.md` (format only).
