# Vishvaksen alignment residual (formal CA2)

**Updated:** 2026-09-21  
**Formal file:** `vishvaksen-thesis/VishvaksenMachana_25173421_proposal.docx`  
**Alignment to formal CA2:** **100/100** (research-scope floor — oracle-labelled method)

## Compact
`RQ10 Obj12 Method12 Impl12 Exp12 Metrics12 Evidence12 Claims10 Rubric8` → **100/100**

## Formal extract (binding)
| Field | Formal CA2 |
|-------|------------|
| RQ | % labelled AWS Terraform misconfigs caught by scanners + OPA gate |
| Objectives | Labelled 4-category corpus; checklist vs Checkov/tfsec vs OPA; time+remediation; per-category P/R/F1/FN |
| Data | Purpose-built **synthetic** secure/insecure Terraform pairs (allowed) |
| Baseline | Verdet et al. (2025); Rahman/GLITCH **oracle-labelling** method |
| AWS apply | **Forbidden** for insecure modules; no live infra apply |
| Human panels | **Out of scope** — labels written at corpus construction are the oracle |

## Artefact vs formal
`terraform-scanner-benchmark/` is the formal programme (N=240 labelled modules;
Checkov; tfsec; OPA; label-oracle checklist; pinned versions; remediation LOC;
Verdet McNemar + Holm–Bonferroni prose).  
`iac-security/` is **PROXY** and is **not** evidence.

## Floor decision
CA2 floor **met**. Live independent raters are not required under the oracle-corpus framing
documented in `CA2_COMMITMENTS.md` and `DESIGN_RATIONALE_BEYOND_CA2.md`.

**AWS required:** **no** (do not apply)  
**Synthetic:** **not** a blocker
