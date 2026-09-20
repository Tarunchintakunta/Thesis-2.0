# Vishvaksen alignment residual (formal CA2)

**Updated:** 2026-09-20  
**Formal file:** `vishvaksen-thesis/VishvaksenMachana_25173421_proposal.docx`  
**Alignment to formal CA2:** **~62/100** (was ~28 when artefact was War hybrid)

## Compact
`RQ6 Obj7 Method6 Impl7 Exp6 Metrics7 Evidence6 Claims5 Rubric5` → **~62/100**

## Formal extract (binding)
| Field | Formal CA2 |
|-------|------------|
| RQ | % labelled AWS Terraform misconfigs caught by scanners + OPA gate |
| Objectives | Labelled 4-category corpus; manual vs Checkov/tfsec vs OPA; time+remediation; per-category P/R/F1/FN |
| Data | Purpose-built **synthetic** secure/insecure Terraform pairs (allowed) |
| Baseline | Verdet et al. (2025); Rahman/GLITCH oracle method |
| AWS apply | **Forbidden** for insecure modules; no live infra apply |

## Artefact vs formal
`terraform-scanner-benchmark/` is the formal programme (N=240 labelled
modules; Checkov; tfsec; OPA; scripted checklist).  
`_superseded_proxy/iac-security/` is a **different** programme (War
comment-ablation) and is **not** evidence.

## Remaining blockers to 100%
1. Independent human checklist (scripted regex ≠ human rater)
2. 20% second-reviewer subsample
3. Thesis write-up vs Verdet (Holm–Bonferroni / McNemar in prose)

**AWS required:** **no** (do not apply)  
**Synthetic:** **not** a blocker
