**INITIAL_EVAL_PASS:** **yes** (full live campaign N=1000×3×3 as initial confirmation; CA2 still 100%)
INITIAL_EVAL_PASS=yes
Final-3: not started as separate post-gate series (campaign is the factorial evidence pack).

# Project Status — Artefact and Evaluation

**Student:** Vikas Reddy Amanagantti (X25178849)  
**Project:** An Empirical Evaluation of Application-Level Idempotency Strategies for Retry Correctness on AWS Lambda and Amazon DynamoDB  
**Last updated:** 2026-09-21  
**CA2 alignment (formal):** **100/100** — live full campaign complete (`_analysis_extract/reports/vikas_alignment.md`)

---

## Summary

Controlled retry experiment for **P1 / P2 / P3 only** (plain put, conditional put, idempotency-key) on stock AWS Lambda + DynamoDB.

| Evidence | Status | May answer RQ? |
|----------|--------|----------------|
| Moto functional (`results/moto/`) | Complete | **No** — plumbing / correctness check only; not AWS latency or capacity |
| Live pilot (`data/runs/live/pilot/`, `results/live/pilot_*`) | Complete (2026-09-19, eu-west-1, mult=2, 150 req) | **Partial** — sizing + directional duplicate behaviour at mult=2 only |
| Live full campaign (`data/runs/live/campaign/`) | **Complete** (2026-09-21, N=1000 × 3 paths × 3 mult, 24000 deliveries) | **Yes** — primary AWS factorial answer |
| Live sensitivity (`data/runs/live/sensitivity/`) | Complete (P3 `p3_between`, 1400 deliveries) | Supports E2 crash-between contrast |
| Live analysis (`results/live/summary.md`, cells, figures) | Complete; E1–E3 all **supported** | Primary Evaluation tables |
| P4 / `TransactWriteItems` | **Out of scope** | Quarantined — CA2 / ASSUMPTIONS A12 / `experiment.yaml` = P1–P3 only |

**Sole AWS residual closed:** live full campaign executed, analysed, stack destroyed.

---

## What has been completed

### Artefact (P1–P3)

- Three write paths in `src/lambda_fn/paths.py` / `handler.py` (primary experiment)
- Injected after-commit timeout driver + Streams ground truth
- Analysis pipeline (pilot sizing, z-tests / χ² / Mann–Whitney, Holm–Bonferroni)
- Terraform IaC (`infra/`) — tags: `project` / `managed_by` / `purpose` / `data` only; **no student name or student ID**
- Config pinned in `config/versions.yaml`; Configuration Manual present
- Tests: 63 pytest tests (STATUS claim; verify with `make test`)

### Moto functional validation (NOT the RQ answer)

- Full factorial N=30/cell; P1 100% dups; P2/P3 0% at mult 2 and 5
- Latency/capacity on moto are **not** AWS measurements
- Outputs: `results/moto/summary.md`, `figures/moto/*`

### Live AWS pilot (sizing)

- Run 2026-09-19T09:38:51+00:00; 150 requests / 300 invocations; multiplicity 2
- Pilot chose **N = 1000** (binding: P2 latency req 392) — `results/live/pilot_choice.json`

### Live AWS full campaign (primary RQ answer) — 2026-09-21

- Region **eu-west-1**; seed **25178849**; workers **6** (account `ConcurrentExecutions=10` Free-Tier guard; Makefile default `WORKERS=4`)
- **N=1000** × paths {P1,P2,P3} × multiplicities {1,2,5} = **9000 requests / 24000 deliveries**; **0** driver errors
- Streams: 21387 campaign stream records; CloudWatch cross-check: invocations match; WCU matches reported+rule
- Sensitivity: 400 requests / 1400 deliveries (P3 × {2,5}, `p3_between`)
- Analysis: `results/live/summary.md`, `cells.csv`, `figures/live/{dup_rate,latency,capacity,surface}.png`
- Pre-registered **E1 / E2 / E3 all supported**
- Headline cells: P1 dup_rate = 1.0 at mult 2 and 5; P2/P3 dup_rate = 0.0; P3 capacity = P2 + 2 WCU/request
- **Stack destroyed** after fold (terraform destroy 8 resources; Lambda/table/role/alarms/log group verified absent)

---

## P4 / TransactWrite — OUT OF SCOPE (quarantined)

- CA2, master prompt, ASSUMPTIONS A12, and `config/experiment.yaml` register **P1, P2, P3 only**
- Any `TransactWriteItems` / P4 narrative in `vikas_final_report.md` is **NON-AUTHORITATIVE**
- Multi-item transactions remain **future work** in the LaTeX report

---

## Moto vs pilot vs campaign

| Aspect | Moto | Live pilot | Live campaign |
|--------|------|------------|---------------|
| Duplicate-rate plumbing | Validated | Partial (mult=2) | **Complete** |
| Latency / capacity for RQ | Unusable | Pilot means only | **Complete** (CIs + Holm) |
| E1/E2/E3 pre-registered decisions | Moto-only | Sizing only | **All supported** |
| Suitable as paper primary results | No | No (partial) | **Yes** |

---

## Next steps (optional / soft)

1. Fold live cells into LaTeX Evaluation as primary tables (moto stays functional-only)
2. Soft: DOI `note={doi:}` hygiene in bibliography

---

## References for this status document

- Wen, J., et al. (2025) Unveiling overlooked performance variance in serverless computing. *EMSE*. doi:10.1007/s10664-025-10615-3
- Qi, S., et al. (2025) Efficient fault tolerance for stateful serverless computing with asymmetric logging. *TOCS*. doi:10.1145/3725985

---

Vikas Reddy Amanagantti
