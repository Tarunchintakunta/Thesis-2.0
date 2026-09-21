# Label-oracle checklist

Deterministic rules used to score each module against the published ground-truth
label in `labels.csv`. Inspect **only** `main.tf` for the module under test.

This stage is part of the labelled-oracle benchmark (alongside Checkov, tfsec and OPA).
Figures from this stage are cited as **label-oracle checklist** accuracy.

## Category checks (summary)

Apply the category sheet for the module’s labelled category (encryption, logging,
public access, IAM). Mark Fail if a required secure control is missing or an
insecure pattern matching the corpus construction rules is present; otherwise Pass.

Full item lists remain in this file’s historical sections below / category annexes
used by `scripts/` when generating checklist metrics.

## Scoring rule
- Predicted insecure if any critical Fail items fire for that category  
- Compare prediction to `labels.csv` for precision/recall/F1/FN  

Pinned tool versions for peer stages are recorded in `results/` manifests.
