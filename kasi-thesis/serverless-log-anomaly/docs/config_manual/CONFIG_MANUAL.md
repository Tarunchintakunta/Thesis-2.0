# Configuration Manual

**Project:** Source-Free Log Anomaly Detection for AWS Serverless Applications:
Measuring the Accuracy Forfeited When No Labelled Source Exists
**Student:** Kasireddy Vadicharla (25104047) - MSc in Cloud Computing, National College of Ireland

How to install, configure and run the artefact, and how to read its outputs.
Separate from the report; not part of the page limit.

---

## 1. What is in the artefact

| Path | Contents |
|------|----------|
| `infra/lambda_app/` | the Orders API Lambda (`handler.py`) and its SAM template |
| `infra/localstack/` | pinned LocalStack compose file (optional live path) |
| `src/logad/collect/` | Lambda runtime emulator, workload, fake DynamoDB, scrubbing, CloudWatch collector, live traffic runner |
| `src/logad/inject/` | fault categories, blocked schedule (ground truth), live fault switch |
| `src/logad/parse/` | fixed Drain parser + fingerprint |
| `src/logad/features/` | 60 s windows, count view (D1), semantic view (D2) |
| `src/logad/source/` | Loghub BGL reader (D2 source) |
| `src/logad/detectors/` | D1 OC-SVM / Isolation Forest, D2 ELFA-Log style transfer, D3 threshold alarms |
| `src/logad/eval/` | metrics, statistics, figures, report |
| `configs/` | experiment, parser, detectors, alarms, smoke and live configs |
| `results/` | window predictions, summaries, statistics, figures, fingerprint, certification |
| `tests/` | unit and integration tests |

**Two ways to get logs:**

* **Emulator (default, free, no Docker):** the real handler runs inside a local
  Lambda runtime emulator on a virtual clock. A full 3-seed campaign
  (~1.5 million log lines) takes about a minute.
* **Live:** LocalStack in Docker or your own AWS account. Real time, so the
  `configs/live.yaml` campaign is much shorter. Implemented and unit tested with
  moto, but not executed while building this repository.

## 2. Prerequisites

| Tool | Version | Needed for |
|------|---------|------------|
| Python | 3.11 or 3.12 | everything |
| git, make, curl, zip | any | scripts |
| Docker + LocalStack 3.8.1 | optional | live path |
| awscli-local, aws-sam-cli | optional | live path |

Python packages are pinned in `requirements.txt` (drain3 is pinned to 0.9.11
on purpose - the parser must not change).

## 3. Setup

```bash
cd kasi-thesis/serverless-log-anomaly
scripts/00_bootstrap.sh     # venv, requirements, editable install, Loghub sample
source .venv/bin/activate
export PYTHONPATH=src
make test                   # unit + integration (smoke pipeline, moto)
make validate               # cfn-lint on the SAM template
```

`scripts/fetch_loghub.sh` downloads `BGL_2k.log` from the Loghub repository
and checks its SHA-256. The file is not committed.

## 4. Running the study (emulator)

| Step | Command | Output |
|------|---------|--------|
| smoke check (seconds) | `make smoke` | `results_smoke/` (not results) |
| logs only | `scripts/02_generate_traffic.sh` | `data/raw/main/seed_*/` |
| full pipeline | `make run` (`scripts/04_train_eval.sh`) | `results/metrics/windows_*_seed_*.csv`, certification, fingerprint |
| statistics + figures | `make report` (`scripts/05_stats_plots.sh`) | `results/metrics/summary.csv`, `results/tables/*.md`, `results/stats/hypotheses.json`, `results/figures/*.png` |
| bundle for submission | `make bundle` | `dist/results_bundle_<date>.zip` |

The pipeline reuses `data/raw/<config>/seed_*` if it exists; `--regenerate`
forces new logs.

## 5. Configuration files

