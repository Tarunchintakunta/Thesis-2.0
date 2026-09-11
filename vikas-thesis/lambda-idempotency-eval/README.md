# lambda-idempotency-eval

MSc in Cloud Computing research project, National College of Ireland -
Vikas Reddy Amanagantti (X25178849).

**An Empirical Evaluation of Application-Level Idempotency Strategies for Retry
Correctness on AWS Lambda and Amazon DynamoDB**

One Lambda function writes to one DynamoDB table in three ways:

| path | what happens on a redelivery |
|---|---|
| P1 plain put | it writes again - a duplicate state change |
| P2 conditional put (`attribute_not_exists(pk)`) | the condition fails, nothing changes, the failed check is still billed |
| P3 idempotency key (Powertools pattern) | the stored result comes back, the business item is not touched again |

The driver sends every request 1, 2 or 5 times with the same `request_id`. On
every delivery except the last one the function times out on purpose **after**
its write has committed, so the caller sees a failure although the state has
already changed. That way the number of retries is known before anything runs.
Duplicate state changes are counted from the table's stream and set against
that number, next to end-to-end latency and consumed capacity.

The baseline is the idea from Qi et al. (2025) (Halfmoon, asymmetric logging):
no duplicate mutation after a retry. Halfmoon gets there with its own runtime;
this project only measures what the three application-level controls achieve
on stock Lambda + DynamoDB. Nothing here re-implements Halfmoon.

## Status

| part | state |
|---|---|
| three write paths + injected timeout (`src/lambda_fn`) | done, tested on moto |
| driver: schedule, ground truth, Lambda + local backends, warm-up, budget stop, seed guard (`src/driver`) | done, tested on moto |
| mutation ground truth from DynamoDB Streams, CloudWatch cross-check | done, tested (moto / stubbed CloudWatch) |
| analysis: pilot rule, metrics, z / chi-square / Welch or Mann-Whitney, Holm, E1-E3, figures (`analysis`) | done, tested |
| Terraform: table, function, IAM, log group, alarms, budget (`infra`) | validates, **not deployed** |
| live pilot + campaign on AWS | **to do** - own account, about USD 0.17 at list prices |
| report, NCI configuration manual, weekly logs, ethics form | **to do** - checklists and drafts in `report/`, `docs/`, `weekly/` |

## Layout

```text
lambda-idempotency-eval/
├── src/lambda_fn/   handler.py (event, injection, structured log), paths.py (P1 / P2 / P3)
├── src/driver/      schedule.py, run.py (Lambda + local backends), streams.py
├── analysis/        metrics.py, stats.py, pilot_size.py, analyse.py, tables.py
├── infra/           Terraform (table, function, IAM, logs, alarms, budget) + lock file
├── config/          versions.yaml (pinned), experiment.yaml (design), prices.yaml (dated list prices)
├── scripts/         build_lambda.sh, budget_estimate.py, collect_cloudwatch.py, check_bib.py
├── data/            payload_template.json; runs/live/ after the campaign
├── results/         SCHEMA.md; moto/ = functional check (not AWS data); live/ after the campaign
├── figures/         moto/ now, live/ after the campaign
├── docs/            ANALYSIS_PLAN, ASSUMPTIONS, ETHICS, CONFIGURATION_MANUAL
├── report/          NCI section checklist
├── weekly/          weekly log template
├── bib/             references.bib - 21 papers (2022-2026) + 3 AWS docs + 2 optional older
└── tests/           60 tests, moto for DynamoDB and Streams
```

## Quick start (no AWS needed)

```bash
make setup
make test
make functional
```

## Live runs

Full steps, permissions and troubleshooting: `docs/CONFIGURATION_MANUAL.md`.

```bash
make deploy                 # builds the zip, terraform apply
make pilot && make pilot-size
make campaign WORKERS=16    # N from the pilot rule
make sensitivity WORKERS=16
make cloudwatch             # ~10 minutes later
make analyse
make destroy
```

## Budget (`make budget`, list prices published 2026-09-11)

| phase | requests | invocations | timeouts | write units | USD |
|---|---|---|---|---|---|
| pilot | 150 | 300 | 150 | 400 | 0.002 |
| campaign (N = 1000) | 9000 | 24000 | 15000 | 30000 | 0.157 |
| sensitivity | 400 | 1400 | 1000 | 3200 | 0.011 |
| warm-up | - | 96 | 0 | 0 | 0.000 |
| **total** | | **25796** | | | **0.17** |

Timed-out deliveries are billed the full 2 s plus an assumed 500 ms INIT on the
next delivery; CloudWatch Logs, stream reads and the free tier are not included.
The driver refuses to go past 60 000 invocations.

## Functional check on moto - NOT AWS data

moto has no latency model and reports 0.5 units for every UpdateItem, so this
only checks the plumbing: injected retries turn into duplicate state changes
for P1 and not for P2 / P3, the stream agrees with the function's own counts
(0 mismatches, 0 missing deliveries out of 720), and the analysis writes every
table and figure. Full output: `results/moto/summary.md`, `figures/moto/`.

| duplicate-mutation rate (30 requests per cell) | P1 | P2 | P3 |
|---|---|---|---|
| 2 deliveries | 100 % | 0 % | 0 % |
| 5 deliveries | 100 % | 0 % | 0 % |

With the timeout **between** P3's two writes (sensitivity case) the rate is
100 % at 2 and 5 deliveries: once the claim has expired, the redelivery writes
the business item again.

## Versions

eu-west-1 · python3.12 arm64, 256 MB, 2 s timeout · boto3 1.35.36 bundled, SDK
retries off · DynamoDB on-demand + streams · Terraform 1.15.7 · AWS provider 6.64.0

## Rules this follows (master prompt)

- stock Lambda + DynamoDB only - no custom runtime, no shared log layer
- three write paths, single-item writes, no transactions
- injected duplicates with a known count; CloudWatch is never the ground truth
- pilot first, 95 % CIs on every comparison, Holm-Bonferroni
- synthetic data, own account, bounded spend
- never claims exactly-once for P1, never claims P2 / P3 match Halfmoon's guarantees

Vikas Reddy Amanagantti
