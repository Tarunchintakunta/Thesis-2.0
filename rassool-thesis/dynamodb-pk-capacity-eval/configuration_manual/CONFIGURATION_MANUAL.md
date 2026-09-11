# Configuration manual

**Partition-Key Design and Capacity Mode in Amazon DynamoDB: An Empirical Performance-Cost Evaluation under Serverless Workloads**

Rasool Basha Durbesula - 24205478 - MSc Cloud Computing, National College of Ireland

Separate from the report's page limit. Everything a marker needs to rebuild and
re-run the ICT artefact. Commands run from `rassool-thesis/dynamodb-pk-capacity-eval/`.

## 1. Outputs of the project

| Output | Type | Where |
|---|---|---|
| Six-table DynamoDB estate (3 key designs x 2 capacity modes), driver Lambda, IAM, dashboard, alarms, budget | Terraform | `iac/` |
| Workload suite: Zipfian key sampler, key designs K1-K3, profiles W1-W4, 1M-item seed loader | Python | `workloads/` |
| Run matrix (randomised blocks, settle -> warm-up -> measure, abort rules) and CloudWatch collection | Python | `scripts/run_matrix.py`, `scripts/collect_metrics.py` |
| Cost model, statistics (two-way ANOVA / ART / Tukey / Holm / joint test), trade-off surface | Python | `analysis/` |
| Result schema, runbook, this manual | docs | `results/SCHEMA.md`, `RUNBOOK.md` |

## 2. Prerequisites and versions

| Tool | Version | Notes |
|---|---|---|
| Python | 3.12 | `python3.12 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt` |
| Terraform | 1.15.x (tested 1.15.7), AWS provider 6.x (locked at 6.64.0) | `iac/.terraform.lock.hcl` |
| AWS CLI | v2 | a named profile with the student's own credentials |
| zip | any | used by `scripts/build_lambda.sh` |

## 3. AWS account set-up

* Region **eu-west-1** for everything; one account (the student's own).
* Credentials: `export AWS_PROFILE=<profile>`; check with `aws sts get-caller-identity`.
* Permissions to deploy: DynamoDB (table + auto-scaling), Application Auto Scaling,
  Lambda, IAM (role + inline policy), S3 (results bucket), CloudWatch (dashboard,
  alarms, logs), AWS Budgets (optional). Least-privilege policy for running the
  matrix afterwards: `terraform output operator_policy_json` (invoke the driver,
  describe tables, read CloudWatch metrics, read the raw objects).
* The driver Lambda's own role may only Get/Put/BatchGet/BatchWrite/DescribeTable
  on the six tables, write `raw/*` in the results bucket and its own logs.

## 4. Deploy, seed, run, analyse, tear down

| Step | Command | What it does |
|---|---|---|
| design | `make design` | capacity plan + hot-key predictions -> `analysis/design_checks/` |
| deploy | `make deploy` | renders `iac/terraform.tfvars.json`, builds `iac/build/driver.zip`, `terraform apply -var seed_mode=true` |
| seed | `make seed` | loads 1,000,000 orders into each table (BatchWriteItem x 25), then `terraform apply -var seed_mode=false` |
| pilot | `make pilot` then `python analysis/pilot_check.py --results results_pilot` | 1 block at 25% rate; settling / power / skew checks |
| run | `make run-matrix` | 720 measured batches in 30 randomised blocks, resumable |
| collect | `make collect` | CloudWatch per batch -> `results/cloudwatch.csv`, real provisioned capacity into `batches.csv` |
| analyse | `make analyse` | tests, tables, figures -> `report/generated/` |
| teardown | `make teardown` | `terraform destroy` (the bucket is force-destroyed, download `results/` first) |

## 5. Switching among the six configurations

There is nothing to switch: all six tables exist at the same time, named
`ddbpk-<k1|k2|k3>-<ondemand|provisioned>`. The run matrix picks the table per
batch (`workloads/matrix.py`). To add or change a configuration, edit
`local.designs` / `local.modes` in `iac/main.tf` and `CONFIGS` in `workloads/matrix.py`.
Provisioned bounds come from `config/experiment.yaml` -> `analysis/design_checks.py`
-> `scripts/render_tfvars.py`; never edit `terraform.tfvars.json` by hand.

## 6. Reading the metrics and CSVs

* `results/batches.csv` - one row per batch; column meanings in `results/SCHEMA.md`.
* `results/cloudwatch.csv` - CloudWatch sums per batch window. `cw_*Throttle*` should
  agree with `throttled` in batches.csv (CloudWatch counts events per partition, so it can
  be higher than the number of failed calls).
* Dashboard `ddbpk` (terraform output `dashboard`) - consumed vs provisioned capacity and
  throttle events per table, driver invocations and errors.

## 7. Mapping from experiment cells to files

| Cell | batch ids | raw file |
|---|---|---|
| key design K, mode M, workload W, replicate r | `b<r:02d>-<K>-<M>-<W>` (e.g. `b07-K2-provisioned-W4`) | `results/raw/<batch_id>.csv.gz` (one row per operation, `lambda_id` column) |

Result tables group by `workload` x `configuration` (`<K>-<M>`), 30 rows each.

## 8. Cost monitoring and abort

* Before running: `python scripts/budget_estimate.py` (whole bill) and
  `python scripts/run_matrix.py --dry-run` (request path of the plan).
* During the run: `run_matrix.py` keeps a running daily total and stops at
  `abort.daily_budget_usd`; a cell stops after `abort.consecutive_batches` batches in a row
  above `abort.throttle_rate` throttled (`results/aborted.json`); the CloudWatch
  `<table>-throttle-storm` alarms flag a table with > 5,000 throttle events/min for 3 minutes;
  `-var budget_email=...` adds an AWS Budgets email at 80% / 100%.
* Recomputing a cost figure by hand: formulas at the end of `results/SCHEMA.md`, prices in
  `config/prices.yaml` (dated), refresh with `make prices`.

## 9. Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| Many throttles on a provisioned table right after deploy | auto-scaling has not reached its floor yet, or seed_mode is still on - wait, check the dashboard |
| `cold_contaminated` on many batches | Lambda environments recycled between cells; raise `warmup_invocations` |
| `response_p99_ms` far above `latency_p99_ms` | the generator fell behind; raise `lambdas_per_batch` |
| `AccessDeniedException` from the driver | the table name does not match the IAM policy - redeploy after changing the prefix |
| `hot_rank_share` far from 0.90 | wrong `zipf_s` in the event; check `config/experiment.yaml` |
| `terraform apply` fails on `filebase64sha256` | build the zip first: `make build` |
| moto smoke runs but every p-value is large | expected - moto has no capacity model; smoke numbers are not DynamoDB data |

Rasool Basha Durbesula
