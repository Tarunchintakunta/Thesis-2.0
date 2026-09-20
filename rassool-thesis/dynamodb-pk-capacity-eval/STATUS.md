# Project Status

**Student:** Rasool Basha Durbesula (24205478)  
**Project:** Partition-Key Design and Capacity Mode in Amazon DynamoDB: An Empirical Performance-Cost Evaluation under Serverless Workloads  
**Date:** September 2026

## Executive Summary

**CA2 alignment < 100%. Not SUBMIT-READY / NOT COMPLETE.**

Artefact implemented. A **partial live DynamoDB key-cell round** (eu-west-1) filled the primary **W3/W4 × K1–K3 × on-demand/provisioned** cells (`results/batches.csv`, `data_source=live`, $n{=}1$, 100k seeded orders). **W1/W2**, full **$n{=}30$ / 1M seed**, and **ANOVA** remain unfilled. No moto invents.

## Research alignment (claim hygiene)

| Item | Status |
|------|--------|
| CA2 factorial K1–K3 × on-demand/provisioned × W1–W4 | **Partial live:** W3/W4 × 6 configs filled; W1/W2 empty |
| Evaluation tables | W3/W4 latency/throttle/cost filled from live CSV; ANOVA still placeholder |
| K4 adaptive sharding | Code presence only — **off CA2 factorial**; **no dominance claims** |
| Live Cost Explorer validation | **Not claimed** |
| DOI notes | Wired `references.bib` has `note={doi:…}` (or explicit `doi: none` + url) |
| IaC tags | `project` / `managed_by` / `purpose` / `data` only — **no student name/ID** |
| STATUS honesty | **<100%**; residual = finish factorial + replication |

**Alignment after key-cell round:** ~**88%** (was ~78% with empty cells). Compact: `RQ8 Obj10 Method13 Impl13 Exp8 Metrics9 Evidence9 Claims8 Rubric10` → ~88/100.

## What Has Been Completed

### 1. Research Design
- Factorial: 3 × 2 × 4 (K1/K2/K3 × capacity × W1–W4)
- Baseline: Pantelić et al. (2026)
- Statistical plan: two-way ANOVA + Tukey / Holm–Bonferroni (code + unit tests; needs $n{\ge}2$)

### 2. Artefact Implementation
- Terraform under `iac/` (six tables; Lambda; IAM; CloudWatch; S3; budgets)
- Workload generators, profiles W1–W4, seed, metrics/cost analysis
- `run_matrix.py --key-designs` filters to CA2 K1–K3 (excludes off-factorial K4 tables)

### 3. Live key-cell round (2026-09-20)
- Applied: 6× DynamoDB (`ddbpk-k{1,2,3}-{ondemand,provisioned}`), Lambda `ddbpk-driver`, S3 `ddbpk-results-*`, CW dashboard `ddbpk`
- Seed: 100,000 items × 6 tables; matrix: 1 block × W3,W4 × K1–K3 × 2 modes = **12 live batches**
- Artefacts: `results/batches.csv`, `results/cloudwatch.csv`, `results/raw/*.csv.gz`, `report/generated/cell_summary.md`
- Headline (live): W3 mean latency ~4.3–5.0 ms (K1/K2) / ~4.9–5.0 ms (K3); W4 mean ~4.6–5.4 ms; **throttle_rate = 0** all 12 cells; K3 on-demand cost/10k ≈ \$0.007 vs K1/K2 ≈ \$0.0039
- Stack **destroyed after round** (see `results/keycell_destroy.log`)

### 4. Testing (moto)
- Pytest validates pipeline against emulator only

## What Is NOT Complete

1. **W1/W2 live cells** (still empty)
2. **Full campaign** ($n{=}30$, 1M seed, all four workloads) for power/ANOVA
3. Cost Explorer validation (not claimed)

## Gate

```
GATE_READY=yes AWS_CLASS=required SOLE_AWS_RESIDUAL=partial READY_FOR_AWS=yes COMPLETE=no
```

**Last Updated:** 2026-09-20  
**Status:** Partial live W3/W4 key-cells filled; CA2 **NOT COMPLETE**
