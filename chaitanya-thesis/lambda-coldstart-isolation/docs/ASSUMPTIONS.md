# Assumptions and decisions

Kondragunta Lakshmi Chaitanya - 25171216

Things the master prompt left open, what was chosen and why. If one of these
changes, write the date and the reason underneath instead of deleting it.

## Platform and scope

| # | Decision | Why |
|---|---|---|
| A1 | One region, `eu-west-1`, one account (the student's own). | Controls. Results are single-region, single-provider and are not generalised to other clouds. |
| A2 | Architecture fixed to **arm64** for every function. | Master prompt 3.5. Bluemke and Zdanowski (2025) found arm64 cheaper, and fixing one arch removes a factor. |
| A3 | Runtimes: `python3.12`, `nodejs20.x`, `java21` (Corretto 21) managed runtimes, zip packages. | Master prompt 3.4. Container images and SnapStart are future work. **Note:** cfn-lint reports that AWS deprecated `nodejs20.x` on 2026-04-30 (new functions can still be created until 2027-02-01). It is kept because the proposal fixes Node.js 20; the student should confirm with the supervisor, and if the campaign runs after February 2027 (or the supervisor prefers a supported runtime) switch to `nodejs22.x` and record it as an amendment. |
| A4 | Provisioned concurrency and SnapStart are **not** treatments. The warmer is an EventBridge `rate(5 minutes)` rule. | Master prompt 3.1 and the warming gate. |
| A5 | Function timeout 30 s, log retention 7 days, X-Ray off by default (can be switched on with a template parameter). | Keeps cost and noise down; REPORT lines already carry the numbers needed. |

## Workload

| # | Decision | Why |
|---|---|---|
| W1 | The same work everywhere: parse the fixed payload, 20,000 rounds of SHA-256 over the previous digest, count and sum 20 integers, return `{ok, digest, n, items, items_total}`. | Master prompt 5.2. SHA-256 is in every standard library, so the optimised variants need no dependency at all. |
| W2 | `n = 20000` is never changed between variants. | Only packaging and configuration change. |
| W3 | Default packages carry heavy libraries that are imported at module level but never used: Python `boto3 1.35.36`, `requests 2.32.3`, `sympy 1.14.0`; Node `aws-sdk 2.1692.0`, `lodash`, `moment`, `axios`; Java `jackson-databind`, `guava`, `commons-lang3` shaded into one jar and touched in static fields. | This is the "import everything at the top" pattern the package-size question is about. Exact sizes and sha256 go to `build/package_manifest.json`. |
| W4 | Warmer pings send `{"warmer": true}` and the handler returns straight away. | A ping should keep the environment alive without doing the work. |
| W5 | Packages are reproducible: zips have sorted entries and a fixed timestamp, no `__pycache__`, and pip's `bin/` console-script wrappers and `*.dist-info/RECORD` files are removed. | The wrappers carry the build machine's interpreter path, so the zip hash changed from machine to machine. Lambda never runs them. |
| W6 | Python packages are shipped without `.pyc` files and the local benchmark runs Python with `-B`. | `/var/task` is read-only on Lambda, so bytecode that is not in the zip is compiled on every cold start; the proxy has to do the same. Shipping `.pyc` could be a further "free" control - future work. |
| W7 | **2026-09-20:** `python-bytecode` cell formally dropped from confirmatory H2. | Live lite: all 24 invocations `function_error=Unhandled`, no Init Duration. Residual is documented, not fixed by a new deploy. |

## Measurement

| # | Decision | Why |
|---|---|---|
| M1 | An invocation is **cold if and only if its REPORT line has `Init Duration`**. | Master prompt 3.7. Intent does not count. Intended-cold calls that came back warm are counted and published. |
| M2 | Cold starts are forced by updating an environment variable (`COLD_TOKEN`) or the memory size before the call (`force_cold: update_env`). The idle method (`force_cold: idle`, wait `idle_gap_min`) is kept and is checked in the pilot `idle_probe`. | Waiting 30+ minutes per cold sample would make ~1,000 cold samples take weeks. A configuration change gives new execution environments on the next call. The pilot shows how often each method really gives a cold start. |
| M3 | Client round-trip time is measured around `lambda.invoke()` (boto3, `LogType=Tail`). The REPORT line comes from the 4 KB log tail and, as a cross-check, from CloudWatch Logs (`collect_logs.py`), joined on request id. | Master prompt 5.3. |
| M4 | Warm Duration for the Phase A (baseline-style) sweep: two warm-up calls per block are thrown away, then one measured call. | Steady-state duration like Bluemke and Zdanowski, without init. |
| M5 | Cost uses the public list price in `configs/pricing.yaml` (arm64 GB-s price + request charge), free tier ignored. INIT billing: if a REPORT line's Billed Duration does not already include the init time, the init time is added (`bill_init_phase: true`). | AWS announced INIT phase billing for on-demand functions from 1 August 2025; the student has to re-check the pricing page and the REPORT format before the live campaign. |
| M6 | Configurations are run in **interleaved randomised blocks** (each block holds every cell once, shuffled). | Wen et al. (2025): performance varies with time, so no cell should get all its samples in one time window. |

## Local and offline work

| # | Decision | Why |
|---|---|---|
| L1 | `DATA_MODE=mock` (the default) runs the whole pipeline against `src/coldstart/mock.py`, which makes synthetic REPORT lines from placeholder parameters in `configs/mock_model.yaml`. Every mock row, table and figure is labelled SYNTHETIC. | Master prompt 5.9. Mock output is for testing the pipeline and is never a result. |
| L2 | A real **local process-start benchmark** (`scripts/local_init_bench.py`) starts a new process for every sample and loads the exact Lambda package. It is called an *init proxy* everywhere. | It is a real measurement of what the package and runtime cost to load, but it has no micro-VM, no code download and no Lambda runtime API, so it is not an Init Duration. |
| L3 | The official proxy dataset is measured on a GitHub Actions `ubuntu-latest` runner (all three runtimes on the same machine). The developer laptop runs are only for development. | Runtimes must be compared on the same machine; Java is not installed on the laptop. |

## Analysis (details frozen in ANALYSIS_PLAN.md)

| # | Decision | Why |
|---|---|---|
| S1 | alpha = 0.05, Holm-Bonferroni over the confirmatory family H1, H2 (x3 runtimes), H3. H4 is exploratory and corrected on its own. | Master prompt 3.6. |
| S2 | Reference memory for H1/H2 is 1024 MB. | Middle of the range, well above the 128 MB where CPU starvation would dominate everything. |
| S3 | "Combined free controls" is pre-registered as optimised package + 1024 MB vs default package + 128 MB (console default). | Chosen before any data, so the combined row is not cherry-picked from H4. |
