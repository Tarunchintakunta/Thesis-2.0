# Project Status Report

**Project:** Lambda Cold-Start Isolation  
**Student:** Kondragunta Lakshmi Chaitanya (25171216)  
**Programme:** MSc Cloud Computing, National College of Ireland  
**Date:** September 19, 2026

---

## Overall Status: LOCAL + PROXY COMPLETE — RESIDUAL = LIVE LAMBDA INIT

**Sole residual to answer the CA2 RQ on AWS:** live CloudWatch REPORT *Init Duration* (plus H3 warming frequency and H4 memory cells). Proxy ≠ Init Duration. ROI / ADOPT bands are **not** measured on AWS.

This project investigates cold-start latency reduction in AWS Lambda across runtime languages (Python 3.12, Node.js 20, Java 21), deployment package sizes, memory allocations, and low-frequency EventBridge warming strategies.

---

## 1. Baseline Reference Verification

**✓ VERIFIED** — Baseline paper DOI is valid and accessible:

- **Citation:** Bluemke, I. and Zdanowski, A. (2025) 'Evaluation of configurations of AWS Lambda functions', *International Journal of Electronics and Telecommunications*, 71(3), pp. 1–9.
- **DOI:** [10.24425/ijet.2025.153619](https://doi.org/10.24425/ijet.2025.153619)
- **Publisher:** Polish Academy of Sciences Chancellery (PAS Journals / IJET 2025)
- **Status:** Published and indexed
- **Verification Date:** September 19, 2026

The baseline establishes performance-cost measurement methodology for Lambda configurations. This project extends it by:
1. Isolating `Init Duration` (cold-start initialization) from total `Duration`
2. Comparing three runtimes (Python, Node.js, Java) instead of Python only
3. Measuring package-size effects (bloated vs. optimized dependencies)
4. Testing low-frequency warming (EventBridge scheduler) as a free alternative to provisioned concurrency

---

## 2. Literature Review Status

**STATUS:** Comprehensive (26 verified DOI entries in `bib/references.bib`)

All 26 references have been verified via `scripts/check_bib.py` using DOI content negotiation (Crossref/DataCite metadata). The bibliography covers:

- **Foundational work:** Serverless characterization, benchmarking (Copik et al. 2021, Yu et al. 2020, Eismann et al. 2022)
- **Cold-start systematic reviews:** Golec et al. 2024 taxonomy, Wen et al. 2023 rise of serverless
- **Recent optimization approaches:** Joosen et al. 2025 (EuroSys), Liu et al. 2025 (ASPLOS), Lee et al. 2024 (ICDE)
- **Platform-level innovations:** FaaSnap (Ao et al. 2022), SnapStore (Panda & Sarangi 2023), Pronghorn (Kohli et al. 2024)
- **ML-based prediction:** Saravana Kumar & Selvakumara Samy 2025, Golec et al. 2024 (MASTER)
- **Provisioning strategies:** Vahidinia et al. 2023 (reinforcement learning), Mahgoub et al. 2022 (ORION)
- **Configuration optimization:** Dantas et al. 2022, Eismann et al. 2021 (Sizeless)
- **Benchmarking frameworks:** SeBS (Copik et al. 2021), ServerlessBench (Yu et al. 2020), BeFaaS (Grambow et al. 2021)

The literature review clearly distinguishes:
- **Init Duration** (initialization/cold-start overhead) vs. **Duration** (total execution including handler)
- Developer-adjustable controls (free: runtime, package size, memory, warming) vs. paid options (provisioned concurrency)
- Aggregate metrics (common in prior work) vs. isolated init metrics (this study's focus)

**References:** 15-20 DOIs are directly cited in the main report sections; all 26 are available for comprehensive coverage.

---

## 3. Artefact Implementation Status

### 3.1 Core Infrastructure ✓ COMPLETE

- **Lambda functions:** 6 deployment variants (3 runtimes × 2 package sizes)
  - Python 3.12: default (21.0 MB with boto3/requests/sympy) vs. optimized (604 B, stdlib only)
  - Node.js 20: default (16.5 MB with aws-sdk/lodash/moment) vs. optimized (815 B, no deps)
  - Java 21: default (6.3 MB with Jackson/Guava/Commons) vs. optimized (4.9 KB, no deps)
- **Workload:** Identical SHA-256 digest computation (20,000 rounds) — all variants return digest `d8d5607b...a44878`
- **IaC:** AWS SAM template (`infra/template.yaml`) with 8 Lambda functions, EventBridge warmer rule, IAM roles
- **Deployment scripts:** `scripts/deploy.sh`, `scripts/package_all.sh`, `scripts/teardown.sh`

### 3.2 Data Collection Pipeline ✓ COMPLETE

- **Invokers:** `invoke_idle.py`, `invoke_steady.py`, `invoke_burst.py` (Phase A multi-arm baseline, Phase H1-H4)
- **Log collection:** `collect_logs.py` (CloudWatch Logs Insights queries with automatic retry/pagination)
- **Metric parser:** `parse_report_metrics.py` (extracts `Init Duration`, `Duration`, `Billed Duration`, `Memory Used`)
- **Cost model:** `cost_model.py` (pricing.yaml: $0.0000166667/GB-sec + $0.20/1M requests)
- **Statistical analysis:** `analyse.py` (Shapiro-Wilk → Kruskal-Wallis/ANOVA + Mann-Whitney U/Welch t, Holm-Bonferroni correction, effect sizes)

### 3.3 Testing Infrastructure ✓ COMPLETE

- **Test suite:** 100+ pytest tests across 16 test modules
- **Coverage areas:**
  - Parser: CloudWatch REPORT line extraction, Init Duration detection
  - Cost model: GB-sec calculations, per-invocation costs
  - Statistical tests: normality checks, hypothesis test selection, power analysis
  - Mock backend: synthetic data generation with configurable variance
  - Digest validation: all 6 packages return identical output
  - Configuration: YAML schema validation, experiment/pilot/analysis plans
  - Packaging: reproducible builds (sha256 checksums match across environments)
- **CI/CD:** GitHub Actions workflow builds all 6 packages (including Java with Corretto 21 + Maven)
- **Verification:** `make test` passes all tests; `make gate` confirms digest uniformity

### 3.4 Local Proxy Benchmarks ✓ REAL DATA

**Purpose:** Measure *relative* package-loading costs in a controlled environment (NOT Lambda Init Duration, but validates package-size hypothesis direction)

**Datasets:**
1. **GitHub Actions `ubuntu-latest` runner** (PRIMARY — all 3 runtimes on same x86_64 machine):
   - Python 3.12.14, Node.js 20.20.2, Corretto 21.0.12
   - 40 randomized blocks (workflow run 34603856172)
   - Results in `data/proxy/github/`, figures in `figures/proxy/`

2. **Development macOS laptop** (SUPPLEMENTARY — Python & Node.js only):
   - Apple Silicon, 30 blocks
   - Results in `data/proxy/dev_macbook/`, figures in `figures/proxy_dev/`

**Key findings (proxy benchmark, NOT Lambda claims):**
- Python default (21 MB): median 2383.7 ms → optimized (604 B): 20.9 ms (**2362.8 ms reduction, p = 4.3e-14**)
- Node.js default (16.5 MB): median 323.6 ms → optimized (815 B): 30.4 ms (**293.2 ms reduction, p = 4.3e-14**)
- Java default (6.3 MB): median 223.1 ms → optimized (4.9 KB): 37.2 ms (**185.9 ms reduction, p = 4.3e-14**)

**Honesty:** Labeled as "proxy" or "local init benchmark" everywhere; never claimed as Lambda Init Duration.

### 3.5 Mock Pipeline ✓ SYNTHETIC VALIDATION ONLY

- **Purpose:** Validate end-to-end pipeline (invoke → collect → parse → cost → analyze → figures/tables) before AWS run
- **Command:** `make mock-all` (regenerates all mock outputs in ~5 seconds)
- **Data mode:** `data_mode=mock` (analysis refuses to mix mock and live)
- **Outputs:** All figures watermarked "SYNTHETIC", all tables labeled "SYNTHETIC — MOCK DATA ONLY"
- **Status:** Pipeline validated; results are meaningless placeholders based on `configs/mock_model.yaml`

---

## 4. AWS Execution Status

### 4.1 Live Lambda Deployment: **NOT YET RUN**

**Reason:** Requires student's personal AWS account (ethics Scenario 3: self-owned infrastructure)

**Prerequisites (documented in `reports/configuration_manual.md`):**
1. AWS CLI configured with credentials (IAM user with Lambda/CloudWatch/EventBridge/S3 permissions)
2. AWS SAM CLI installed
3. Budget guard: `scripts/budget_guard.py` caps spend at configured daily limit
4. Estimated cost: ~$2–5 for pilot + campaign (free tier eligible, actual cost depends on sample sizes)

**Deployment steps ready:**
```bash
bash scripts/deploy.sh                     # SAM build + deploy
make MODE=live pilot                        # run pilot, freeze sample sizes
make MODE=live campaign pipeline            # run full experiment, analyze
```

### 4.2 Current Dataset Status

| Dataset | Status | Data Mode | Purpose | Location |
|---------|--------|-----------|---------|----------|
| **Proxy benchmark (GitHub CI)** | ✓ REAL | `proxy` | Validate package-size hypothesis direction | `data/proxy/github/` |
| **Proxy benchmark (macOS)** | ✓ REAL | `proxy` | Supplementary cross-platform check | `data/proxy/dev_macbook/` |
| **Mock pipeline run** | ✓ SYNTHETIC | `mock` | Pipeline validation only | `data/*/mock/` |
| **Live Lambda pilot** | ⧗ NOT RUN | `live` | Power analysis, freeze N | `data/pilot/live/` (empty) |
| **Live Lambda campaign** | ⧗ NOT RUN | `live` | H1–H4 hypothesis tests | `data/*/live/` (empty) |

**Key distinction:**
- **Proxy benchmarks** = REAL measurements of package-loading time in isolated processes (valid for relative comparisons, NOT Lambda Init Duration)
- **Mock data** = SYNTHETIC placeholders to test pipeline mechanics (explicitly labeled, never claimed as results)
- **Live Lambda data** = AWAITING student AWS account (target for final submission)

---

## 5. Research Design Integrity

### 5.1 Pre-registered Analysis Plan ✓ COMPLETE

- **File:** `docs/ANALYSIS_PLAN.md`
- **Hypothesis tests:** H1 (runtimes), H2 (package size, per runtime), H3 (warming), H4 (memory, exploratory)
- **Test selection:** Shapiro-Wilk normality → parametric (ANOVA/Welch t) or non-parametric (Kruskal-Wallis/Mann-Whitney U)
- **Multiple comparison correction:** Holm-Bonferroni over H1 + H2×3 + H3 (5 primary tests)
- **Effect sizes:** Epsilon-squared (Kruskal-Wallis), rank-biserial (Mann-Whitney U), Cohen's d (Welch t), eta-squared (ANOVA)
- **Power analysis:** Pilot-driven sample size determination (`scripts/pilot_power.py`)

### 5.2 Reproducibility Controls

- **Workload validation:** All 6 packages return identical digest (verified in CI and locally via `scripts/check_digests.py`)
- **Packaging reproducibility:** sha256 checksums recorded in `data/proxy/github/run_info.json`
- **Data mode tagging:** Every row carries `data_mode` (live/mock/proxy); analysis refuses mixed modes
- **Budget guard:** Automatic stop before exceeding daily spend cap
- **Intended-cold discarding:** Cold-start invocations that return warm are logged and excluded (never analyzed as cold)

### 5.3 Ethics Compliance

- **Scenario:** Self-owned AWS infrastructure (Scenario 3 — no human subjects, no secondary datasets)
- **Documentation:** `docs/ETHICS_NOTES.md` outlines acceptable-use limits, energy/cost awareness
- **Declaration:** Ethics declaration form ready for Moodle submission
- **Responsible disclosure:** Protocol for reporting unexpected platform behavior

---

## 6. Report and Deliverables Status

### 6.1 Main Report (LaTeX)

**Location:** `latex_report/projectReport.tex` and subsections (`text/*.tex`)

**Structure (NCI template, ≤20 pages):**
1. **Abstract** ✓
2. **Introduction** ✓ (research question, objectives, significance)
3. **Literature Survey** ✓ (3–4 pages, 15–20 DOIs cited, gap analysis)
4. **Research Methodology** ✓ (controlled experiment design, variables, statistical plan)
5. **Design and Implementation Specifications** ✓ (architecture, IaC, workload, instrumentation)
6. **Evaluation** ✓ REWRITTEN (proxy tables only; explicitly no live Init Duration / ROI / ADOPT claims; residual = live Lambda)
7. **Conclusions and Discussion** ✓ QUARANTINED (decision-matrix framework pending live cost cells; proxy ≠ Lambda)
8. **References** ✓ (26 verified entries in `bib/references.bib`)

**Figures/Tables:**
- Methodology diagrams ✓ (experiment phases, statistical decision tree, cost model formula)
- Proxy benchmark results ✓ (tables/figures in `reports/paper/tables/proxy/`, `figures/proxy/`)
- Mock pipeline outputs ✓ (watermarked, `reports/paper/tables/mock/`, `figures/mock/`)
- Live results ⧗ (awaiting AWS run)

**Compilation:** PDF generation via `pdflatex` (requires LaTeX distribution)

### 6.2 Configuration Manual ✓ COMPLETE

**Location:** `reports/configuration_manual.md`

**Contents:**
- AWS prerequisites (CLI, SAM, credentials, permissions)
- Deployment instructions (step-by-step with exact commands)
- Pilot execution and sample-size freezing
- Campaign execution (Phase A, H1–H4, burst, combined)
- Log collection and analysis pipeline
- Budget guard configuration
- Troubleshooting common deployment issues
- Teardown procedure

### 6.3 Weekly Progress Reports ⧗ TEMPLATE

**Location:** `reports/weekly/WEEK_TEMPLATE.md`

**Status:** Template provided; student must populate with actual weekly activities for Moodle submission (12% of final grade)

### 6.4 Viva Materials ⧗ TEMPLATE

**Location:** `reports/viva/README.md`

**Contents (templates provided):**
- Presentation video script outline
- Demo video script outline
- Anticipated examiner questions and preparation notes
- Decision matrix walkthrough

**Status:** Framework ready; student must prepare final scripts and record videos

### 6.5 Outputs Summary ✓ DRAFT

**Location:** `reports/outputs_summary.md`

**Contents:**
- Links to all deliverables (report PDF, code repository, configuration manual)
- Dataset provenance statements (proxy benchmarks: real; mock: synthetic; live: awaiting execution)
- Reproducibility instructions
- Contribution statement

---

## 7. Known Limitations and Future Work

### 7.1 Current Limitations

1. **No live Lambda data yet:** All conclusions about Lambda Init Duration are hypotheses awaiting validation
2. **Proxy benchmarks ≠ Lambda Init Duration:** Local process-start measurements validate *direction* of package-size effect, not exact Lambda magnitudes
3. **Mock data for pipeline testing only:** Synthetic outputs prove mechanics, not results
4. **Node.js 20 runtime choice:** Documented assumption (latest LTS at project start); supervisor confirmation pending (`docs/ASSUMPTIONS.md` A3)
5. **No Java testing on development macOS:** JDK 21 + Maven not installed locally; CI runner handles Java builds

### 7.2 Extensions for Future Work (documented in report)

1. **Bytecode pre-compilation:** Ship `.pyc` files to avoid on-demand compilation (Python lambda read-only `/var/task` limitation)
2. **GraalVM native images:** Test Java ahead-of-time compilation vs. JVM cold starts
3. **SnapStart evaluation:** AWS-native Java optimization (requires Java 11/17 Corretto, account-level enablement)
4. **Provisioned concurrency comparison:** Paid alternative cost-benefit analysis
5. **Multi-region variance:** Test init latency across AWS regions
6. **Real-world workload diversity:** API gateways, S3 triggers, SQS consumers (vs. current synthetic CPU-bound task)

---

## 8. Artifact Checklist

### Code Repository Contents ✓

- [x] Lambda function code (6 variants: `functions/{python,nodejs,java}/{default,optimised}/`)
- [x] Infrastructure-as-Code (SAM template: `infra/template.yaml`)
- [x] Workload and expected output (`payloads/fixed_payload.json`, `payloads/expected_output.json`)
- [x] Deployment scripts (`scripts/package_all.sh`, `scripts/deploy.sh`, `scripts/teardown.sh`)
- [x] Data collection scripts (`scripts/invoke_*.py`, `scripts/collect_logs.py`)
- [x] Analysis pipeline (`scripts/parse_report_metrics.py`, `scripts/cost_model.py`, `scripts/analyse.py`)
- [x] Statistical utilities (`src/coldstart/stats.py`, `src/coldstart/power.py`, `src/coldstart/analysis.py`)
- [x] Test suite (16 modules, 100+ tests in `tests/`)
- [x] Configuration files (`configs/*.yaml`)
- [x] Real proxy data (`data/proxy/github/`, `data/proxy/dev_macbook/`)
- [x] Mock pipeline validation (`data/*/mock/`)
- [x] Documentation (`README.md`, `docs/*.md`, `reports/*.md`)
- [x] Verified bibliography (`bib/references.bib`, `scripts/check_bib.py`)
- [x] CI/CD workflow (`.github/workflows/main.yml`)
- [x] Makefile with common commands (`make test`, `make mock-all`, `make campaign`, etc.)
- [x] Requirements files (`requirements.txt`, `requirements-dev.txt`)

### Documentation Completeness ✓

- [x] README with quick-start instructions
- [x] Configuration manual with deployment guide
- [x] Analysis plan with pre-registered hypotheses
- [x] Assumptions document with supervisor-confirmation notes
- [x] Ethics notes with scenario classification
- [x] Architecture overview
- [x] Dataset provenance statements
- [x] Progress tracking (weekly template provided)

### Quality Gates ✓

- [x] All tests pass (`make test`)
- [x] Digest uniformity verified (`make gate`)
- [x] Bibliography DOIs resolve (`python scripts/check_bib.py`)
- [x] Proxy benchmarks complete with statistical analysis
- [x] Mock pipeline generates all expected outputs
- [x] No credentials committed to repository
- [x] `.gitignore` excludes raw logs, AWS artifacts, virtual environments

---

## 9. Submission Readiness

### Ready for Submission (Local Validation Complete)

- [x] Baseline paper DOI verified and accessible
- [x] Literature review comprehensive (26 verified references, 15–20 cited in report)
- [x] Research design rigorous (pre-registered hypotheses, statistical plan, reproducibility controls)
- [x] Artefact implemented and tested (100+ tests pass, proxy benchmarks complete, mock pipeline validated)
- [x] Report structure complete (NCI template followed, all sections drafted with real content)
- [x] Configuration manual detailed (step-by-step AWS deployment guide)
- [x] Ethics compliant (Scenario 3 self-owned infrastructure, declaration ready)
- [x] Reproducibility ensured (digest validation, package checksums, data mode tagging, budget guard)

### Awaiting Student Action (Requires AWS Account)

- [ ] Deploy to personal AWS account (`bash scripts/deploy.sh`)
- [ ] Run pilot study (`make MODE=live pilot`)
- [ ] Freeze sample sizes based on pilot power analysis
- [ ] Execute full campaign (`make MODE=live campaign pipeline`)
- [ ] Collect live Lambda Init Duration data
- [ ] Populate Evaluation section with live results
- [ ] Generate final decision matrix with live cost-benefit data
- [ ] Finalize Conclusions with Lambda-validated findings
- [ ] Compile final report PDF (`pdflatex projectReport.tex` or similar)
- [ ] Complete weekly progress reports for Moodle
- [ ] Record presentation and demo videos
- [ ] Submit all deliverables via Moodle

---

## 10. Contact and Support

**Student:** Kondragunta Lakshmi Chaitanya  
**Student ID:** 25171216  
**Programme:** MSc Cloud Computing  
**Institution:** National College of Ireland

**Supervisor Confirmation Pending:**
- Node.js 20 runtime choice (documented in `docs/ASSUMPTIONS.md` assumption A3)

**Questions or Issues:**
- Review `reports/configuration_manual.md` for deployment troubleshooting
- Check `docs/ASSUMPTIONS.md` for documented decision rationale
- Consult `docs/ANALYSIS_PLAN.md` for statistical methodology
- See `README.md` for quick-start and layout overview

---

## Residual to 100% CA2 alignment

| Item | Status |
|------|--------|
| Proxy package-size evidence | Present (REAL); labeled not Lambda |
| Mock pipeline | Present (SYNTHETIC); not RQ answer |
| Live Lambda Init Duration (H1 primary) | **NOT RUN** — sole hard residual |
| H3 warming frequency / H4 memory | **NOT RUN** (live) |
| Measured ROI / ADOPT decision matrix | **NOT MEASURED** (framework only) |
| Evaluation chapter predictive-provisioning filler | Removed / quarantined |

Non-AWS claim hygiene for evaluation / STATUS / abstract ROI wording is complete. Remaining blocker to a full RQ answer is live AWS Lambda data collection (no deploy in this pass).

## 11. Honesty and Integrity Statement

This project adheres to strict honesty rules:

1. **Data mode segregation:** Every dataset is tagged (`live`, `mock`, `proxy`); analysis refuses to mix modes
2. **Explicit labeling:**
   - Proxy benchmarks: clearly labeled as "local init benchmark" or "proxy", never claimed as Lambda Init Duration
   - Mock data: watermarked "SYNTHETIC" on all figures, "MOCK DATA ONLY" in all tables
   - Live data: awaiting execution; no fabricated results
3. **Intended-cold validation:** Cold-start invocations that return warm are logged and excluded from cold-start analysis
4. **No invented metrics:** All measurements trace to CloudWatch REPORT lines (Init Duration, Duration, Billed Duration) or instrumented client timestamps
5. **Reproducibility:** Package digests, statistical tests, and analysis decisions are auditable via code and logs

**No results have been fabricated. The proxy benchmarks are real measurements of process-start time (labeled as such). The mock data is explicitly synthetic for pipeline testing only. Live Lambda data awaits student AWS execution.**

---

**Status Summary:** Local artefact, proxy evidence, and claim hygiene are in place. Evaluation no longer claims live Init Duration or measured ROI. **Sole residual:** live Lambda Init Duration (+ H3/H4) on the researcher's AWS account. No AWS deploy in this alignment pass.

**Last Updated:** September 20, 2026  
**Document Version:** 1.1 (claim hygiene)  
**Prepared by:** Project build system (autonomous research assistant)

---

**Final Line (per master prompt requirement):**

Kondragunta Lakshmi Chaitanya
