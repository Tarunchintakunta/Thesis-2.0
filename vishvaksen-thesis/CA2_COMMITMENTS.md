# CA2 Commitments — Vishvaksen (formal)

**Source:** Derived from formal CA2 file `vishvaksen-thesis/VishvaksenMachana_25173421_proposal.docx` (*Evaluation of Terraform Security Scanners and Policy-as-Code Gates…*).  
**Status:** Binding research contract = **formal CA2**. Current `iac-security/` artefact implements a **different thesis** (War et al. comment-ablation hybrid) and does **not** satisfy this CA2.  
**AWS deploy / apply:** **Not required.** Formal ethics: corpus is evaluation-only; **“No live infrastructure is applied.”** Free-tier AWS may be used only for optional parse/validate. **Do not terraform-apply** insecure modules.

## Research question (formal)
What percentage of the labelled AWS misconfigurations will be identified by Terraform security scanners and an enforced policy-as-code gate?

## Objectives (must evidence)
1. Build a **labelled** set of secure/insecure Terraform modules in **four** AWS misconfiguration categories (~60 modules/category; ~60% defective; second-reviewer subsample).
2. Measure detection accuracy of **manual checklist review**, **static scanning (Checkov + tfsec)**, and an **OPA/Rego CI gate** on identical inputs.
3. Record **scan time** and **remediation effort** (LOC diff secure↔insecure) per stage.
4. Report precision / recall / F1 / false-negative rate **per category** (not only macro averages).

## Baseline (formal)
Verdet et al. (2025) Terraform security-policy adoption study — gap is missing labelled recall/F1 on known defects; Rahman/GLITCH cited as oracle methodology anchors.

## Variables / metrics
| Metric | Formal commitment |
|--------|-------------------|
| Precision, Recall, F1, FN rate | Per stage × category |
| Severity coverage | Required |
| Scan time / module | Required |
| Remediation effort (diff LOC) | Required |

## Non-goals / honesty
- Prior proxy “War comment-ablation + TF-IDF hybrid” is **not** this CA2.
- Synthetic labelled modules are **not** a blocker (formal corpus is purpose-built synthetic).
- Fine-tuned CodeBERT / Ansible-Puppet smell detection is out of scope for this formal CA2.
