# Baseline paper — Vishvaksen (formal CA2)

**Student folder:** `vishvaksen-thesis`  
**Citation:** Verdet, Hamdaqa, Da Silva & Khomh (2025) — *Assessing the
adoption of security policies by developers in Terraform across different
cloud providers.* Empirical Software Engineering 30(3), 74.
doi: 10.1007/s10664-024-10610-0

## File

Formal CA2 maps the **gap** to Verdet et al. (accuracy only on disputed
Checkov/tfsec cases; no labelled Terraform recall/F1). Rahman et al. (2023)
and Saavedra & Ferreira (2022) / GLITCH remain **oracle methodology**
anchors, not the Terraform scanner baseline.

The War et al. (2025) preprint was the **proxy-era** baseline and is
superseded for this CA2. PDF may still sit in this folder; do not treat it
as the binding gap.

## Problem → CA2 commitment

No published Terraform study reports recall/F1 against labelled ground
truth across manual review, Checkov/tfsec, and an OPA gate.

## Gap this artefact measures

Labelled secure/insecure AWS modules in four categories; per-category
P/R/F1/FN; scan time; remediation LOC.

## Metrics mapped to eval

| Paper / commitment | Ours |
|--------------------|------|
| Precision, recall (disputed subsample) | Precision, recall, F1, FN rate **per category** on a labelled corpus |
| Alert conflicts | Checkov vs tfsec McNemar on the same modules; Holm–Bonferroni on four pre-registered pairs (`docs/VERDET_COMPARISON.md`) |
| (none) scan time / LOC | `results/scan_times.csv`, `results/remediation_loc.csv` |

Evidence: `terraform-scanner-benchmark/results/` — **not**
`_superseded_proxy/iac-security/results/`.
