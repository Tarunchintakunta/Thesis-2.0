# CA2 Commitments — Vishvaksen (formal)

**Source:** Formal CA2 `vishvaksen-thesis/VishvaksenMachana_25173421_proposal.docx`  
(*Evaluation of Terraform Security Scanners and Policy-as-Code Gates…*).  
**Status:** Binding research contract = **formal CA2**. Artefact = `terraform-scanner-benchmark/`.  
War comment-ablation hybrid is quarantined at `_superseded_proxy/iac-security/` (**not** this CA2).  
**AWS deploy / apply:** **Not required.** Ethics: evaluation-only corpus — **no live infrastructure is applied.**

## Method framing (binding — no live human raters)

This thesis uses a **labelled oracle corpus** (Rahman/GLITCH-style): each Terraform module carries a known secure/insecure ground-truth label written at construction time.  
Detection stages are scored **against those labels only**:

1. Deterministic **label-oracle checklist** (rule/heuristic pass aligned to the published labels)  
2. Static scanners (**Checkov** + **tfsec**)  
3. **OPA/Rego** policy-as-code CI gate  

Live independent human reviewers are **out of scope** for this project and are **not** part of the evaluation design or thesis claims.

## Research question (formal)
What percentage of the labelled AWS misconfigurations will be identified by Terraform security scanners and an enforced policy-as-code gate?

## Objectives (must evidence)
1. Build a **labelled** set of secure/insecure Terraform modules in **four** AWS misconfiguration categories (~60 modules/category; ~60% defective).  
2. Measure detection accuracy of the **label-oracle checklist**, **static scanning (Checkov + tfsec)**, and an **OPA/Rego CI gate** on identical inputs.  
3. Record **scan time** and **remediation effort** (LOC diff secure↔insecure) per stage.  
4. Report precision / recall / F1 / false-negative rate **per category** (not only macro averages).

## Baseline (formal)
Verdet et al. (2025) — gap is missing labelled recall/F1 on known Terraform defects; Rahman/GLITCH cited as **oracle-labelling** methodology anchors (not live dual-human panels).

## Variables / metrics
| Metric | Formal commitment |
|--------|-------------------|
| Precision, Recall, F1, FN rate | Per stage × category |
| Severity coverage | Required |
| Scan time / module | Required |
| Remediation effort (diff LOC) | Required |

## Non-goals / honesty
- Prior proxy “War comment-ablation + TF-IDF hybrid” is **not** this CA2 (`_superseded_proxy/`).  
- Synthetic labelled modules are **not** a blocker (formal corpus is purpose-built synthetic).  
- Fine-tuned CodeBERT / Ansible-Puppet smell detection is out of scope.  
- Live human dual-review panels are **out of scope** and must not appear in thesis claims.
