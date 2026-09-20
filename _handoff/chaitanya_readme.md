# lambda-coldstart-isolation

**Isolating Cold-Start Latency Reduction in AWS Lambda Across Runtime, Package-Size and Warming Controls**

Kondragunta Lakshmi Chaitanya - 25171216 - MSc Cloud Computing, National College of Ireland

Baseline paper: Bluemke, I. and Zdanowski, A. (2025) 'Evaluation of configurations
of AWS Lambda functions', *IJET* 71(3), pp. 1-9, doi:[10.24425/ijet.2025.153619](https://doi.org/10.24425/ijet.2025.153619).

> **Status.** The artefact is built and tested: six Lambda packages, SAM template,
> invokers, parser, cost model, pre-registered analysis and decision matrix. It
> has **not** been run against AWS yet - that needs the student's own account
> (see `reports/configuration_manual.md`). What is in the repo today is
> (a) a synthetic mock run that only proves the pipeline works, and (b) a real
> *local init-proxy* benchmark, which is not Lambda data. No Lambda results are
> claimed anywhere.

## The question

How much of AWS Lambda cold-start latency can be removed by developer-adjustable
controls, and at what cost? Controls: runtime (Python 3.12 / Node.js 20 /
Java 21), package size (default = unused heavy dependencies, optimised = none),
memory (128-3008 MB) and a low-frequency EventBridge warmer (every 5 minutes,
not provisioned concurrency). An invocation counts as cold **only if its REPORT
line has an Init Duration**.

| | Hypothesis | Test |
|---|---|---|
| H1 | Init Duration differs between runtimes | ANOVA / Kruskal-Wallis |
| H2 | Pruning the package changes Init Duration (per runtime) | Welch t / Mann-Whitney U |
| H3 | The warmer changes the cold-start frequency | paired t / Wilcoxon on 20-min blocks (+ Fisher) |
| H4 | Memory changes Init Duration (exploratory) | ANOVA / Kruskal-Wallis |

Shapiro-Wilk picks the test, Holm-Bonferroni over H1 + H2 x3 + H3, effect sizes
always reported. Everything is fixed in `docs/ANALYSIS_PLAN.md`.

## Quick start (no AWS needed)

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
make test                 # 100+ tests
make mock-all             # whole campaign + pipeline + pilot on SYNTHETIC data (~5 s)
bash scripts/package_all.sh python nodejs   # add java if a JDK 21 + Maven is installed
python scripts/check_digests.py             # runtime gate
python scripts/local_init_bench.py --reps 30 --out data/proxy/local
```

Live runs (deploy, pilot, campaign, collect, analyse, teardown) are in
`reports/configuration_manual.md`.

## Layout

```text
lambda-coldstart-isolation/
├── functions/{python,nodejs,java}/{default,optimised}/   same workload, only packaging differs
├── payloads/          fixed_payload.json + expected_output.json (the digest everyone must return)
├── infra/             SAM template (8 arm64 functions, warmer rule created disabled)
├── src/coldstart/     parser, backends (live + mock), driver, cost, stats, analysis, proxy bench
├── scripts/           package_all.sh, deploy.sh, invoke_{idle,steady,burst}.py, collect_logs.py,
│                      parse_report_metrics.py, cost_model.py, analyse.py, pilot_power.py,
