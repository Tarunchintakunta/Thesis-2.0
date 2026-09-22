# GENAI_HANDOFF.md — Vishvaksen (terraform-scanner-benchmark)

## 0. Document meta

| Field | Value |
|-------|-------|
| Student | Vishvaksen Machana |
| Artefact root | `vishvaksen-thesis/terraform-scanner-benchmark/` |
| Programme | MSc Cloud Computing Research Project |
| Honest CA2 floor | **met (~90)** — independent review 2026-09-22 |
| Eval completeness | **3 full-scale local finals done** (`results/final_1\|2\|3/`) + `isolated_eval1/` |
| AWS | **N/A — not required**; ethics: **no terraform apply** |
| Handoff date | 2026-09-22 |
| Authority | `CA2_COMMITMENTS.md`, `_analysis_extract/reports/INDEPENDENT_REVIEW_VISHVAKSEN.md`, on-disk `results/` |

## 1. Research problem, motivation, research question, and objectives

**RQ:** What percentage of the labelled AWS misconfigurations will be identified by Terraform security scanners and an enforced policy-as-code gate?

**Objectives:** labelled 4-category corpus (N=240); checklist / Checkov+tfsec / OPA; scan time + remediation LOC; per-category P/R/F1.

## 2. Identified literature gap and how this research addresses it

Gap vs Verdet-style scanner papers: missing labelled recall/F1 on known Terraform defects. Method anchors: Rahman/GLITCH-style labelled oracle.

## 3. CA2 proposal alignment and any extensions beyond the proposal

Aligned labelled-oracle method. War hybrid quarantined under `_superseded_proxy/iac-security/` (**not evidence**). Public-repo transfer optional beyond-CA2 (not done).

## 4. Research methodology and experimental design

Fixed labelled corpus (`corpus/labels.csv`: 144 insecure / 96 secure; 60/category). Stages scored vs labels. Pinned tools in `tool_versions.json`. McNemar+Holm on stage pairs.

## 5. Artefact purpose and artefact-only project structure

```
terraform-scanner-benchmark/
  corpus/ mappings/ policies/ src/ scripts/ results/ tests/
```

## 6. AWS architecture, services, configurations, and experimental setup

**N/A — AWS not required / not applied.** No `terraform apply`.

## 7. Evaluation metrics and why they were selected

P/R/F1/FN + identified % answer the RQ; per-category splits; scan time and remediation LOC for operational objectives.

## 8. Baseline definition and baseline comparison

Checklist = calibration ceiling (partly label-aligned). Checkov/tfsec/static_union/OPA = measurement targets. **Scanner FN rates are the finding.**

## 9. Complete evaluation process and number of runs

`results/final_1|2|3/` + `isolated_eval1/`. Final-3 deterministic (identical metrics expected for fixed corpus+pins).

## 10. Final results and key findings (committed evidence)

From `results/final_1/metrics_per_category.csv` (ALL):

| Stage | Precision | Recall | F1 | Identified % |
|-------|----------:|-------:|---:|-------------:|
| checklist | 0.951 | 0.8125 | 0.876 | **81.25** |
| checkov | 0.771 | **0.5625** | 0.651 | **56.25** |
| tfsec | 0.788 | 0.6181 | 0.693 | **61.81** |
| static_union | 0.729 | 0.7083 | 0.718 | **70.83** |
| opa | 1.000 | 0.6042 | 0.753 | **60.42** |

Pins: Checkov **3.3.19**, OPA **1.4.2**. Remediation mean diff LOC ALL ≈ **13.10**.

## 11. How results satisfy or address each research objective

All four objectives Demonstrated on disk (corpus, stage metrics, scan_times, remediation LOC, per-category CSV).

## 12. How results answer the research question

Scanners alone identify ~56–62% of labelled defects; union ~71%; OPA ~60% at P=1.0; checklist ~81%. **Low scanner % = FN finding.**

## 13. How findings relate to the literature gap and previous research

Supplies labelled recall/F1 often omitted; do not market checklist F1 as scanner performance.

## 14. Statistical analysis and significance

McNemar+Holm: checklist vs OPA rejects; Checkov vs tfsec does not (independent review).

## 15. Important observations, trends, positive/negative findings, and anomalies

Positive: pinned reproducible pipeline; OPA precision 1.0; union lifts recall. Negative: Checkov misses ~43.75% labelled defects. Caveat: checklist circularity; no public-repo transfer.

## 16. Limitations, validity, reproducibility, and generalisability

Purpose-built labels; local-only; deterministic final-3; checklist ≠ scanner efficacy.

## 17. Final conclusions and research contribution

Quantified identification rates of Checkov/tfsec/OPA against a labelled AWS Terraform oracle; large FN residue remains.

## 18. What changed or improved during the evaluation process

War hybrid quarantined; formal labelled-oracle CA2 locked; isolated_eval1 confirms Checkov gap; honest floor ~90.

## 19. Remaining issues or recommended future work

Lead with scanner FN rates; optional public corpus transfer; keep proxy quarantined.

## 20. Important files, scripts, configurations, datasets, and artefacts to reproduce/continue

| Item | Path |
|------|------|
| CA2 | `vishvaksen-thesis/CA2_COMMITMENTS.md` |
| Labels | `corpus/labels.csv` |
| Evidence | `results/final_{1,2,3}/`, `FINAL3_BASELINE.md`, `isolated_eval1/` |
| Review | `_analysis_extract/reports/INDEPENDENT_REVIEW_VISHVAKSEN.md` |
