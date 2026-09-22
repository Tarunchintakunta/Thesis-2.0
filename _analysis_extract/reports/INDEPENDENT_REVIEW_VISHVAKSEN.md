# Independent review — Vishvaksen (terraform-scanner-benchmark)

**Date:** 2026-09-22  
**STATUS claim:** `CA2 100%` — **mostly acceptable** for labelled-oracle method; soft on checklist circularity.  
**Honest CA2 floor:** **met (~90)**

## RQ (formal proposal)
> What percentage of the labelled AWS misconfigurations will be identified by Terraform security scanners and an enforced policy-as-code gate?

Objectives: labelled 4-category corpus; checklist / Checkov+tfsec / OPA; scan time + remediation LOC; per-category P/R/F1.

## Artefact reality
`terraform-scanner-benchmark/` N=240 modules (`corpus/labels.csv`: 144 insecure / 96 secure; 60/category). War hybrid quarantined under `_superseded_proxy/`. Ethics: no terraform apply.

## Evidence (disk)

| Claim | Verdict | Path / numbers |
|-------|---------|----------------|
| Label-oracle checklist | **Demonstrated** | `results/metrics_per_category.csv`: P=0.951 R=0.8125 F1=**0.876** identified **81.25%** |
| Checkov 3.3.19 | **Demonstrated** | R=**0.5625** F1=0.651 identified 56.25% |
| tfsec v1.28.14 | **Demonstrated** | R=0.618 F1=0.693 identified 61.81% |
| Static union | **Demonstrated** | R=0.708 F1=**0.718** identified **70.83%** |
| OPA gate | **Demonstrated** | P=1.0 R=0.604 F1=0.753 identified 60.42% |
| Per-category + time + LOC | **Demonstrated** | same CSV; `scan_times.csv`; `remediation_loc_summary.csv` mean diff LOC ALL=**13.10** |
| Verdet-style McNemar+Holm | **Demonstrated** | `mcnemar_pairs.csv` / `holm_bonferroni.csv`: checklist vs OPA Holm reject; Checkov vs tfsec not |
| Final-3 | **Demonstrated (deterministic)** | `final_1|2|3/metrics_per_category.csv` identical hash — expected for fixed corpus+pins |

## Floor
**Met** for the labelled-oracle CA2. Caveat: checklist rules are aligned to published labels (high F1 partly by construction); scanner recall gaps are the real finding. Public-repo transfer not done (optional).

## Highest-value next steps
1. Hold checklist as calibration ceiling; lead report with scanner FN rates (Checkov misses ~43.75% of labelled defects).  
2. Optional transfer study on public Terraform repos.  
3. Keep proxy War hybrid quarantined.
