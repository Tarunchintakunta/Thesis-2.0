# Configuration Manual

**Project:** Reliability and Recovery of Amazon SQS Messaging under Injected
Consumer and Downstream Failures
**Student:** Anjaneya Reddy Gurram (24288853) - MSc in Cloud Computing, National College of Ireland

This manual explains how to install, configure, run and tear down the
artefact, and how to read what it produces. It is separate from the report
and does not count towards the page limit.

---

## 1. What is in the artefact

| Folder | Contents |
|--------|----------|
| `template.yaml`, `samconfig.toml` | AWS SAM stack: SQS queue + DLQ, two Lambda functions, two DynamoDB tables, SSM fault switch, log groups |
| `src/` | handler code (`queue_consumer`, `sync_api`, `common`), load generator (`producer`), experiment control (`control`), local simulator (`localsim`) |
| `configs/` | experiment definitions (pilot, baseline, arms, fault campaigns, burst cells), pre-registered analysis plan, price table |
| `scripts/` | setup, deploy, destroy, run and cost-guard helpers |
| `analysis/` | statistics (`stats_tests.py`) and figures (`plot_results.py`) - read manifests only |
| `results/` | run manifests, summaries, figures (raw per-run dumps are gitignored) |
| `tests/` | unit tests + integration tests (dry-run pipeline, moto-backed AWS code) |

There are two back ends:

* **DRY_RUN=1 (default)** - a local discrete-event simulator of SQS + Lambda +
  DynamoDB calls the real handler code. Free, needs no AWS account, a full
  campaign runs in seconds. Its outputs are labelled `backend: localsim` and
  are **not AWS measurements**.
* **DRY_RUN=0 plus `--live`** - the same runner drives the deployed SAM stack
  in your own AWS account.

## 2. Prerequisites

| Tool | Version used | Needed for |
|------|--------------|------------|
| Python | 3.11 or newer (3.12 used) | everything |
| pip / venv | bundled with Python | dependencies |
| git | any recent | manifests record the commit |
| make | any (optional) | shortcuts |
| AWS CLI v2 | 2.x | live mode only |
| AWS SAM CLI | 1.x (`pip install aws-sam-cli`) | build/deploy only |
| An AWS account you own | - | live mode only |

Docker and LocalStack are **not** required.

## 3. Local setup

```bash
cd anji-thesis/sqs-reliability-recovery
scripts/scaffold.sh              # creates .venv, installs requirements-dev.txt, copies .env
source .venv/bin/activate
make test                        # unit + integration tests (about 2 s)
make validate                    # cfn-lint on template.yaml
make self-check                  # statistics self test
```

If `python3.12` is not on your PATH: `PYTHON=python3.11 scripts/scaffold.sh`.

## 4. Running the experiments locally (free)

| Step | Command | Runs | Output folder |
|------|---------|------|---------------|
| Pilot + repeat check | `make pilot` | 18 | `results/pilot/`, `results/summary/power_from_pilot.json` |
| Baseline replication (no fault) | `make baseline` | 115 | `results/baseline/`, `results/figures/baseline/` |
| Sync vs queue arm (no fault) | `make arms` | 10 | `results/arms/` |
| Fault campaigns A-F + H grid | `make campaigns` | 187 | `results/campaigns/` |
| Burst replication | `make burst` | 20 | `results/burst/` |
| Hypothesis tests | `make stats` | - | `results/summary/hypotheses.md`, `stats_H1_H2_H3.json` |
| Figures | `make figures` | - | `results/figures/*.png` |
| Quality gates | `make gates` | - | exit code 0 when all pass |

`make experiments` runs the five run steps in order. Single campaigns:

```bash
scripts/run_fault_campaign.sh --fault consumer_kill --vary visibility_timeout      # A (H1)
scripts/run_fault_campaign.sh --fault unhandled_error --vary max_receive_count     # B (H2)
scripts/run_fault_campaign.sh --fault datastore_reject --vary max_receive_count    # C
scripts/run_fault_campaign.sh --fault datastore_timeout --vary visibility_timeout  # D
scripts/run_fault_campaign.sh --campaign E_guidance_transfer                       # H3
scripts/run_fault_campaign.sh --campaign F_arms_under_fault
scripts/run_fault_campaign.sh --load burst --subset configs/key_cells.yaml
```

Handy runner flags: `--list` (show the plan, run nothing), `--limit N`,
`--repeats N`, `--orders N`, `--no-raw`, `--from-env` (one run from `.env`).

## 5. AWS account setup (live mode only)

Use **your own** account (the ethics declaration relies on the target system
being yours). A fresh account with a budget alarm is ideal.

