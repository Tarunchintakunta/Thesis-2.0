# Final report pointer — Vishvaksen (formal CA2)

Binding study: **Evaluation of Terraform Security Scanners and Policy-as-Code
Gates for AWS Infrastructure-as-Code Misconfiguration Detection**.

Implementation: `terraform-scanner-benchmark/`.  
Numbers: `terraform-scanner-benchmark/results/METRICS.md` (N=240; Checkov
recall 56.2%; tfsec 61.8%; union 70.8%; OPA 60.4%; scripted checklist 81.2%).

### Verdet-aligned paired tests (evidence-only)

McNemar on 144 insecure modules + Holm–Bonferroni (α=0.05, m=4): see
`terraform-scanner-benchmark/docs/VERDET_COMPARISON.md` and
`latex/verdet_comparison.tex`. After correction, **only** checklist vs OPA
is significant (adjusted p=7.45×10⁻⁹). Checkov vs tfsec p=0.229 (n.s.).

### Manual checklist artefact

Human-executable protocol: `docs/MANUAL_CHECKLIST.md` + blank
`docs/CHECKLIST_SCORING_SHEET.md`. Sample filled sheets are
**NON-INDEPENDENT / same-author (scripted)** —
`docs/CHECKLIST_SAMPLE_FILLED_NONINDEPENDENT.md`. Human pass **not run**.

War hybrid: `iac-security/STATUS.md` (PROXY) → `_superseded_proxy/iac-security/`
— **not** this CA2.

`terraform-scanner-benchmark/results/second_review_subsample.json`.

**Status:** NOT COMPLETE. Alignment **~82%**. AWS **not required**.
**Do not terraform apply.**

