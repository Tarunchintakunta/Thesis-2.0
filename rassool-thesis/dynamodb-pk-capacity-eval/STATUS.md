# Project Status

**Student:** Rasool Basha Durbesula (24205478)  
**Project:** Partition-Key Design and Capacity Mode in Amazon DynamoDB: An Empirical Performance-Cost Evaluation under Serverless Workloads  
**Date:** September 2026

## Executive Summary

**CA2 alignment < 100%. Not SUBMIT-READY.**

The artefact (Terraform, Lambda workloads, Zipfian generator, cost model, ANOVA pipeline, moto tests) is substantially implemented and documented. Evaluation evidence is **moto-only**: there is no filled live campaign (`results/` is schema-only; `cell_summary.md` remains `[TO BE FILLED FROM EXPERIMENT]`). Scientific claims about production DynamoDB latency/throttle/cost trade-offs are **not** established.

## Research alignment (claim hygiene)

| Item | Status |
|------|--------|
| CA2 factorial K1–K3 × on-demand/provisioned × W1–W4 | Designed in `config/experiment.yaml`; **not live-run** |
| K4 adaptive sharding | Code/design-check presence only — **off CA2 factorial**; **no dominance / empirical win claims** |
| Live Cost Explorer validation | **Not claimed** — no Cost Explorer artefact in-tree |
| IaC tags | `project` / `managed_by` / `purpose` / `data` only — **no student name/ID tags** |
| STATUS honesty | **<100%**; moto-only; live AWS residual remains |

## What Has Been Completed

### 1. Research Design
- Factorial experiment design: 3 × 2 × 4 (K1/K2/K3 × capacity × W1–W4)
- Baseline: Pantelić et al. (2026)
- Statistical plan: two-way ANOVA + Tukey / Holm–Bonferroni (code present)
- Ethics: synthetic data notes

### 2. Artefact Implementation
- Terraform under `iac/` (six tables for K1–K3 × two modes; Lambda; IAM; CloudWatch; S3; budgets)
- Workload generators (Zipfian), profiles W1–W4, seed, metrics/cost analysis
- pytest suite against **moto**
- Config externalised (`config/experiment.yaml`, `config/prices.yaml`)

### 3. Testing and Validation (moto)
- Tests validate pipeline behaviour against the emulator
- Moto does **not** replicate network latency, adaptive/burst capacity, or auto-scaling delays

## What Is NOT Complete (blockers)

1. **Live AWS DynamoDB campaign** — empty empirical cells (AWS residual)
2. Item-size sensitivity run (1/8/32 KB) — not executed on live service
3. Evaluation tables still `[MOTO SIM]` / unfilled
4. WhatsApp DOI `note={doi:...}` hygiene in wired `references.bib` (if required)
5. Side-doc K4 “dominance” narratives quarantined — must not re-enter LaTeX as evidence

## Data and Results

### Current state: moto simulation / placeholders only

- No production DynamoDB measurements committed
- Cost model uses list-price YAML; **not** “validated against AWS Cost Explorer in a pilot”
- `rassool_final_report.md` K4 win rhetoric is **quarantined** (unsupported; off-factorial)

### IaC tagging (verified)

```
project = dynamodb-pk-capacity
managed_by = terraform
purpose = research-eval
data = synthetic
```

No `student` / student-ID tags in Terraform.

## Honest assessment

- Artefact engineering: strong  
- Empirical CA2 answer (live latency × throttle × cost surface): **missing**  
- Alignment after claim hygiene: ~**74%** design/artefact credit; **not 100%**

**Do not** describe the project as SUBMIT-READY or production-ready science until live campaign results replace placeholders.

**Last Updated:** 2026-09-20  
**Status:** Claim hygiene raised; CA2 alignment **not** 100%; AWS residual **yes**
