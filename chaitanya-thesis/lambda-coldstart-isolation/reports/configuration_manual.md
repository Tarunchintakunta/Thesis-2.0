# Configuration manual

**Isolating Cold-Start Latency Reduction in AWS Lambda Across Runtime, Package-Size and Warming Controls**

Kondragunta Lakshmi Chaitanya - 25171216 - MSc Cloud Computing, National College of Ireland

This manual lists everything needed to rebuild the artefact, run it (live or
mock) and regenerate every table and figure. Commands run from
`chaitanya-thesis/lambda-coldstart-isolation/` unless noted.

## 1. What is in the artefact

| Part | Where |
|---|---|
| Six Lambda functions: Python 3.12 / Node.js 20 / Java 21 x default / optimised package, same workload | `functions/` |
| Warming pair (target with EventBridge rule, control without) | `infra/template.yaml` |
| Infrastructure as code (AWS SAM) | `infra/template.yaml`, `infra/samconfig.toml` |
| Packaging + package manifest | `scripts/package_all.sh`, `src/coldstart/packaging.py` |
| Invokers (idle / steady / burst), live and mock backends | `scripts/invoke_*.py`, `src/coldstart/{driver,backends,mock}.py` |
| Log collection, REPORT parser, dataset join | `scripts/collect_logs.py`, `scripts/parse_report_metrics.py`, `src/coldstart/{logs,report_parser,metrics}.py` |
| Cost model | `scripts/cost_model.py`, `src/coldstart/cost_model.py`, `configs/pricing.yaml` |
| Pre-registered analysis, decision matrix | `scripts/analyse.py`, `src/coldstart/{analysis,stats}.py`, `docs/ANALYSIS_PLAN.md` |
| Pilot power check, budget guard | `scripts/pilot_power.py`, `scripts/budget_guard.py` |
| Local init-proxy benchmark | `scripts/local_init_bench.py`, `scripts/bench/`, `.github/workflows/chaitanya-proxy-bench.yml` |

## 2. Software versions

| Tool | Version used | Needed for |
|---|---|---|
| Python | 3.12 | everything |
| Node.js | 20.x (CI and proxy bench); any 18+ works for the local tests | Node packages, digest check |
| Java | Amazon Corretto 21 + Maven 3.9 | Java packages (built in CI; not needed for mock runs) |
| AWS SAM CLI | 1.x | live deploy only |
| AWS CLI | v2 | live deploy only (account check, teardown) |