1. Create an IAM user or IAM Identity Center user for the experiment. It needs
   permission to create CloudFormation stacks and the resources in
   `template.yaml`: CloudFormation, Lambda, SQS, DynamoDB, SSM Parameter
   Store, IAM role creation (`CAPABILITY_IAM`), S3 (SAM artefact bucket),
   CloudWatch Logs and CloudWatch metrics (read). For a short project the
   managed `PowerUserAccess` plus `IAMFullAccess` is the simple option; revoke
   it afterwards.
2. `aws configure` (or `aws configure sso`) and set the region you will keep
   for the whole study, e.g. `eu-west-1`.
3. Check: `aws sts get-caller-identity`.

**Function permissions** are least privilege and scoped to single resources:
the consumer and the sync processor may only put/get items on the Orders
table, write to the Events table and read the one SSM parameter; SAM adds the
SQS poller permissions for the orders queue only. There is no `*` on `*`.

### Billing alarm (do this before the first deploy)

Enable *Receive Billing Alerts* in Billing preferences, then:

```bash
aws sns create-topic --name billing-alerts --region us-east-1
aws sns subscribe --topic-arn <topic-arn> --protocol email \
  --notification-endpoint <your-email> --region us-east-1
aws cloudwatch put-metric-alarm --region us-east-1 \
  --alarm-name billing-over-5-usd --namespace AWS/Billing --metric-name EstimatedCharges \
  --dimensions Name=Currency,Value=USD --statistic Maximum --period 21600 \
  --evaluation-periods 1 --threshold 5 --comparison-operator GreaterThanThreshold \
  --alarm-actions <topic-arn>
```

(AWS Budgets with a monthly cost budget and an email alert works as well.)

## 6. The `.env` file

Copy `.env.example` to `.env` (the scaffold script does it). The runner loads
it automatically; real environment variables win over the file.

| Variable | Meaning |
|----------|---------|
| `AWS_REGION` | region of the stack; keep it constant |
| `STAGE` | `dev`, `pilot` or `exp`; part of every resource name |
| `STACK_NAME` | stack the live runner reads its outputs from |
| `DRY_RUN` | `1` simulator (default), `0` live (also needs `--live`) |
| `FAULT_MODE`, `FAULT_RATE`, `FAULT_WINDOW_SEC` | fault for `--from-env` runs |
| `VISIBILITY_TIMEOUT`, `MAX_RECEIVE_COUNT`, `BATCH_SIZE` | queue settings for `--from-env` runs |
| `ORDER_COUNT`, `LOAD_PROFILE` | workload for `--from-env` runs |
| `RUN_ID` | fixed run id for `--from-env` (empty = derived from the config) |
| `ENABLE_COST_GUARD` | `1` = refuse plans above the budget |
| `MAX_ESTIMATED_USD` | budget for one live invocation of the runner |

## 7. Deploy and destroy

```bash
make guard                       # cost guard + sanity checks, must print "cost guard ok"
scripts/deploy.sh                # sam validate --lint, sam build, sam deploy (stack sqs-rr-dev)
scripts/deploy.sh pilot          # or the pilot / exp stacks from samconfig.toml
export STACK_NAME=sqs-rr-dev
...
scripts/destroy.sh sqs-rr-dev    # sam delete + checks the stack is really gone
```

`destroy.sh` appends a line to `results/teardown_log.txt` when the stack is
confirmed deleted - keep that file as teardown evidence.

Stack outputs used by the runner:

| Output | Used for |
|--------|----------|
| `OrdersQueueUrl`, `OrdersQueueArn`, `OrdersDlqUrl` | sending, depth sampling, reading the DLQ |
| `SyncApiUrl` | sync arm requests |
| `OrdersTableName`, `EventsTableName` | evidence collection |
| `QueueConsumerFunctionName` | CloudWatch counters for the cost proxy |
| `ConsumerMappingId` | changing batch size between runs |
| `FaultParamName` | the fault switch |

## 8. Live runs

```bash
python scripts/estimate_cost.py --config configs/pilot.yaml   # look at the estimate first
DRY_RUN=0 scripts/run_pilot.sh
DRY_RUN=0 scripts/run_baseline.sh
DRY_RUN=0 scripts/run_fault_campaign.sh --fault consumer_kill --vary visibility_timeout
```

What the live runner does per run: applies the visibility timeout,
maxReceiveCount and delivery delay to the queue and the batch size to the event
source mapping, waits for the mapping to be `Enabled`, purges both queues and
waits 61 s (SQS allows one purge per minute), writes the fault schedule to SSM,
sends the orders, samples queue depth every 5 s, drains, then reads the events
table, the DLQ and the leftover messages.

Notes:

* The live backend is implemented and unit tested with moto, but it has not
  been executed against a real account in this repository - run the pilot
  first and check the manifests by hand.
* The estimate for all 187 fault-campaign runs is about $4.6 with a x2 safety
  factor and ~20 h of wall time because of the cool-downs. Split campaigns
  over days, but keep each campaign in one block (Eismann et al., 2022).
