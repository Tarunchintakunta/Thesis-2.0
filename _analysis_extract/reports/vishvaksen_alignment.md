# Vishvaksen alignment residual (formal CA2)

**Updated:** 2026-09-20  
**Formal file:** `vishvaksen-thesis/VishvaksenMachana_25173421_proposal.docx`  
**Alignment to formal CA2:** **~28/100** (was ~86 vs superseded War comment-ablation proxy)

## Compact
`RQ3 Obj2 Method2 Impl5 Exp4 Metrics4 Evidence3 Claims2 Rubric3` → **~28/100**

## Formal extract (binding)
| Field | Formal CA2 |
|-------|------------|
| RQ | % labelled AWS Terraform misconfigs caught by scanners + OPA gate |
| Objectives | Labelled 4-category corpus; manual vs Checkov/tfsec vs OPA; time+remediation; per-category P/R/F1/FN |
| Data | Purpose-built **synthetic** secure/insecure Terraform pairs (allowed) |
| Baseline | Verdet et al. (2025); Rahman/GLITCH oracle method |
| AWS apply | **Forbidden** for insecure modules; no live infra apply |

## Artefact vs formal
`iac-security/` is a **different programme** (War comment-ablation + TF-IDF hybrid on synthetic snippets). Domain keyword overlap (IaC misconfiguration); tools/corpus/stages do **not** match formal Checkov/tfsec/OPA benchmark.

## True blockers to 100% (vs formal)
1. Labelled Terraform secure/insecure corpus (4 AWS categories) with dual review
2. Three-stage evaluation: manual checklist, Checkov+tfsec defaults, OPA/Rego CI gate
3. Per-category P/R/F1/FN + scan time + remediation LOC; pinned tool versions
4. Soft: retire War-hybrid-as-CA2 claims; publish corpus/policies/scripts

**AWS required:** **no** (do not apply)  
**Synthetic:** **not** a blocker (formal corpus is synthetic by design)
