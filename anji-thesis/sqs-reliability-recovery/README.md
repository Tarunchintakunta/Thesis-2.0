# SQS reliability and recovery under injected failures

MSc in Cloud Computing - Research Project artefact, National College of Ireland
**Title:** Reliability and Recovery of Amazon SQS Messaging under Injected Consumer and Downstream Failures
**Student:** Anjaneya Reddy Gurram (24288853)

Research question: *How does Amazon SQS configuration affect message
reliability and recovery under injected consumer and downstream failures?*

This repo is the artefact: an AWS SAM application (sync arm + SQS/DLQ arm),
an in-process fault injection switch, an experiment runner that walks a
randomised config matrix and writes a manifest per run, and the statistics /
plotting scripts. It also contains a local simulator so everything can be run
for free without an AWS account.

## Quick start (one command pilot, no AWS)

```bash
scripts/scaffold.sh && make pilot
```

That creates `.venv`, installs the dev requirements, runs the 18 pilot runs
on the local simulator and prints the repeat-count check. Then:

```bash
make test          # unit + integration tests
make experiments   # pilot, baseline, arms, fault campaigns, burst (~30 s)
make stats figures # hypothesis tests + figures
make gates         # the quality gates from the master prompt
```

Live AWS runs (own account only): see `docs/CONFIGURATION_MANUAL.md`.

## Layout

```text
sqs-reliability-recovery/
├── template.yaml / samconfig.toml   SAM stack (SQS + DLQ, 2 Lambdas, DynamoDB, SSM fault switch)
├── src/
│   ├── queue_consumer/handler.py     SQS event source Lambda (ReportBatchItemFailures)
│   ├── sync_api/app.py               HTTP API Lambda (control arm)
│   ├── common/                       models, faults, idempotency, dynamo, metrics, processing
│   ├── producer/                     synthetic orders + normal/burst/batch load
│   ├── control/                      runner, configs, fault controller, manifests, cost guard, live backend
│   └── localsim/                     SQS/Lambda/DynamoDB simulator on a virtual clock (DRY_RUN=1)
├── configs/                          pilot, baseline, arms, fault campaigns, burst, analysis plan, prices
├── scripts/                          scaffold, deploy, destroy, run_*, estimate_cost, free tier guard
├── analysis/                         stats_tests.py, plot_results.py, load_results.py
├── results/                          manifests + summaries + figures (simulated, see results/README.md)
├── docs/                             CONFIGURATION_MANUAL, ARCHITECTURE, DEMO_WALKTHROUGH
├── report/  weekly/                  report notes, weekly template
└── tests/                            unit + integration (moto)
```

## Experiment phases

| Phase | What | Command |
|-------|------|---------|
| 1 | unit tests, template lint, dry run | `make test validate pilot` |
| 3 | baseline replication (no fault, VT x batch) | `make baseline` |
| 4 | sync vs queue arm | `make arms` |
| 5 | fault campaigns A-D, H3 campaign E, arms under fault F, grid H | `make campaigns` |
| 5 | burst replication | `make burst` |
| 6 | H1-H3 with Holm, figures | `make stats figures` |
| 7 | teardown (live) | `scripts/destroy.sh` |

## Status

- [x] SAM template (cfn-lint clean), handlers, fault switch, idempotency
- [x] local simulator + experiment runner + manifests + cost guard
- [x] tests (unit + integration with moto) and GitHub Actions CI
- [x] full simulated study (350 runs), statistics and figures - **simulation, not AWS**
- [ ] pilot + campaigns on a real AWS account (live backend written and unit tested, not yet run)
- [ ] research report (to be written in the NCI template, see `report/README.md`)
- [ ] weekly reports (fill in `weekly/WEEK_TEMPLATE.md` each week)

## Baseline

Kyrychenko, O.O., Ostapov, S.E. and Kyrychenko, O.L. (2025) 'Optimization of
SQS configurations for efficient batch data processing', *WSEAS Transactions
on Systems*, 24, pp. 36-43. https://doi.org/10.37394/23202.2025.24.4

Anjaneya Reddy Gurram
