# Project Status — Artefact and Evaluation

**Student:** Vikas Reddy Amanagantti (X25178849)  
**Project:** An Empirical Evaluation of Application-Level Idempotency Strategies for Retry Correctness on AWS Lambda and Amazon DynamoDB  
**Last updated:** 2026-09-21  
**CA2 alignment (formal):** **~74/100** — evaluation scope unmet while live full campaign is empty (`_analysis_extract/reports/vikas_alignment.md`)

---

## Summary

Controlled retry experiment for **P1 / P2 / P3 only** (plain put, conditional put, idempotency-key) on stock AWS Lambda + DynamoDB.

| Evidence | Status | May answer RQ? |
|----------|--------|----------------|
| Moto functional (`results/moto/`) | Complete | **No** — plumbing / correctness check only; not AWS latency or capacity |
| Live pilot (`data/runs/live/pilot/`, `results/live/pilot_*`) | Complete (2026-09-19, eu-west-1, mult=2, 150 req) | **Partial** — sizing + directional duplicate behaviour at mult=2 only |
| Live full campaign (`data/runs/live/campaign/deliveries.jsonl`) | **Empty (0 bytes)** | **No** — schedule + ground_truth prepared; deliveries not executed |
| P4 / `TransactWriteItems` | **Out of scope** | Quarantined — CA2 / ASSUMPTIONS A12 / `experiment.yaml` = P1–P3 only |

**Sole residual to answer the CA2 RQ quantitatively on AWS:** run and analyse the live full campaign (N=1000 × 3 paths × 3 multiplicities), then replace moto-primary Evaluation tables with live cells.

---

## What has been completed

### Artefact (P1–P3)

- Three write paths in `src/lambda_fn/paths.py` / `handler.py` (primary experiment)
- Injected after-commit timeout driver + Streams ground truth
- Analysis pipeline (pilot sizing, z-tests / χ² / Mann–Whitney, Holm–Bonferroni)
- Terraform IaC (`infra/`) — tags: `project` / `managed_by` / `purpose` / `data` only; **no student name or student ID required**
- Config pinned in `config/versions.yaml`; Configuration Manual present
- Tests: 63 pytest tests (STATUS claim; verify with `make test`)

### Moto functional validation (NOT the RQ answer)

- Full factorial N=30/cell; P1 100% dups; P2/P3 0% at mult 2 and 5
- Latency/capacity on moto are **not AWS measurements**
- Outputs: `results/moto/summary.md`, `figures/moto/*`

### Live AWS pilot (partial evidence)

- Run 2026-09-19T09:38:51+00:00; 150 requests / 300 invocations; multiplicity 2
- Pilot chose **N = 1000** (binding: P2 latency req 392) — `results/live/pilot_choice.json`
- Pilot shows expected path behaviour directionally (P1 second writes; P2/P3 guarded) but is **not** a full factorial campaign answer

---

## What has NOT been done

### Live full campaign — EMPTY

- `data/runs/live/campaign/deliveries.jsonl` is **0 bytes**
- Schedule + ground_truth files exist; no campaign deliveries, no live `summary.md` / cells / figures for the full factorial
- Therefore: **do not treat moto or the live pilot as the full campaign answer**

### P4 / TransactWrite — OUT OF SCOPE (quarantined)

- CA2, master prompt, ASSUMPTIONS A12, and `config/experiment.yaml` register **P1, P2, P3 only**
- Any `TransactWriteItems` / P4 narrative in `vikas_final_report.md` is **NON-AUTHORITATIVE** and must not be cited as evaluation results
- Multi-item transactions remain **future work** in the LaTeX report

---

## Moto vs pilot vs campaign

| Aspect | Moto | Live pilot | Live campaign |
|--------|------|------------|---------------|
| Duplicate-rate plumbing | Validated | Partial (mult=2) | **Missing** |
| Latency / capacity for RQ | Unusable | Pilot means only; not full CIs across design | **Missing** |
| E1/E2/E3 pre-registered decisions | Moto-only | Sizing only | **Missing** |
| Suitable as paper primary results | No | No (partial) | Yes (when run) |

---

## Report claim hygiene (2026-09-20)

- LaTeX Evaluation: moto labeled functional-only; live pilot acknowledged; full campaign empty; P4 not claimed
- Abstract: does not assert completed full-campaign collection
- `vikas_final_report.md`: quarantined banner (P4 overclaims unsupported)
- Infra docs: no student-ID tag requirement

---

## Next steps (live AWS — not run in this pass)

1. `make campaign` with N from `pilot_choice.json`
2. Sensitivity + CloudWatch collect
3. `make analyse` → `results/live/` + `figures/live/`
4. Replace Evaluation primary tables with live cells

---

## References for this status document

- Wen, J., et al. (2025) Unveiling overlooked performance variance in serverless computing. *EMSE*. doi:10.1007/s10664-025-10615-3
- Qi, S., et al. (2025) Efficient fault tolerance for stateful serverless computing with asymmetric logging. *TOCS*. doi:10.1145/3725985

---

Vikas Reddy Amanagantti
