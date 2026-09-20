# Project Status

**Student:** Rasool Basha Durbesula (24205478)  
**Project:** Partition-Key Design and Capacity Mode in Amazon DynamoDB: An Empirical Performance-Cost Evaluation under Serverless Workloads  
**Date:** September 2026

## Executive Summary

**CA2 alignment < 100%. Not SUBMIT-READY.**

Artefact (Terraform, Lambda workloads, Zipfian generator, cost model, ANOVA pipeline, moto unit tests) is implemented. **No filled factorial campaign cells** (`results/` schema-only; `cell_summary.md` = `[TO BE FILLED FROM EXPERIMENT]`). Claim hygiene pass treats empty cells as the **live AWS residual**, not as inventable moto numbers.

## Research alignment (claim hygiene)

| Item | Status |
|------|--------|
| CA2 factorial K1–K3 × on-demand/provisioned × W1–W4 | Designed in `config/experiment.yaml`; **not live-run** |
| Evaluation tables | Placeholders only (`evaluation.tex`, `cell_summary.md`) — **no invented fills** |
| K4 adaptive sharding | Code presence only — **off CA2 factorial**; **no dominance claims** |
| Live Cost Explorer validation | **Not claimed** — no Cost Explorer artefact |
| DOI notes | Wired `references.bib` has `note={doi:…}` (or explicit `doi: none` + url for USENIX/CIDR) |
| IaC tags | `project` / `managed_by` / `purpose` / `data` only — **no student name/ID** |
| STATUS honesty | **<100%**; sole hard residual = live DynamoDB campaign |

**Alignment after claim hygiene:** ~**78%** (was ~74%). Compact: `RQ8 Obj10 Method13 Impl13 Exp4 Metrics8 Evidence7 Claims7 Rubric8` → ~78/100.

## What Has Been Completed

### 1. Research Design
- Factorial: 3 × 2 × 4 (K1/K2/K3 × capacity × W1–W4)
- Baseline: Pantelić et al. (2026)
- Statistical plan: two-way ANOVA + Tukey / Holm–Bonferroni (code + unit tests)
- Ethics: synthetic data notes

### 2. Artefact Implementation
- Terraform under `iac/` (six tables; Lambda; IAM; CloudWatch; S3; budgets)
- Workload generators, profiles W1–W4, seed, metrics/cost analysis
- pytest suite against **moto** (plumbing only)
- Config externalised (`config/experiment.yaml`, `config/prices.yaml`)

### 3. Testing and Validation (moto unit tests)
- Tests validate pipeline behaviour against the emulator
- Moto does **not** replicate network latency, adaptive/burst capacity, or auto-scaling delays
- Fixture ANOVA significance ≠ DynamoDB finding

## What Is NOT Complete (sole AWS residual)

1. **Live AWS DynamoDB K1–K3 factorial campaign** — fill `results/` / replace placeholders (AWS residual = empty cells)

Non-AWS claim blockers cleared this pass: practitioner overclaim demoted; K4 quarantined; DOI notes complete; Cost Explorer not claimed.

## Data and Results

### Current state: placeholders only

- No production DynamoDB measurements committed
- Cost model uses list-price YAML; **not** Cost Explorer–validated
- `rassool_final_report.md` K4 win rhetoric remains **quarantined**

### IaC tagging (verified)

```
project = dynamodb-pk-capacity
managed_by = terraform
purpose = research-eval
data = synthetic
```

No `student` / student-ID tags in Terraform.

## Gate

```
GATE_READY=yes AWS_CLASS=required SOLE_AWS_RESIDUAL=yes READY_FOR_AWS=yes
```

**Do not** terraform apply until budget/alignment operators start the live campaign. Do not invent cell values.

**Last Updated:** 2026-09-20  
**Status:** Claim hygiene raised (~78%); CA2 **not** 100%; sole residual = live DDB
