## Alignment note (2026-09-20, iter-2 — run-count reconcile)

**CA2 research alignment ≈ 90% — still < 100%. Sole hard residual = live SQS / CloudWatch key-cell campaign.**

Authoritative evidence: packaging-deduped `results/summary/stats_H1_H2_H3.json` (`runs: 350`, `backend: localsim`), `stats_H0_throughput_config.json`, `hypotheses.md`. Design cells = 350; on-disk manifests = 690 (adaptive_vt packaging twins). Loader: `analysis/load_results.py` (`dedupe_packaging_twins`).

| Issue | Status |
|-------|--------|
| Phase run-count table (350 vs 690) | **Reconciled** — design vs on-disk table in `evaluation.tex` + `results/README.md`; analysis dedupes |
| H1–H3 claim↔JSON (twin-inflated n=10) | **Fixed** — regeneratd stats: H3_recovery **fail to reject** after Holm ($p_{adj}=0.084$); twin $n=10$/$U=250$ withdrawn |
| DIVE / production overclaims | Softened; `adaptive_vt: false` / not evaluated |
| CA2 lit in bib | `note={doi:…}` present (AlSaid/Bosilia + baselines) |
| Obj4 cost as experimental claim | Softened: estimator-only |
| Live AWS SQS / CloudWatch | **Sole hard residual** — do not deploy until this STATUS says READY and operator starts AWS phase |

```
READY_FOR_AWS=yes
SOLE_AWS_RESIDUAL=yes
AWS_CLASS=required
GATE_READY=yes
```

Optional soft residual (not blocking AWS): dedicated adaptive_vt/DIVE campaign only if that claim is re-introduced.

---
# Project Status: Simulation vs Live AWS

**Student:** Anjaneya Reddy Gurram (24288853)  
**Project:** Reliability and Recovery of Amazon SQS Messaging under Injected Consumer and Downstream Failures  
**Last Updated:** September 20, 2026

## Executive Summary

This artefact has been developed with a **local simulator** that emulates SQS, Lambda, and DynamoDB behavior on a virtual clock. All experimental results, figures, and statistical analyses included in this submission are generated from **simulated runs**, not from live AWS infrastructure. **DIVE/adaptive_vt was not enabled** in the committed experiment matrix. Confirmatory statistics use **350 packaging-deduplicated design cells** (`repeats_per_cell: 5`); 690 on-disk manifest files include packaging twins and must not be counted as independent repeats.

## Implementation Status

### ✅ Completed (Simulated)

1. **Core Infrastructure**
   - AWS SAM template with SQS + DLQ, Lambda functions, DynamoDB table, SSM parameter
   - In-process fault injection switch (consumer kill, unhandled error, datastore reject/timeout)
   - Idempotency layer with deduplication tracking
   - Metrics collection and aggregation

2. **Local Simulator** (`src/localsim/`)
   - Discrete-event simulator with virtual clock
   - SQS Standard queue with configurable visibility timeout, maxReceiveCount, DLQ redrive
   - Lambda event source mapping with batch processing and partial failure reporting
   - DynamoDB state store simulation
   - Fault injection controller integrated with simulator

3. **Experiment Infrastructure** (`src/control/`)
   - Randomized config matrix generator
   - Manifest-based experiment runner with reproducible runs
   - Cost estimation and free-tier guard (for future live runs)
   - Metrics aggregator and summary generator
   - Terraform stack under `terraform/` (project tags only; **not applied**)

4. **Testing**
   - Unit tests for fault injection, metrics, SQS simulation, engine (`tests/unit/`)
   - Integration tests with moto for AWS service mocking (`tests/integration/`)
   - pytest suite with 100% pass rate in CI/CD (GitHub Actions)

5. **Experiments and Analysis** (ALL SIMULATED)
   - **Pilot** 18 design / 36 on-disk
   - **Baseline** 115 design / 230 on-disk
   - **Arms** 10 design / 10 on-disk
   - **Campaigns A–H** 187 design / 374 on-disk
   - **Burst** 20 design / 40 on-disk
   - **Hypothesis tests H1–H3** with Holm–Bonferroni on packaging-deduped rows
   - **Figures** (11 plots in `results/figures/`)

6. **Documentation**
   - Configuration manual (`docs/CONFIGURATION_MANUAL.md`)
   - Architecture design (`docs/ARCHITECTURE.md`)
   - Demo walkthrough (`docs/DEMO_WALKTHROUGH.md`)
   - Viva Q&A seeds (`docs/VIVA_QA.md`)

### ⚠️ Partial (Live Backend Code Written, Not Executed)

1. **Live AWS Backend** (`src/control/live_backend.py`)
   - Code for deploying SAM stack, sending messages to real SQS, polling CloudWatch metrics
   - Cost guard to prevent accidental spend
   - **Status:** Unit tested with moto, but **never executed against real AWS account**

### ❌ Not Implemented

1. **Live AWS Campaigns** — sole hard residual for CA2 cloud evidence
2. **Real-World Failure Injection** on AWS
3. **Dedicated adaptive_vt / DIVE campaign** (optional; code path exists, matrix disabled)

## Simulation Validity

### Known Simulator Limitations

1. **No Cold Starts**
2. **No Concurrency Limits**
3. **No Network Variability**
4. **No AWS Service Failures**
5. **Simplified Visibility Timeout**
6. **No Poison Pill Side Effects**

### Packaging twin note

Two git cohorts differ only by whether `spec.adaptive_vt: false` is present. Metrics and seeds match; `config_hash`/`run_id` differ. See `results/README.md` and `configs/analysis_plan.yaml` amendment 2026-09-20.

## How to Verify Simulation Claims

1. **Run Tests**: `make test`
2. **Run Pilot**: `make pilot`
3. **Run Full Experiments**: `make experiments` (design = 350 unique cells)
4. **Run Stats**: `make stats` (must report `350 runs` after packaging-dedup)
5. **Generate Figures**: `make figures`
6. **Quality Gates**: `make gates`

All commands default to `DRY_RUN=1`. Live AWS requires explicit operator action (`DRY_RUN=0`) and is **out of scope for this hygiene pass**.

## Conclusion

Localsim evidence is reconciled to the 350-cell design. **CA2 alignment remains < 100%** until live SQS/CloudWatch key-cell validation is collected. `READY_FOR_AWS=yes` means the sole hard residual is that live campaign—not that deploy has started.

---

**Honest Disclosure:** No AWS account was charged in this pass. CA2 alignment **≈ 90% < 100%**. Sole hard residual = live SQS.