Python packages: `requirements.txt` (runtime) and `requirements-dev.txt` (tests, ruff, cfn-lint).

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
make test
```

## 3. AWS settings (live mode)

| Setting | Value |
|---|---|
| Account | the student's own account (the deploy script prints the account id) |
| Region | `eu-west-1` |
| Stack name | `coldstart-study` (function names `coldstart-study-<runtime>-<variant>`, `-warm-target`, `-warm-control`) |
| Architecture | arm64 for all eight functions |
| Runtimes | `python3.12`, `nodejs20.x`, `java21` (see ASSUMPTIONS A3 about the Node.js 20 deprecation) |
| Memory | 1024 MB at deploy; the invokers set 128-3008 MB per cell with `UpdateFunctionConfiguration` |
| Timeout | 30 s |
| Warmer | EventBridge rule `coldstart-study-warmer`, `rate(5 minutes)`, created **disabled**, enabled only during the warming phase |
| Logs | one log group per function, 7-day retention |
| IAM | SAM creates one basic execution role per function (CloudWatch Logs write only; X-Ray write only if `EnableTracing=true`) |
| Not used | provisioned concurrency, SnapStart, VPC, layers |

The IAM user or role running the invokers needs: `lambda:InvokeFunction`,
`lambda:GetFunctionConfiguration`, `lambda:UpdateFunctionConfiguration`,
`events:EnableRule`, `events:DisableRule`, `logs:FilterLogEvents`, plus the usual
CloudFormation/S3 rights for `sam deploy`.

## 4. Build the packages

```bash
bash scripts/package_all.sh            # python nodejs java -> build/
bash scripts/package_all.sh python nodejs   # on a machine without a JDK
python scripts/check_digests.py --require python,nodejs,java   # runtime gate
```

`build/package_manifest.json` records zip size, unzipped size, file count and
sha256 of every package; `scripts/deploy.sh` copies it to
`data/package_manifest_deployed.json` so the data always sits next to the exact
packages that produced it. Zips are deterministic (sorted entries, fixed
timestamps), so the same source always gives the same hash.

## 5. Deploy, check the budget, tear down

```bash
python scripts/budget_guard.py --plan configs/experiment.yaml   # up-front cost estimate
bash scripts/deploy.sh                                          # STACK / REGION env vars optional
bash scripts/teardown.sh                                        # at the end (collect logs first!)
```

The daily cap is `budget.daily_usd` in `configs/experiment.yaml`; every call is
logged to `data/spend_log.csv` and the invokers stop before a call could pass the cap.

## 6. Pilot, then freeze the sample sizes

```bash
make MODE=live pilot
python scripts/pilot_power.py --in data/pilot/live/ --out docs/ANALYSIS_PLAN.md
```

The second command writes the pilot section of the analysis plan. If it says
"raise", change `reps` in `configs/experiment.yaml` before the main campaign and
note it under Amendments.

## 7. Main campaign

```bash
make MODE=live campaign     # invoke_steady (baseline + warming), invoke_idle (cold phases), invoke_burst
make MODE=live pipeline     # collect_logs -> parse_report_metrics -> cost_model -> analyse
```

Or phase by phase, as in the master prompt:

```bash
DATA_MODE=live python scripts/invoke_steady.py --phase baseline --memories 128,512,1024,3008 --runtime python --variant default --reps 40 --out data/raw/live/
DATA_MODE=live python scripts/invoke_idle.py --phase runtime_compare --reps 50 --out data/raw/live/
DATA_MODE=live python scripts/invoke_idle.py --phase package_size --reps 50 --out data/raw/live/
DATA_MODE=live python scripts/invoke_idle.py --phase memory --reps 40 --out data/raw/live/
DATA_MODE=live python scripts/invoke_steady.py --phase warming --duration 4h --out data/raw/live/
DATA_MODE=live python scripts/invoke_burst.py --phase burst --out data/raw/live/
DATA_MODE=live python scripts/invoke_idle.py --phase combined --out data/raw/live/
DATA_MODE=live python scripts/collect_logs.py --runs data/raw/live/
python scripts/parse_report_metrics.py --in data/raw/live/ --out data/processed/live/metrics.csv
python scripts/cost_model.py --in data/processed/live/metrics.csv --out data/processed/live/costs.csv
python scripts/analyse.py --in data/processed/live/ --out figures/live/ reports/paper/tables/live/
```

A phase folder that already has data is never overwritten; use a new `--out`.

## 8. Mock mode (no AWS account)

`DATA_MODE=mock` is the default. `make mock-all` runs the whole campaign, the
pipeline and the pilot on synthetic data from `configs/mock_model.yaml` and
regenerates `data/processed/mock/`, `figures/mock/` and
`reports/paper/tables/mock/`. Everything it produces is stamped SYNTHETIC and is
for checking the pipeline only.

## 9. Local init-proxy benchmark

```bash
python scripts/local_init_bench.py --reps 30 --out data/proxy/local
python scripts/analyse_proxy.py --in data/proxy/local --out figures/proxy_local reports/paper/tables/proxy_local
```

The committed proxy dataset was measured on a GitHub Actions runner so the three
runtimes share one machine: run the `chaitanya-proxy-bench` workflow
(Actions tab -> Run workflow), then

```bash
gh run download <run-id> -n proxy-bench -D data/proxy/github
make proxy-analysis
```

## 10. Regenerating figures and tables

| Output | Command |
|---|---|
| `figures/<mode>/*.png`, `reports/paper/tables/<mode>/*` | `python scripts/analyse.py --in data/processed/<mode>/ --out figures/<mode>/ reports/paper/tables/<mode>/` |
| `figures/proxy/*.png`, `reports/paper/tables/proxy/*` | `make proxy-analysis` |
| `notebooks/analysis.ipynb` | open in Jupyter; it only reads the processed CSVs |

## 11. Troubleshooting

* `ResourceConflictException` on `UpdateFunctionConfiguration`: an update is still
  in progress; the backend waits with the `function_updated_v2` waiter, so this
  only happens if two invokers run against the same stack at once - don't.
* `TooManyRequestsException` during bursts: account concurrency is lower than 20
  (new accounts can start at 10). Lower `concurrency` in the config.
* No REPORT lines from `collect_logs.py`: log events can take a minute to arrive;
  wait and run it again. The invoke log tail is used as a fallback.
* `cfn-lint` W2531 for `nodejs20.x`: expected, see ASSUMPTIONS A3.
