# Second-reviewer protocol (not executed this pass)

Formal CA2: labels prepared before tools run; **20% subsample independently
labelled** for inter-reviewer agreement.

## Procedure (when a second reviewer is available)

1. Draw a stratified random 20% sample (12 modules per category; 48 total)
   with seed recorded in `results/second_review_sample.csv`.
2. Hide `label`, `severity`, and sibling fields. Provide only `main.tf` and
   the category name.
3. Second reviewer fills `docs/MANUAL_CHECKLIST.md` (Pass/Fail + notes).
4. Compute Cohen’s κ on insecure vs secure.
5. Disagreements go to a reconciliation log; original generator labels remain
   the scoring oracle unless a generator bug is proven.

## This pass

**NOT RUN.** No second human. `results/second_review_STATUS.md` records the
gap. Do not invent κ.
