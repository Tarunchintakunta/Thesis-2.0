# Vishvaksen alignment residual (formal CA2)

**Updated:** 2026-09-21  
**Formal file:** `vishvaksen-thesis/VishvaksenMachana_25173421_proposal.docx`  
**Alignment to formal CA2:** **~82/100** (was ~72 with dual-review artefact;
~62 scanner without dual-review; ~28 War-as-CA2)

## Compact
`RQ7 Obj9 Method10 Impl9 Exp7 Metrics10 Evidence10 Claims10 Rubric10` → **~82/100**

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
Checkov; tfsec; OPA; scripted checklist; **human-executable protocol + scoring
sheet** + NON-INDEPENDENT scripted sample sheets; pinned versions; remediation
LOC; provisional dual-review subsample JSON; **McNemar + Holm–Bonferroni
prose** vs Verdet).  
`iac-security/` is **PROXY** (STATUS redirect → `_superseded_proxy/iac-security/`,
War comment-ablation) and is **not** evidence.

## Closed this pass (honest)
- Checklist rater protocol + blank scoring sheet + labelled
  NON-INDEPENDENT / same-author scripted sample sheets
- Verdet comparison prose (Holm–Bonferroni / McNemar) from measured
  `mcnemar_pairs.csv` / `holm_bonferroni.csv` only — only checklist vs OPA
  rejects after correction

## Remaining blockers to 100%
1. Independent **human** checklist (protocol ready; sheets not human-filled)
2. Independent **second human** for 20% subsample (provisional same-author dual-pass exists)

**Do not claim 100%** while either human residual remains.

**AWS required:** **no** (do not apply)  
**Synthetic:** **not** a blocker
