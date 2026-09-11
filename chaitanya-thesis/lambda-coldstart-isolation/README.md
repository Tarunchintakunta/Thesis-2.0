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
│                      budget_guard.py, mock_cloudwatch.py, local_init_bench.py, check_*.py
├── configs/           experiment.yaml, pilot.yaml, analysis_plan.yaml, pricing.yaml, mock_model.yaml
├── data/              processed/{live,mock}, pilot/, proxy/   (raw dumps are git-ignored)
├── figures/           live/ (empty until the campaign), mock/ (SYNTHETIC), proxy/, proxy_dev/
├── reports/           configuration_manual.md, outputs_summary.md, paper/tables/, weekly/, viva/
├── notebooks/         analysis.ipynb
├── docs/              ASSUMPTIONS, ANALYSIS_PLAN, ETHICS_NOTES, ARCHITECTURE, DATASET, PROGRESS
├── bib/references.bib 26 entries, all resolved online by scripts/check_bib.py
└── tests/
```

## The workload

Parse the fixed payload, run 20,000 rounds of SHA-256 over the previous digest,
count and sum 20 integers, return `{ok, digest, n, items, items_total}`. All six
variants return digest `d8d5607b...a44878`; CI builds every package (including
the Java jars with Corretto 21) and checks this on every push.

| package | zip | unzipped | files |
|---|---|---|---|
| python default (boto3, requests, sympy - imported, never used) | 21.0 MB | 49.8 MB | 3,751 |
| python optimised (stdlib only) | 604 B | 854 B | 1 |
| nodejs default (aws-sdk v2, lodash, moment, axios) | 16.5 MB | 111.5 MB | 4,680 |
| nodejs optimised (no dependencies) | 815 B | 971 B | 2 |
| java default (jackson-databind, guava, commons-lang3 shaded, touched in static fields) | 6.3 MB | 14.3 MB | 3,978 |
| java optimised (no dependencies) | 4.9 KB | 7.0 KB | 5 |

The Java jars are built on the CI runner (Corretto 21 + Maven). The sha256 of
every package is in `data/proxy/github/run_info.json`; the Python and Node.js
zips get exactly the same hashes on the macOS laptop, so the packaging is reproducible.

## Results so far

### 1. Local init proxy (real measurement - but NOT Lambda)

A fresh process per sample loads the exact Lambda package and runs the payload
once (`python -B -s -S`, `node`, `java -cp`), in interleaved randomised blocks.
This measures runtime start + package loading on one machine. It has no
micro-VM, no code download and no Lambda runtime API, so the numbers are **not**
Init Durations; they only say something about *relative* load cost.

**GitHub Actions `ubuntu-latest` runner** (x86_64, 4 vCPU, Python 3.12.14,
Node.js 20.20.2, Corretto 21.0.12; 40 blocks, workflow run 34603856172, no failed
runs). This is the main proxy dataset because all three runtimes share one machine.

| runtime | package | init proxy p50 (ms) | p95 | p99 | first handler run p50 (ms) |
|---|---|---|---|---|---|
| python | default | 2383.7 | 2413.0 | 2419.7 | 8.4 |
| python | optimised | 20.9 | 25.5 | 26.2 | 8.5 |
| nodejs | default | 323.6 | 335.3 | 336.6 | 50.3 |
| nodejs | optimised | 30.4 | 36.0 | 37.4 | 38.2 |
| java | default | 223.1 | 248.1 | 251.4 | 67.8 |
| java | optimised | 37.2 | 41.2 | 42.3 | 84.8 |

* H1-proxy (optimised packages): Kruskal-Wallis p = 3.4e-22 after Holm,
  epsilon^2 = 0.85. The runtimes differ, but only by about 16 ms at the median.
* H2-proxy: pruning cuts the median by 2362.8 ms (Python), 293.2 ms (Node.js)
  and 185.9 ms (Java); p = 4.3e-14 for each after Holm, rank-biserial 1.00.
* Java's JVM starts about as fast as the others with a small jar, but its first
  handler run is the slowest (68-85 ms against about 8 ms for Python) because
  nothing is JIT-compiled yet. If that happens on Lambda too it lands in the cold
  call's Duration, not its Init Duration - one reason the study records both.

Tables and figures: `reports/paper/tables/proxy/`, `figures/proxy/`.

Development laptop (Apple Silicon, macOS, 30 blocks, no JDK so no Java) - supplementary:

| runtime | package | init proxy p50 (ms) | p95 | p99 | handler p50 (ms) |
|---|---|---|---|---|---|
| python | default | 856.2 | 945.8 | 963.0 | 4.0 |
| python | optimised | 16.5 | 18.6 | 21.4 | 4.1 |
| nodejs | default | 131.7 | 145.1 | 152.0 | 8.4 |
| nodejs | optimised | 46.6 | 50.3 | 51.2 | 9.8 |

Pruning: median difference 839.7 ms (Python) and 85.0 ms (Node.js), Mann-Whitney
p = 3e-11 for both after Holm, rank-biserial 1.00 (every default sample was
slower than every optimised one). Full tables: `reports/paper/tables/proxy_dev/proxy_summary.md`.

What it suggests (to be checked on Lambda, not claimed): the unused
dependencies cost far more than the runtime choice, and most of the Python
default's cost is compiling the libraries from source. On Lambda `/var/task` is
read-only, so bytecode that is not shipped in the zip cannot be cached between
cold starts either. Whether shipping `.pyc` files helps on Lambda is not tested
here (future work).

### 2. Mock pipeline (SYNTHETIC - pipeline test only)

`make mock-all` pushes about 3,800 synthetic invocations through the whole
chain and produces every figure and the decision matrix in `figures/mock/` and
`reports/paper/tables/mock/`. Those numbers come from placeholder parameters in
`configs/mock_model.yaml`, are watermarked SYNTHETIC and mean nothing about
Lambda. They exist so the student can see the outputs before paying for a live run.

## Honesty rules built into the code

* every row carries `data_mode`; the analysis refuses to mix `live` and `mock`
* every mock figure is watermarked, every mock table says SYNTHETIC
* the proxy benchmark is always called a proxy
* intended-cold calls that came back warm are counted and published, never analysed as cold
* the budget guard stops a live run before it can pass the daily cap

## What is left for the student

1. Deploy to their own AWS account, run the live pilot and freeze the sample sizes.
2. Run the live campaign (Phase A, H1-H4, burst, combined), collect, analyse.
3. Write the report, weekly reports and viva material (templates and checklists only are here).
4. Confirm the Node.js 20 runtime choice with the supervisor (`docs/ASSUMPTIONS.md` A3).
