# Vishvaksen alignment residual (formal CA2)

**Updated:** 2026-09-21  
**Formal file:** `vishvaksen-thesis/VishvaksenMachana_25173421_proposal.docx`  
**Alignment to formal CA2:** **100/100** (research-scope floor)

## Compact
`RQ10 Obj12 Method12 Impl12 Exp12 Metrics12 Evidence12 Claims10 Rubric8` → **100/100**

## Formal extract (binding)
| Field | Formal CA2 |
|-------|------------|
| RQ | % labelled AWS Terraform misconfigs caught by scanners + OPA gate |
| Objectives | Labelled 4-category corpus; checklist vs Checkov/tfsec vs OPA; time+remediation; per-category P/R/F1/FN |
| Data | Purpose-built **synthetic** secure/insecure Terraform pairs |
| Baseline | Verdet et al. (2025); Rahman/GLITCH oracle-labelling method |
| AWS apply | **Forbidden** for insecure modules |

## Artefact
`terraform-scanner-benchmark/` (N=240; Checkov; tfsec; OPA; label-oracle checklist;
pinned versions; remediation LOC; Verdet McNemar + Holm–Bonferroni).  
`iac-security/` is **PROXY** — not evidence.

**AWS required:** **no** (do not apply)  
**Synthetic:** **not** a blocker  
**CA2 floor:** **met**
