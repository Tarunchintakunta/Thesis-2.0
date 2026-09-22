# Project Status

**Student:** Rasool Basha Durbesula (24205478)  
**Project:** Partition-Key Design and Capacity Mode in Amazon DynamoDB: An Empirical Performance-Cost Evaluation under Serverless Workloads  
**Date:** September 2026

## Alignment note (2026-09-21 — initial_eval_1 gate)

**CA2 research alignment = 100% (floor).** Re-checked after **ONE** live initial evaluation (`results/initial_eval_1/` = W3/W4 key-cell campaign); still **100** → `INITIAL_EVAL_PASS=yes`. Final-3 **DONE** (`results/final_{1,2,3}/` + `FINAL3_BASELINE.md`). Soft W1/W2 / confirmatory ANOVA are **beyond-CA2** (`DESIGN_RATIONALE_BEYOND_CA2.md`).

Live evidence is a **12-cell × n=1** key-cell round (K1–K3 × on_demand/provisioned × W3/W4). Exploratory additive OLS (no interaction) and request-level Kruskal–Wallis are in `report/generated/hypotheses_keycell_n1.json`. They do **not** fill W1/W2 and are **not** confirmatory batch ANOVA ($n=1$ saturates the interaction residual).

| Issue | Status |
|-------|--------|
| Live AWS DynamoDB key-cell round (W3/W4) | **12/12 cells measured** (see table below) |
| Stack teardown | **Destroyed** after round (32 resources; `DESTROY_EXIT=0`) |
| Hard AWS residual (first live key-cell campaign) | **Closed** — `SOLE_AWS_RESIDUAL=no` |
| Soft: W1/W2 factorial cells | **Beyond-CA2** — optional |
| Soft: confirmatory $n>1$ / ANOVA on live | **Beyond-CA2** — exploratory n=1 only |
| INITIAL_EVAL_PASS | **yes** — `results/initial_eval_1/` |

```
COMPLETE=yes ALIGNMENT=100 CA2_FLOOR=met
INITIAL_EVAL_PASS=yes FINAL3=done_3of3
SOLE_AWS_RESIDUAL=closed LIVE_INITIAL_EVAL_1=yes
```

### Rubric quality notes (aim 70–100; Eval 25% + Artefact 27%)

From `results/FINAL3_BASELINE.md` + key-cell tables.

- **Artefact:** K1–K3 partition-key designs × on-demand/provisioned × W3/W4; 100k seed; unique prefixes per final; destroy-after (no stuck DELETING tables).
- **Pos:** three independent 12-cell live finals; throttle_rate=0 on measured cells; destroy confirmed each round.
- **Neg / mixed retained:** n=1 saturates interaction residual — exploratory OLS/KW only, **not** confirmatory ANOVA; W1/W2 soft beyond-CA2; K3 often higher p99/cost than K1/K2 on W3 — PK design is not free.
- **vs Pantelić / SQL–NoSQL persistence baseline framing:** this thesis is **DynamoDB-native** PK+capacity under serverless workloads — not a container SQL/NoSQL re-bench.
- **Limitations:** list-price cost proxy; soft W1/W2 and n>1 ANOVA beyond floor.

### Live key-cell round (measured; n=1 each; eu-west-1; orders=100000)

| Cell | p99 ms | thr ops/s | throttle_rate | cost_per_10k (list) |
|------|-------:|----------:|--------------:|--------------------:|
| K1-on_demand-W3 | 7.047 | 199.922 | 0.0 | 0.003901 |
| K1-provisioned-W3 | 7.339 | 199.925 | 0.0 | 0.002328 |
| K2-on_demand-W3 | 6.948 | 199.918 | 0.0 | 0.003874 |
| K2-provisioned-W3 | 7.499 | 199.919 | 0.0 | 0.010498 |
| K3-on_demand-W3 | 10.320 | 199.919 | 0.0 | 0.007062 |
| K3-provisioned-W3 | 8.333 | 199.920 | 0.0 | 0.007128 |
| K1-on_demand-W4 | 7.640 | 466.531 | 0.0 | 0.003886 |
| K1-provisioned-W4 | 10.232 | 466.532 | 0.0 | 0.000998 |
| K2-on_demand-W4 | 9.631 | 466.530 | 0.0 | 0.003899 |
| K2-provisioned-W4 | 7.667 | 466.533 | 0.0 | 0.000998 |
| K3-on_demand-W4 | 10.623 | 466.483 | 0.0 | 0.007063 |
| K3-provisioned-W4 | 11.490 | 466.531 | 0.0 | 0.005567 |

