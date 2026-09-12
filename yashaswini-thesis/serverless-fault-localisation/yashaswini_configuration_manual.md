# Configuration manual - serverless-fault-localisation

Technical draft of the separate NCI configuration manual. Move it into the NCI
template and check every step against your own account.

## 1. Prerequisites

| tool | version | check |
|---|---|---|
| own AWS account kept for the study | - | `aws sts get-caller-identity` |
| AWS CLI v2, AWS SAM CLI | current | `aws --version`, `sam --version` |
| Python | 3.12 | `python3.12 --version` |
| Docker (optional) | - | only for `sam build --use-container` |
| make | any | |

**IAM (least-privilege sketch).** Deploying: CloudFormation, Lambda, IAM roles
for the functions, API Gateway, DynamoDB, SSM parameter, CloudWatch Logs,
X-Ray sampling rules, Budgets (optional), an S3 bucket for `sam deploy`.
Running: `ssm:PutParameter` on `/faultlab/fault`, `lambda:PutFunctionConcurrency`
and `lambda:DeleteFunctionConcurrency` on the three targets,
`cloudwatch:GetMetricData`, `cloudwatch:GetMetricStatistics`,
`xray:GetTraceSummaries`, `xray:BatchGetTraces`.

## 2. Set up

```bash
git clone https://github.com/Tarunchintakunta/Thesis-2.0.git
cd Thesis-2.0/yashaswini-thesis/serverless-fault-localisation
make setup          # .venv with requirements-dev.txt
cp .env.example .env   # fill in STACK, REGION; never commit .env
make test && make lint && make cfn-lint && make sim     # everything local first
```

## 3. Deploy and seed

```bash
sam build           # add --use-container to build the layer inside Docker
sam deploy --guided --stack-name faultlab --capabilities CAPABILITY_IAM \
    --parameter-overrides TracingMode=Active LogLevel=ERROR SamplingFixedRate=0.05 SamplingReservoir=1
python scripts/seed_inventory.py --table <TableName output>
export API_URL=<ApiUrl output>
curl -s -X POST "$API_URL/orders" -d '{"customer_id":"CUST-0001","sku":"0001","qty":1}'
```

## 4. Calibrate (24 h, fault-free) and freeze

```bash
python scripts/campaign.py --phase calibration --url "$API_URL"
```

The thresholds are computed from this window when `eval/rig.py` runs and are
hashed; nothing is retuned later.

## 5. Campaigns

```bash
python scripts/campaign.py --phase steady --url "$API_URL"   # 60 min control + 240 injections, ~25 h
python scripts/campaign.py --phase peak   --url "$API_URL"   # the same at 10 rps
python scripts/collect_telemetry.py --run data/runs/live      # within 15 days
python -m eval.rig --source live --run data/runs/live --out results/live --figures figures/live
```

## 6. Overhead (tracing on / off)

For each condition, redeploy with its parameters, then run 30 minutes and collect:

| condition | parameter overrides |
|---|---|
| full | `TracingMode=Active LogLevel=INFO SamplingFixedRate=1.0 SamplingReservoir=1000` |
| policy | `TracingMode=Active LogLevel=ERROR SamplingFixedRate=0.05 SamplingReservoir=1` |
| off | `TracingMode=PassThrough LogLevel=ERROR` |

```bash
python scripts/campaign.py --phase overhead-full --url "$API_URL"
python scripts/collect_overhead.py --run data/runs/live --condition full
# ... policy, off ...
python scripts/collect_overhead.py --run data/runs/live --summarise
```

## 7. RCAEval comparison (offline, no AWS)

```bash
make rcaeval-data        # RE2-OB, ~0.9 GB from Hugging Face into data/rcaeval
make rcaeval-venv        # separate .venv-rcaeval with RCAEval 1.7.0
make leg2                # rule arm + baselines + analysis -> results/rcaeval
```

CausalRCA is slow (minutes per case); `make leg2` runs it on repetition 1 only.

## 8. Tear down and cost control

```bash
sam delete --stack-name faultlab
```

Check the console for leftover log groups and the sampling rule. Before the
campaign run `make budget`; set `AlertEmail` for a monthly budget e-mail.

## 9. Troubleshooting

| symptom | fix |
|---|---|
| every request 502 | the fault switch still holds a fault: `aws ssm put-parameter --name /faultlab/fault --value '{}' --overwrite` |
| a target stays throttled | `aws lambda delete-function-concurrency --function-name faultlab-<target>` |
| no traces | TracingMode=PassThrough, or the sampling rule fixed rate is 0 |
| `windows.json` refuses a phase | a phase is never re-run into the same folder - use a new `--run` folder |
| RCAEval install fails | use Python 3.12 and a clean venv; see RCAEval docs/SETUP.md |

Yashaswini Penumarthi (24262404)
