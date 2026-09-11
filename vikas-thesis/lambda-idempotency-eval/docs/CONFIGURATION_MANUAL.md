# Configuration manual - lambda-idempotency-eval

Technical draft of the separate NCI configuration manual: how to set up, run
and tear down the artefact. Move it into the NCI template and check every step
against your own account before submitting.

## 1. What gets deployed

```text
driver (laptop / CloudShell / EC2 in eu-west-1)
   | synchronous Invoke, LogType=Tail, no SDK retries
   v
Lambda idem-eval-fn  (python3.12, arm64, 256 MB, 2 s timeout, boto3 1.35.36 bundled)
   | PutItem / UpdateItem, ReturnConsumedCapacity=TOTAL
   v
DynamoDB idem-eval   (on-demand, stream NEW_AND_OLD_IMAGES, TTL on "expiry")
   + CloudWatch log group (14 days), two daily alarms, optional SNS e-mail + monthly budget
```

All resources come from `infra/` and are tagged `project = lambda-idempotency-eval`,
`student = X25178849`, `data = synthetic`.

## 2. Prerequisites

| tool | version | check |
|---|---|---|
| own AWS account (not a production or shared one) | - | `aws sts get-caller-identity` |
| AWS CLI | v2 | `aws --version` |
| Terraform | 1.15.7 | `terraform version` |
| Python | 3.12 | `python3.12 --version` |
| make, zip | any | `make --version`, `zip -v` |

Permissions: Terraform needs to create DynamoDB tables, Lambda functions, IAM
roles and inline policies, CloudWatch log groups and alarms, SNS topics and
(optionally) a budget. The driver needs `lambda:InvokeFunction`,
`dynamodb:DescribeTable`, `dynamodb:GetItem`, the four DynamoDB Streams read
actions (`DescribeStream`, `GetShardIterator`, `GetRecords`, `ListStreams`) and
`cloudwatch:GetMetricStatistics`.

## 3. Set up

```bash
git clone https://github.com/Tarunchintakunta/Thesis-2.0.git
cd Thesis-2.0/vikas-thesis/lambda-idempotency-eval
make setup                 # .venv with requirements-dev.txt
aws configure              # or aws sso login; region eu-west-1
```

## 4. Pinned versions (report these)

| item | value | where |
|---|---|---|
| region | eu-west-1 | `config/versions.yaml` |
| Lambda runtime / arch / memory / timeout | python3.12 / arm64 / 256 MB / 2 s | `config/versions.yaml`, `infra/variables.tf` |
| SDK in the function | boto3 1.35.36, botocore 1.35.36 (bundled) | `src/lambda_fn/requirements.txt` |
| SDK retries | off (`total_max_attempts = 1`) | `src/lambda_fn/handler.py`, `src/driver/run.py` |
| DynamoDB | on-demand, Standard table class, streams NEW_AND_OLD_IMAGES | `infra/main.tf` |
| Terraform / AWS provider | 1.15.7 / 6.64.0 | `infra/.terraform.lock.hcl` |
| analysis | Python 3.12, `requirements.txt` | |

## 5. Check everything locally first (no AWS, no cost)

```bash
make test        # unit + moto integration tests
make lint
make tf-check    # terraform fmt + validate
make check-bib   # bibliography structure
make functional  # whole pipeline on moto -> results/moto, figures/moto (NOT AWS data)
```

## 6. Build and deploy

```bash
make build                                   # build/lambda.zip, prints its hash (reproducible)
cd infra
terraform init
terraform plan -out tfplan                   # add -var alert_email=you@example.com for alerts + budget
terraform apply tfplan
cd ..
aws lambda invoke --function-name idem-eval-fn --cli-binary-format raw-in-base64-out \
    --payload '{"warmup": true}' /dev/stdout  # expect {"type": "warmup", "cold_start": true}
```

If `alert_email` is set, confirm the SNS subscription e-mail.

## 7. Pilot

```bash
make pilot         # 150 requests (50 per path, multiplicity 2), 300 invocations, then reads the stream
make pilot-size    # results/live/pilot_report.md + pilot_choice.json
```

Read the decision in `pilot_report.md`. If anything in the plan changes, add a
dated line to the amendments table in `docs/ANALYSIS_PLAN.md`.

## 8. Campaign and sensitivity

Run the driver close to the region (CloudShell or a small EC2 instance in
eu-west-1) and keep the same machine for the whole campaign - latency is
measured by the driver.

```bash
make campaign WORKERS=16     # N comes from results/live/pilot_choice.json
make sensitivity WORKERS=16  # P3, timeout between its writes
make cloudwatch              # about 10 minutes after the campaign (CloudWatch lags)
```

Each target reads the table stream straight after its run; stream records
expire after 24 hours. A phase is never re-run into the same folder, and a
repeated phase needs a new seed (`python -m driver.run ... --seed 2`), otherwise
the driver refuses because the request ids already exist in the table.

## 9. Analysis

```bash
make analyse     # results/live/*.csv, summary.md, figures/live/*.png
```

Look at `results/live/checks.csv` first: missing deliveries, errors, lost log
records and stream-vs-self-report disagreements should all be 0 (or explained).

## 10. Tear down

```bash
make destroy
```

Then check the console for leftovers: Lambda, DynamoDB, the log group
`/aws/lambda/idem-eval-fn`, the two alarms, SNS topic and budget (if created).
Commit `data/runs/live/` and `results/live/` - they are the raw and analysed results.

## 11. Troubleshooting

| symptom | cause / fix |
|---|---|
| `terraform apply` fails on reserved concurrency | keep `reserved_concurrency = -1` (new accounts have a low concurrency limit) |
| rows with `status = error` and `TooManyRequestsException` | account concurrency limit - lower `WORKERS` and re-run the phase with a new seed |
| `lost_records` > 0 | the function record was not in the 4 KB log tail; find the `exec_id` in CloudWatch Logs |
| `stream_self_mismatch` > 0 | the stream read was incomplete - re-run `python -m driver.streams --out <run>` within 24 h |
| `FileExistsError` | a run folder is never reused - pick a new `--out` |
| "request ids are already in the table" | that phase was run before - pass a new `--seed` |
| `N` is empty in `make campaign` | run `make pilot-size` first or pass `N=...` |

Vikas Reddy Amanagantti
