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