* Fault switching goes through a ~5 s SSM cache, so window edges are fuzzy by
  a few seconds in live mode.

## 9. Reading the outputs

### Manifests - `results/<step>/manifests/<RUN_ID>.json`

The source of truth for the analysis. Main fields: `run_id`, `campaign`,
`backend` (`localsim` or `live`), `git.sha` and `git.dirty`, `config_hash`,
`seed`, `order_position` (place in the randomised order), `fault_schedule`,
`spec` (every setting of the run), `metrics`, `cost`, `counters`.

### `summary.csv` (one row per run, rebuilt from the manifests)

| Column | Meaning |
|--------|---------|
| `loss_rate` | share of produced orders neither processed nor in the DLQ when the run ended |
| `stranded_rate` | part of the above still sitting in the main queue (not lost, just late) |
| `duplicate_rate` | extra successful processing events per processed order (compare to the no-fault floor) |
| `dlq_capture_rate` | share of produced orders that ended in the DLQ |
| `success_rate` | share of produced orders written to the Orders table |
| `recovery_time_s` | seconds from fault OFF until the backlog (visible + in flight) is back in the pre-fault band; empty = did not recover before the horizon |
| `recovery_time_visible_s` | same but on the visible count only (master prompt wording); can say 0 while failed messages hide in flight |
| `throughput_msg_s` | processed orders / (last success - first send) |
| `latency_p50_s`, `latency_p95_s` | produce -> first successful write |
| `usd_total` | cost proxy from request counts and GB-s |

### Raw dumps - `results/<step>/raw/<RUN_ID>/` (gitignored)

`events.csv` (one row per attempt), `samples.csv` (queue depth over time),
`produced.csv` (order id, send time).

### Statistics - `results/summary/`

`hypotheses.md` (the table for the report), `stats_H1_H2_H3.json` (full
results incl. group means, 95 % bootstrap CIs, normality p-values, Holm
adjusted p-values, decisions, exploratory tests and excess duplicates),
`stats_H0_throughput_config.json` (baseline), `power_from_pilot.json`.

## 10. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Many duplicates even without faults | visibility timeout shorter than processing time, message reappears while still being processed | raise VT to at least 6x the function timeout; check `duplicate_rate` of the no-fault runs |
| Recovery takes minutes after a short fault | long visibility timeout: failed messages wait the full VT before a retry | expected - that is the effect being measured; lower VT if fast recovery matters |
| DLQ fills up during a short outage | `maxReceiveCount` too low, messages run out of retries before the fault ends | raise maxReceiveCount or VT so retries span the outage |
| `sam deploy` fails with "visibility timeout ... less than function timeout" | VT < consumer timeout | keep `VisibilityTimeout >= ConsumerTimeout` (the config validator refuses such runs) |
| `batch size > 10` rejected | batching window 0 | keep `BatchingWindowSeconds >= 1` |
| `PurgeQueueInProgress` | two purges within 60 s | the runner waits 61 s; do not run two runners on one stack |
| `recovery_time_s` empty | run never got back into the band before the horizon | increase `drain_timeout_s` or accept it as censored (the analysis uses the lower bound with rank tests) |
| Live runner stops with CostGuardError | plan above `MAX_ESTIMATED_USD` | reduce orders/repeats, or raise the limit on purpose |
| `no manifests under ...` in the analysis | wrong `--in` folder | point it at `results/` or the step folder |

## 11. Cost controls

* Default mode is the simulator - nothing is billed unless DRY_RUN=0 and `--live`.
* `scripts/assert_free_tier_guard.py` blocks live runs when the guard is off,
  the budget is silly, the stage looks like production, or the plan is too
  expensive.
* The runner prices the whole plan with the simulator before any live run and
  aborts above `MAX_ESTIMATED_USD`.
* 256 MB functions, 7 day log retention, on-demand tables with TTL on events.
* Destroy the stack after every campaign (`scripts/destroy.sh`).

## 12. Reproducing the committed results

```bash
scripts/scaffold.sh && source .venv/bin/activate
make experiments      # pilot, baseline, arms, campaigns, burst (simulator, ~10 s)
make stats figures
```

Run ids and seeds are derived from the configs, so the manifests come out with
the same ids and the same metrics (only timestamps and the git sha change).

## 13. Tests and CI

`make test` runs the unit tests (fault modes, idempotency, handlers, simulated
SQS semantics, metrics, configs, engine behaviour, cost guard) and the
integration tests (dry-run pipeline end to end; DynamoDB, SQS and SSM code
against moto). GitHub Actions (`.github/workflows/ci.yml` at the repository
root) runs ruff, the tests, cfn-lint, the statistics self-check and a pilot
dry run on every push.

Anjaneya Reddy Gurram
