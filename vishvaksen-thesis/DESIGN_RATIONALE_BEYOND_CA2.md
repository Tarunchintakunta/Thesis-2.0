# Design rationale — Vishvaksen

## Binding method
Evaluation uses a purpose-built **labelled oracle corpus**. Each module’s
secure/insecure label is fixed at construction. Precision, recall, F1 and
false-negative rates compare tool and checklist outputs to those labels
(Rahman/GLITCH-style IaC oracle benchmark).

## In scope
- Labelled N=240 AWS Terraform modules (four misconfiguration categories)
- Label-oracle checklist, Checkov, tfsec, OPA/Rego CI gate on identical inputs
- Scan time and remediation LOC
- Statistical comparison using measured contingency tables vs Verdet-style claims

## Ethics
Insecure modules are evaluation-only and are **never** applied to a live AWS account.

## Optional beyond-floor work
Transfer evaluation on public Terraform repositories; additional scanner versions.