| File | What you can change |
|------|---------------------|
| `configs/experiment.yaml` | seeds, start time, window size, workload (rate, diurnal amplitude, route mix), runtime (memory, timeout, reserved concurrency, cold start), DynamoDB latency, fault strengths, phase lengths, injections per category, block size |
| `configs/drain.yaml` | **fixed** - fingerprinted on the first run; the pipeline refuses to run if it changes afterwards |
| `configs/detectors.yaml` | D1 models + threshold quantile + primary model; D2 source windows, hashing size, SVD, CORAL, pseudo-label rounds/entropy |
| `configs/alarms.yaml` | D3 alarms, calibration quantile, floors |
| `configs/smoke.yaml` | tiny version for CI |
| `configs/live.yaml` | short real-time version for LocalStack / AWS |

Changing `drain.yaml` on purpose means starting a new study: delete
`results/parser_fingerprint.json` and rerun everything.

## 6. Live path (optional)

```bash
make localstack-up                        # docker compose, LocalStack 3.8.1
make deploy-local                         # table, role, function, HTTP API (awslocal)
export AWS_ENDPOINT_URL=http://localhost:4566 AWS_DEFAULT_REGION=eu-west-1
python -m logad.collect.live_traffic --config configs/live.yaml --api-url <API_URL> \
    --role kasireddy-orders-role --out data/raw/live
python -m logad.pipeline --config configs/live.yaml --raw data/raw --out results_live
python -m logad.eval.report --results results_live
make localstack-down
```

For your own AWS account use `TARGET=aws scripts/01_deploy_app.sh` (SAM),
leave `AWS_ENDPOINT_URL` unset, set a billing alarm first, and delete the stack
afterwards (`sam delete --stack-name kasireddy-orders`). Faults are switched by
`LiveFaultSwitch`: a Deny policy on the role, a wrong `TABLE_NAME`,
`DOWNSTREAM_DELAY_MS`, and memory 128 MB. Only ever point it at your own
function.

## 7. Reading the outputs

* `results/metrics/windows_B_seed_<s>.csv` / `windows_C_seed_<s>.csv` - one row
  per 60 s window: `label`, `category`, `block`, `burst`, `cold_starts`, and for
  every detector `score_<det>` (higher = more anomalous) and `pred_<det>`.
  All other numbers are computed from these files.
* `results/metrics/summary.csv` - per detector: precision, recall, F1 with a
  95 % block-bootstrap CI, false-alarm rate on normal phase B windows, phase C
  elasticity false-alarm rate (overall / in bursts / outside bursts), share of
  injections detected, median detection delay.
* `results/tables/per_category.md` - F1 / detection rate / delay per fault category.
* `results/tables/hypotheses.md` and `results/stats/hypotheses.json` - H1, H2
  (one test per approach), H3, Holm-adjusted p-values, effect sizes, the
  pre-registered decision rule, McNemar tests per category, power check.
* `results/parser_fingerprint.json` - parser + version + config SHA-256.
* `results/certification/seed_<s>.json` - clean-window evidence for phase A.
* `results/run_info.json` - per seed: line counts, templates, D1 validation FAR
  and thresholds, D2 source statistics and pseudo-labelling history, D3 thresholds.

## 8. Troubleshooting

| Problem | Fix |
|---------|-----|
| `SourceMissing: ... BGL_2k.log not found` | `scripts/fetch_loghub.sh` |
| `ParserChanged` | `configs/drain.yaml` or the drain3 version differs from the fingerprint - restore it |
| `TrainingWindowNotClean` | something faulty ended up in phase A - check `results/certification/` and the schedule |
| `lines still carry identifiers after scrubbing` | a new identifier format appeared - extend `collect/scrub.py` |
| `ModuleNotFoundError: logad` | `export PYTHONPATH=src` or `pip install -e .` |
| LocalStack deploy fails | `make localstack-up`, wait for `curl localhost:4566/_localstack/health` |

## 9. Reproducibility

Seeds, the parser fingerprint, the clean-window certificates and the ground
truth (inside `data/raw/.../ground_truth.csv`) fully determine a run; rerunning
`make run report` with the same configs regenerates the same window CSVs.

Kasireddy Vadicharla
