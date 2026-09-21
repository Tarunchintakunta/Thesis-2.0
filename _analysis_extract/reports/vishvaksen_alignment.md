# Vishvaksen alignment residual (formal CA2)

**Updated:** 2026-09-21  
**Formal file:** `vishvaksen-thesis/VishvaksenMachana_25173421_proposal.docx`  
**Alignment to formal CA2:** **~72/100** (was ~28 War-as-CA2; ~62 scanner without dual-review artefact)

## Compact
`RQ7 Obj8 Method7 Impl8 Exp7 Metrics8 Evidence7 Claims6 Rubric6` → **~72/100**

## Formal extract (binding)
| Field | Formal CA2 |
|-------|------------|
| RQ | % labelled AWS Terraform misconfigs caught by scanners + OPA gate |
| Objectives | Labelled 4-category corpus; manual vs Checkov/tfsec vs OPA; time+remediation; per-category P/R/F1/FN |
| Data | Purpose-built **synthetic** secure/insecure Terraform pairs (allowed) |
| Baseline | Verdet et al. (2025); Rahman/GLITCH oracle method |
| AWS apply | **Forbidden** for insecure modules; no live infra apply |

## Artefact vs formal
`terraform-scanner-benchmark/` is the formal programme (N=240 labelled modules;
Checkov; tfsec; OPA; scripted checklist; pinned versions; remediation LOC;
provisional dual-review subsample JSON).  
`iac-security/` is **PROXY** (STATUS redirect → `_superseded_proxy/iac-security/`,
War comment-ablation) and is **not** evidence.

## Remaining blockers to 100%
1. Independent **human** checklist (scripted ≠ human rater)
2. Independent **second human** for 20% subsample (provisional same-author dual-pass exists)
3. Thesis write-up vs Verdet (Holm–Bonferroni / McNemar in prose)

**AWS required:** **no** (do not apply)  
**Synthetic:** **not** a blocker