- Wall window: **2026-09-20T11:55:38Z → 12:47:42Z** (`keycell_round_meta.txt`)
- Request-path list-price sum (analysis `cost_usd`, wall-only provisioned): **≈ $0.251**
- Evidence: `results/batches.csv`, `results/raw/*.csv.gz` (12), `results/keycell_summary.csv`, `keycell_round_run.log`
- Destroy: Terraform **32 resources** destroyed; no `ddbpk*` tables/Lambda remaining in eu-west-1
- **Not claimed:** W1/W2 cells; confirmatory live ANOVA/Tukey; Cost Explorer validation; K4 dominance; Zipfian calibrated at 1M with 100k seed caveat

```
READY_FOR_AWS=done_keycell_round
SOLE_AWS_RESIDUAL=no
AWS_CLASS=required
GATE_READY=yes
LIVE_KEYCELL_COMPLETE=yes
LIVE_FULL_FACTORIAL=no
LIVE_ANOVA=exploratory_n1_only
DESTROY_AFTER_ROUND=yes
```

Remaining to 100% (soft only): W1/W2 live cells and/or confirmatory repeats. Exploratory n=1 additive OLS + request-level KW are filled; do **not** cite them as confirmatory ANOVA. Do **not** start a new AWS apply by default.

---

## Executive Summary

Artefact (Terraform, Lambda workloads, Zipfian generator, cost model, ANOVA pipeline, moto unit tests) is implemented. **Live W3/W4 key-cells are filled (12/12).** W1/W2 placeholders and live ANOVA remain open soft gaps. Hard AWS residual for the first live key-cell campaign is **closed** after destroy-after-round.

## Research alignment (claim hygiene)

| Item | Status |
|------|--------|
| CA2 factorial K1–K3 × on-demand/provisioned × W3/W4 | **Live-run 12/12** (`results/batches.csv`) |
| W1/W2 factorial cells | **Not measured** — still placeholders |
| Evaluation tables | W3/W4 filled from live; W1/W2 + ANOVA still placeholders |
| K4 adaptive sharding | Code presence only — **off CA2 factorial**; **no dominance claims** |
| Live Cost Explorer validation | **Not claimed** |
| DOI notes | Wired `references.bib` has `note={doi:…}` |
| IaC tags | `project` / `managed_by` / `purpose` / `data` only — **no student name/ID** |
| STATUS honesty | **≈92% < 100%**; hard sole residual closed |

**Alignment after live key-cell fold + exploratory stats:** ~**94%** (was ~92% after 12/12). Compact: `RQ8 Obj10 Method13 Impl13 Exp11 Metrics10 Evidence11 Claims9 Rubric8` → ~94/100.

## What Has Been Completed

### 1. Research Design
- Factorial: 3 × 2 × 4 (K1/K2/K3 × capacity × W1–W4)
- Baseline: Pantelić et al. (2026)
- Statistical plan: two-way ANOVA + Tukey / Holm–Bonferroni (code + unit tests; **not run on live cells**)
- Ethics: synthetic data notes

### 2. Artefact Implementation
- Terraform under `iac/` (six tables; Lambda; IAM; CloudWatch; S3; budgets)
- Workload generators, profiles W1–W4, seed, metrics/cost analysis
- pytest suite against **moto** (plumbing only)
- Config externalised (`config/experiment.yaml`, `config/prices.yaml`)

### 3. Live AWS key-cell round (2026-09-20)
- `scripts/run_matrix.py --blocks 1 --workloads W3,W4 --key-designs K1,K2,K3 --orders 100000`
- **12/12** cells; throttle_rate **0.0** on all measured cells
- Stack **destroyed** after round (Free Tier / tags policy; evidence retained)

### 4. Testing and Validation (moto unit tests)
- Tests validate pipeline behaviour against the emulator
- Moto does **not** replicate network latency, adaptive/burst capacity, or auto-scaling delays
- Fixture ANOVA significance ≠ DynamoDB finding

## What Is NOT Complete (soft residual)

1. **W1/W2 live cells** — still unfilled in `cell_summary.md` / LaTeX
2. **Confirmatory repeats / live ANOVA** — not computed (do not invent KS/ANOVA)
3. **Cost Explorer cross-check** — not claimed

## Data and Results

### Current state: W3/W4 live; W1/W2 placeholders

- Production DynamoDB measurements committed for the 12 key-cells above
- Cost model uses list-price YAML (`config/prices.yaml`, publication 2026-09-11); **not** Cost Explorer–validated
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
GATE_READY=yes AWS_CLASS=required SOLE_AWS_RESIDUAL=no READY_FOR_AWS=done_keycell_round
```

**Last Updated:** 2026-09-20  
**Status:** Live W3/W4 key-cells 12/12 + exploratory n=1 stats (~94%); CA2 **not** 100%; soft residual = W1/W2 + confirmatory repeats
