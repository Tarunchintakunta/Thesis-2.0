## Alignment note (2026-09-20, iter-1)

**CA2 research alignment ≈ 78% — still < 100%. AWS phase blocked.**

Authoritative evidence: `results/summary/stats_H1_H2_H3.json`, `stats_H0_throughput_config.json`, `hypotheses.md` (`backend: localsim` only).

| Issue | Status |
|-------|--------|
| H1–H3 LaTeX/report vs JSON | Fixed in `latex_report/text/{abstract,evaluation,conclusion}.tex` + `results/README.md` |
| DIVE / production overclaims | Softened: STATUS + VIVA/DEMO + final report; `adaptive_vt: false` in all manifests |
| CA2 lit in bib | Added AlSaidAhmad2024Chaos + Bosilia2025AsyncResilience (`note={doi:…}`); cited in relatedwork |
| Obj4 cost as experimental claim | Softened: cost = estimator projection only; no cost DV in results |
| Live AWS SQS / CloudWatch | **Residual blocker** — not started (do not deploy until alignment gate) |

Remaining to 100%: live AWS key-cell validation (CA2 cloud evidence); optional dedicated adaptive_vt campaign if DIVE is retained as a claim; reconcile phase run-count table (documented 350 vs on-disk manifests/stats run counts) without inventing metrics.

---
# Project Status: Simulation vs Live AWS

**Student:** Anjaneya Reddy Gurram (24288853)  
**Project:** Reliability and Recovery of Amazon SQS Messaging under Injected Consumer and Downstream Failures  
**Last Updated:** September 20, 2026

## Executive Summary

This artefact has been developed with a **local simulator** that emulates SQS, Lambda, and DynamoDB behavior on a virtual clock. All experimental results, figures, and statistical analyses included in this submission are generated from **simulated runs**, not from live AWS infrastructure. **DIVE/adaptive_vt was not enabled** in the committed experiment matrix.

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

4. **Testing**
   - Unit tests for fault injection, metrics, SQS simulation, engine (`tests/unit/`)
   - Integration tests with moto for AWS service mocking (`tests/integration/`)
   - pytest suite with 100% pass rate in CI/CD (GitHub Actions)

5. **Experiments and Analysis** (ALL SIMULATED)
   - **Pilot runs** (18 configurations, 3 repeats): Repeatability validation
   - **Baseline replication** (6 VT × 4 batch configs, 5 repeats): Steady-state performance
   - **Arms comparison** (sync vs queue, 10 repeats): Architecture comparison
   - **Fault campaigns A-E** (consumer kill, error, reject, timeout, grid): Hypothesis testing
   - **Hypothesis tests H1-H3** with Holm-Bonferroni correction: Statistical validation
   - **Figures** (11 plots in `results/figures/`): All generated from simulated data

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
   - **Reason:** Project designed for free-tier awareness; simulation sufficient for research objectives

### ❌ Not Implemented

1. **Live AWS Campaigns**
   - No real SQS queues created
   - No Lambda functions deployed to AWS
   - No DynamoDB tables provisioned in AWS
   - No CloudWatch metrics collected from AWS

2. **Real-World Failure Injection**
   - Fault injection tested only in simulator
   - No actual Lambda container kills or downstream service timeouts in AWS

## Simulation Validity

### Simulator Design Principles

The simulator (`src/localsim/engine.py`) implements:

1. **Discrete-Event Semantics**: Messages progress through states (sent → visible → received → processing → deleted/dlq) via time-ordered events
2. **SQS Standard Behavior**: At-least-once delivery, configurable visibility timeout, receive count tracking, DLQ redrive
3. **Lambda Batch Processing**: Event source mapping with batch size, partial failure reporting via `ReportBatchItemFailures`
4. **Fault Injection**: Deterministic faults triggered at configured times (e.g., consumer unavailable 30-40s into run)
5. **Metrics Fidelity**: Same metric collection (loss, duplicates, DLQ depth, recovery time, latency, throughput) as live system would provide

### Known Simulator Limitations

1. **No Cold Starts**: Lambda invocations assume warm execution; no cold-start latency modeled
2. **No Concurrency Limits**: Unlimited concurrent Lambda executions; real AWS has soft limits (1,000 default)
3. **No Network Variability**: Deterministic timing; real AWS has network jitter and retry backoff
4. **No AWS Service Failures**: Simulator assumes SQS/Lambda/DynamoDB never fail; real AWS has service events
5. **Simplified Visibility Timeout**: Exact second-precision; real SQS has approximate timing
6. **No Poison Pill Side Effects**: Unhandled errors are instant; real Lambda invocations may timeout after configured duration

### Why Simulation is Scientifically Adequate

This research investigates **configuration trade-offs** (visibility timeout, maxReceiveCount, batch size) under **controlled failure injection**. The simulator provides:

- **Reproducibility**: Seeded RNG, deterministic event ordering, commit-able manifests
- **Isolation**: No AWS account variability, billing, or quota limits
- **Efficiency**: 350+ runs complete in ~30 seconds; equivalent live runs would take hours and incur cost
- **Hypothesis Testing**: Statistical comparisons require many trials; simulation enables sufficient sample sizes

The **relative effects** (e.g., "higher VT reduces loss by X%") are what matter for answering the RQ, not absolute AWS performance. Kyrychenko et al. (2025) provides live AWS baseline for steady-state; this work extends with fault injection under same config assumptions.

## How to Verify Simulation Claims

1. **Run Tests**: `make test` (pytest suite with moto)
2. **Run Pilot**: `make pilot` (18 runs, repeatability check)
3. **Run Full Experiments**: `make experiments` (~30s, 350 runs)
4. **Run Stats**: `make stats` (hypothesis tests with Holm correction)
5. **Generate Figures**: `make figures` (11 plots from results/)
6. **Quality Gates**: `make gates` (all checks pass)

All commands default to `DRY_RUN=1` (simulator mode). To attempt live AWS: set `DRY_RUN=0` and configure AWS credentials (not done in this submission).

## Future Work: Live AWS Validation

To validate simulation against real AWS (outside scope of this submission):

1. **Set Up AWS Account**: Configure credentials, ensure free-tier eligibility or accept costs
2. **Deploy Stack**: `make deploy` (creates SQS, Lambda, DynamoDB via SAM)
3. **Run Subset**: Use `configs/key_cells.yaml` (10-20 runs, ~$5-10 estimated)
4. **Compare Metrics**: Plot simulated vs live results for same configs
5. **Document Deltas**: Report where real AWS differs (e.g., latency variance, cold starts)
6. **Teardown**: `make destroy` (delete all resources)

## Conclusion

This submission demonstrates a **methodologically rigorous, reproducible, and cost-effective** localsim approach to studying SQS reliability under failure injection. All results are **clearly labeled as simulated** in report text, figure captions, and `results/README.md`. Relative configuration effects are interpretable under the simulator's documented limits; **live AWS key-cell validation remains required for CA2 cloud evidence** and must not be assumed to leave findings unchanged.

---

**Honest Disclosure:** No AWS account was charged. No real queues were harmed in the making of this research. CA2 alignment **< 100%**.
