# Runbook

Rasool Basha Durbesula - 24205478

Step by step, local machine -> the student's own AWS account -> results. Every
step is also a `make` target. Commands run from `rassool-thesis/dynamodb-pk-capacity-eval/`.

## 0. Prerequisites

```bash
aws --version                        # AWS CLI v2
terraform version                    # 1.15.x
python3.12 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
export AWS_PROFILE=<your-profile> AWS_REGION=eu-west-1
aws sts get-caller-identity          # make sure it is YOUR account
make test                            # everything offline (moto), about a minute
```

## 1. Budget first

```bash
python scripts/budget_estimate.py
python scripts/run_matrix.py --dry-run
```

Estimate at eu-west-1 list prices (Price List API, 2026-09-11), free tier ignored:

| item | USD |
|---|---|
| request path during batches + settling (the cost-per-10k basis) | 15.29 |
| provisioned tables between batches (charged every hour they exist, ~61 h) | 41.69 |
| seeding 1M items x 3 on-demand tables | 2.12 |
| seeding the 3 provisioned tables at the seed write floor | 4.41 |
| storage (6 tables, ~1 GB each) | 0.34 |
| driver Lambda (arm64, ~190 Lambda-hours) | 15.76 |
| **total** | **~80** |

The provisioned tables cost about $0.68 per hour whether they are used or not:
deploy only when you are ready to run, and destroy straight after. This is more
than the free tier (see docs/ASSUMPTIONS.md C3) - agree the budget with the supervisor.

## 2. seed -> deploy

```bash
make design          # capacity plan + hot-key predictions (analysis/design_checks/)
make deploy          # tfvars, driver zip, terraform apply -var seed_mode=true
                     # add -var budget_email=you@example.com in iac/ for the Budgets alert
make seed            # 1,000,000 orders into each of the six tables, then seed_mode=false
```

Seeding takes roughly 10-20 minutes per table. Check the item counts in the
console (DynamoDB updates `ItemCount` about every 6 hours, so use a
`Select=COUNT` scan on one table if you need it now).

## 3. warmup and pilot (short n before the full n = 30)

```bash
make pilot                                          # 1 block (24 batches) at 25% of the rate, ~1.5 h
python analysis/pilot_check.py --results results_pilot
```

Read `results_pilot/pilot_check.json`:

* `settling.lengthen_settling` true -> raise `settling_seconds` in `config/experiment.yaml`
  and write an amendment in `docs/ANALYSIS_PLAN.md` before the main run;
* `hot_rank_share.min` should be about 0.90;
* `power_f025_n30` is the power of the design for a medium effect.

Warm-up is automatic: before every measured batch `run_matrix.py` sends
`warmup_invocations` warm-up calls and a `settling_seconds` settle call.

## 4. run-matrix

```bash
make run-matrix          # 720 batches, 30 randomised blocks, ~60 h wall time
```

It is resumable - if it stops (laptop sleep, budget cap), run it again and it
skips the batch ids already in `results/batches.csv`. Keep the laptop awake
(`caffeinate -i make run-matrix` on macOS) or run it from a small EC2 instance.

### Abort conditions

| Condition | What happens |
|---|---|
| a cell has 3 batches in a row above 50% throttled | that cell stops, listed in `results/aborted.json` - report it, do not rerun it quietly |
| running spend of the day passes `abort.daily_budget_usd` ($25) | the run stops; continue the next day |
| CloudWatch alarm `<table>-throttle-storm` goes to ALARM | stop the run by hand (Ctrl-C) and look at the dashboard |
| AWS Budgets email at 80% | check `budget_estimate.py` against the bill before carrying on |

## 5. collect-metrics

```bash
make collect             # results/cloudwatch.csv + real provisioned capacity into batches.csv
```

Run it within 14 days (1-minute CloudWatch data is kept for 15 days).

## 6. analyse

```bash
make analyse             # report/generated/: cell_summary, hypotheses.json, pareto, figures
```

## 7. teardown

```bash
aws s3 sync s3://$(cd iac && terraform output -raw results_bucket)/raw results/raw_s3/   # optional copy
make teardown            # terraform destroy - tables, Lambda, bucket, alarms, dashboard
```

## Recomputing any cost figure

From `config/prices.yaml` and the columns of `results/batches.csv`:

    on-demand:   cost = rcu * 0.0000001415 + wcu * 0.000000705
    provisioned: cost = (prov_rcu_avg * 0.000147 + prov_wcu_avg * 0.000735) * wall_s / 3600
    cost_per_10k = cost / succeeded * 10000

`analysis/cost_model.py` does exactly this; `tests/test_stats_cost.py` checks it by hand.

## Offline smoke test (no AWS)

```bash
make smoke               # real handler + in-memory fake DynamoDB (moto), about 2 minutes
```

Its numbers only show that the pipeline works - they are not DynamoDB measurements.

Rasool Basha Durbesula
