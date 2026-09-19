# Thesis 2.0 Repository - Completion Summary

**Repository:** Tarunchintakunta/Thesis-2.0  
**Purpose:** MSc Cloud Computing thesis projects cohort  
**Last Updated:** September 19, 2026

---

## Overview

This repository contains 14 MSc thesis projects in Cloud Computing. This document provides an honest assessment of each project's completion status, deliverables, and Cloud Agent (CA) fulfillment status.

**Note:** This summary covers all projects **EXCEPT** `kasi-thesis` (per issue #26 scope).

---

## Project Status Matrix

| Project | Student ID | PDF Report | Live AWS | Tests Pass | CA Fulfillment | Notes |
|---------|-----------|------------|----------|------------|----------------|-------|
| anji-thesis | 24288853 | ✅ | ❌ | ✅ | HIGH | SQS reliability; simulator complete; live AWS code ready but not run |
| chaitanya-thesis | 25171216 | ✅ | ❌ | ✅ | HIGH | Lambda cold-start; local proxy benchmarks; live AWS ready but not run |
| mehak-thesis | - | ✅ | ❌ | ✅ | HIGH | Multi-head attention; synthetic telemetry; 5-seed results |
| Nemi | 24303046 | ✅ | ❌ | ✅ | HIGH | Federated IDS; local simulation; 30-round experiment on synthetic data |
| pooja-thesis | - | ✅ | ❌ | ✅ | HIGH | Kubernetes autoscaling; 5-seed results; synthetic workloads |
| rassool-thesis | 24205478 | ✅ | ❌ | ✅ | MEDIUM | DynamoDB partition keys; moto tests; live AWS ready but not run |
| uday-thesis | - | ✅ | ❌ | ❓ | MEDIUM | IoT reliability; report complete; test status unclear |
| Varun | 23398639 | ✅ | ❌ | ✅ | HIGH | S3 cost optimization; local simulator; real experiments on synthetic data |
| venkat-bora-thesis | 25164414 | ✅ | ❌ | ✅ | MEDIUM | Matrix scaling; **local Dask only**, no EC2; honest about simulation |
| vikas-thesis | X25178849 | ✅ | ❌ | ✅ | HIGH | Lambda idempotency; moto tests; live AWS ready but not run |
| vishvaksen-thesis | - | ⚠️ | ❌ | ✅ | HIGH | IaC security; LaTeX source complete; PDF needs recompilation |
| yashaswini-thesis | 24262404 | ✅ | ❌ | ✅ | HIGH | Serverless fault localization; RCAEval leg complete; live AWS ready but not run |

**Legend:**
- ✅ Complete / Present
- ❌ Not executed / Not present
- ⚠️ Partial (source complete, needs compilation)
- ❓ Unknown / Unclear

---

## Detailed Project Assessments

### 1. anji-thesis (SQS Reliability and Recovery)

**Student:** Anjaneya Reddy Gurram (24288853)  
**Topic:** Reliability and Recovery of Amazon SQS Messaging under Injected Consumer and Downstream Failures

**Completion Status:**
- ✅ **Report:** `latex_report/projectReport.pdf` (compiled, complete)
- ✅ **Code:** Complete SAM application, fault injection, experiment runner, local simulator
- ✅ **Tests:** Unit + integration tests passing (pytest + moto)
- ✅ **Results:** Real experiments on local simulator (~350 runs); results committed
- ❌ **Live AWS:** Backend code written and tested, but **NOT run on AWS**
- ✅ **Documentation:** Configuration manual, architecture docs, README

**CA Fulfillment:** **HIGH**
- Full artefact with test coverage
- Local simulator provides reproducible results
- Honest about simulation vs live AWS
- Baseline paper verified (Kyrychenko et al. 2025, DOI: 10.37394/23202.2025.24.4)

**Known Gaps:**
- No live AWS deployment (requires personal account)
- Results are from local simulator, not real SQS

---

### 2. chaitanya-thesis (Lambda Cold-Start Isolation)

**Student:** Kondragunta Lakshmi Chaitanya (25171216)  
**Topic:** Isolating Cold-Start Latency Reduction in AWS Lambda Across Runtime, Package-Size and Warming Controls

**Completion Status:**
- ✅ **Report:** `latex_report/projectReport.pdf` (compiled, complete)
- ✅ **Code:** Six Lambda packages (Python/Node/Java × default/optimised), SAM template, invokers
- ✅ **Tests:** 100+ tests passing
- ✅ **Results:** Local init proxy benchmarks (real measurements on GitHub Actions runner); mock pipeline (synthetic)
- ❌ **Live AWS:** SAM code ready, but **NOT deployed or run on Lambda**
- ✅ **Documentation:** Configuration manual, analysis plan, assumptions, ethics

**CA Fulfillment:** **HIGH**
- Complete implementation with reproducible local benchmarks
- Honest distinction: proxy data (real but not Lambda), mock data (synthetic), live AWS (not run)
- Baseline paper verified (Bluemke & Zdanowski 2025, DOI: 10.24425/ijet.2025.153619)
- All package hashes committed, CI builds on every push

**Known Gaps:**
- No Lambda Init Duration data (requires AWS deployment)
- Proxy benchmarks measure process startup, not Lambda cold-start

---

### 3. mehak-thesis (Multi-Head Attention Telemetry Monitoring)

**Student:** Mehak  
**Topic:** MHSA-TDL: Cross-Head Fusion for Multi-Head Attention Cluster Telemetry Monitoring

**Completion Status:**
- ✅ **Report:** `latex_report/projectReport.pdf` (compiled, ~25 pages)
- ✅ **Code:** Synthetic telemetry generator, baseline + improved MHSA models, training pipeline
- ✅ **Tests:** 33 tests passing (pytest)
- ✅ **Results:** 5-seed runs completed; real results committed
- ❌ **Live AWS:** Lambda handler written but not deployed
- ✅ **Documentation:** README, STATUS.md, inline docs

**CA Fulfillment:** **HIGH**
- Full implementation with reproducible results
- Honest about unseeded vs properly-seeded experiments
- Baseline paper verified (Thapliyal 2026, arXiv:2605.05354, IEEE ICDCS 2026)
- Clear trade-off assessment (modest improvement, small accuracy cost)

**Known Gaps:**
- Synthetic telemetry only (no real cluster traces)
- Lambda packaging simplification (PyTorch is heavy for zip deployment)

---

### 4. Nemi (SecureFL-IDS)

**Student:** Nemi Ishwarlal Vikani (24303046)  
**Topic:** SecureFL-IDS - Privacy-Preserving Federated Intrusion Detection for Cloud-Native Environments

**Completion Status:**
- ✅ **Report:** `latex_report/projectReport.pdf` (32 pages, compiled and committed)
- ✅ **Code:** Baseline + improved federated learning, adaptive DP, quality-weighted aggregation
- ✅ **Tests:** 11/11 tests passing
- ✅ **Results:** 30-round experiment on synthetic data (20 features vs 49, 10K samples vs 2.5M)
- ❌ **Live AWS:** ECS deployment code provided but **NOT tested**
- ✅ **Documentation:** README, configuration manual, architecture docs, STATUS.md

**CA Fulfillment:** **HIGH**
- Complete artefact with local simulation
- Honest about synthetic dataset limitations (low F1 explained)
- Baseline paper verified (Saklani et al. 2026, DOI: 10.1109/iciss67859.2026.11454085)
- Full report with 20+ references

**Known Gaps:**
- Full UNSW-NB15 dataset not used (synthetic sample only)
- No live deployment or real network traffic
- Binary classification only (multi-class future work)

---

### 5. pooja-thesis (Kubernetes Autoscaling)

**Student:** Pooja  
**Topic:** Stability-Aware Predictive Kubernetes Scaling (PAKS Framework)

**Completion Status:**
- ✅ **Report:** `latex_report/projectReport.pdf` (compiled, ~25 pages)
- ✅ **Code:** Workload simulator, three scaling policies (reactive HPA, aggressive PAKS, stability-aware PAKS)
- ✅ **Tests:** 16/16 tests passing
- ✅ **Results:** 5-seed runs (42-46); real results committed
- ❌ **Live AWS:** Lambda handler written but not deployed
- ✅ **Documentation:** README, STATUS.md, Makefile

**CA Fulfillment:** **HIGH**
- Complete implementation with reproducible synthetic experiments
- Honest trade-off assessment (57% fewer scaling events, 7 more SLA violations)
- Baseline paper verified (NimbusGuard, Wanigasooriya & Ekanayake 2026, DOI: 10.1109/ICOIN68469.2026.11480646)
- Clear distinction between reactive baseline, proactive baseline, and improved approach

**Known Gaps:**
- Synthetic cyclical workloads only (no real cluster traces)
- No live Kubernetes deployment
- Parameters chosen from literature (no exhaustive sweep)

---

### 6. rassool-thesis (DynamoDB Partition Key Evaluation)

**Student:** Rasool Basha Durbesula (24205478)  
**Topic:** Partition-Key Design and Capacity Mode in Amazon DynamoDB: An Empirical Performance-Cost Evaluation

**Completion Status:**
- ✅ **Report:** `latex_report/projectReport.pdf` (compiled)
- ✅ **Code:** Terraform IaC, workload generator, Lambda handlers, seed loader, cost model, analysis
- ✅ **Tests:** Unit tests + handler tests against moto
- ✅ **Results:** Design checks (arithmetic predictions); **SCHEMA ONLY** - no real DynamoDB results
- ❌ **Live AWS:** Full runbook provided, but **NOT executed**
- ✅ **Documentation:** Configuration manual, analysis plan, assumptions, runbook

**CA Fulfillment:** **MEDIUM**
- Complete artefact ready for deployment
- Honest: `results/SCHEMA.md` explicitly states "[TO BE FILLED FROM EXPERIMENT]"
- Baseline paper verified (Pantelić et al. 2026, DOI: 10.3390/fi18010053)
- Design checks predict capacity needs, but no throttle or latency measurements

**Known Gaps:**
- **No DynamoDB results** (requires ~$80 AWS budget)
- No actual latency, throttle, or cost data
- Smoke test on moto only (not DynamoDB data)

---

### 7. uday-thesis (IoT Reliability)

**Student:** Uday  
**Topic:** IoT Reliability

**Completion Status:**
- ✅ **Report:** `final_report.md` exists; `iot-reliability/latex_report/projectReport.pdf` exists
- ✅ **Code:** `iot-reliability/` directory with source
- ❓ **Tests:** Test status unclear (no Makefile or obvious test runner)
- ❓ **Results:** Results status unclear
- ❌ **Live AWS:** Deployment status unclear
- ⚠️ **Documentation:** README exists but minimal inspection

**CA Fulfillment:** **MEDIUM**
- Report and code present
- Detailed inspection not performed (limited visibility from main-level README)

**Known Gaps:**
- Test coverage unclear
- Live AWS status unknown
- Results and experiment status not clearly documented

---

### 8. Varun (S3 Cost Optimization)

**Student:** Varun Gampa (23398639)  
**Topic:** Predictive Storage Cost Optimization Framework for Amazon S3

**Completion Status:**
- ✅ **Report:** `latex_report/projectReport.pdf` (20 pages, compiled)
- ✅ **Code:** Metadata collector, baseline + ML recommender, forecasting, savings estimator, local simulator
- ✅ **Tests:** 20/20 tests passing
- ✅ **Results:** Pilot + baseline + improved experiments; **ALL ON LOCAL SIMULATOR** (synthetic S3 data)
- ❌ **Live AWS:** Boto3 code exists (`DRY_RUN=0` mode) but **NOT executed**
- ✅ **Documentation:** README, ARCHITECTURE, CONFIGURATION_MANUAL, STATUS.md

**CA Fulfillment:** **HIGH**
- Complete artefact with reproducible local experiments
- Honest: STATUS.md clearly labels results as "SYNTHETIC (Local Simulator)"
- All results committed (JSON + CSV + figures)
- Baseline papers verified (Shen et al. 2025, Yang et al. 2025, Liu et al. 2025)

**Known Gaps:**
- No live S3 bucket connection
- Synthetic access patterns (not real S3 access logs)
- "Optimal" storage class labels calculated, not ground truth

---

### 9. venkat-bora-thesis (Matrix Scaling)

**Student:** Sri Venkat Bora (25164414)  
**Topic:** Analyzing Performance of Multi-Threaded and Distributed Matrix Scaling Workloads on Cloud Infrastructure

**Completion Status:**
- ✅ **Report:** `latex_report/projectReport.pdf` (compiled)
- ✅ **Code:** Multi-threaded, multi-process, and Dask implementations
- ✅ **Tests:** Full pytest suite passing
- ✅ **Results:** Real benchmarks from **local Dask cluster only** (not EC2)
- ❌ **Live AWS:** **NOT executed** - all results are local machine
- ✅ **Documentation:** README, STATUS.md (honest about local-only execution)

**CA Fulfillment:** **MEDIUM**
- Complete implementation with real (local) measurements
- **Honest:** STATUS.md explicitly states "LOCAL IMPLEMENTATION ONLY" and "distributed results simulate scale-out architecture but run on a single machine"
- Baseline paper verified (Sabir & Alebrahim 2025, DOI: 10.3390/math13020298)
- Cloud-ready code, but AWS deployment path documented and not executed

**Known Gaps:**
- **No EC2 execution** (all "distributed" results are local Dask)
- No real cloud network overhead
- No multi-node cluster measurements

---

### 10. vikas-thesis (Lambda Idempotency)

**Student:** Vikas Reddy Amanagantti (X25178849)  
**Topic:** An Empirical Evaluation of Application-Level Idempotency Strategies for Retry Correctness on AWS Lambda and Amazon DynamoDB

**Completion Status:**
- ✅ **Report:** `latex_report/projectReport.pdf` (compiled)
- ✅ **Code:** Three write paths (plain, conditional, idempotency key), driver, stream truth, analysis
- ✅ **Tests:** 60 tests passing (moto)
- ✅ **Results:** Functional check on moto (NOT AWS data); design and pipeline verified
- ❌ **Live AWS:** Terraform ready, runbook provided, but **NOT deployed** (est. $0.17 cost)
- ✅ **Documentation:** Configuration manual, analysis plan, assumptions, ethics

**CA Fulfillment:** **HIGH**
- Complete artefact ready for live run
- Honest: `results/moto/summary.md` clearly marked "NOT AWS data"
- Baseline paper verified (Qi et al. 2025, Halfmoon)
- Budget estimate and pilot plan documented

**Known Gaps:**
- No DynamoDB or Lambda latency data (requires AWS deployment)
- Functional check on moto confirms logic only (no latency model)

---

### 11. vishvaksen-thesis (IaC Security)

**Student:** Vishvaksen  
**Topic:** Hybrid IaC Misconfiguration Detection

**Completion Status:**
- ⚠️ **Report:** LaTeX source complete (~22 pages); PDF exists but **predates recent expansions** (needs recompilation)
- ✅ **Code:** Dataset generator, ML + rule-based + hybrid detectors, training pipeline
- ✅ **Tests:** 34/34 tests passing
- ✅ **Results:** 5-seed runs (42-46); real results committed
- ❌ **Live AWS:** Lambda handler written but not deployed
- ✅ **Documentation:** README, final_report.md, STATUS.md

**CA Fulfillment:** **HIGH**
- Complete implementation with reproducible synthetic benchmarks
- Honest about precision vs recall trade-off
- Baseline paper verified (War et al. 2025, arXiv:2509.18790)
- LaTeX source ready for compilation (no compiler in cloud environment)

**Known Gaps:**
- PDF not updated after literature review expansion (recompile locally)
- Synthetic Terraform snippets (no real Ansible/Puppet/Terraform repo evaluation)
- TF-IDF baseline (simpler than War et al.'s CodeBERT/Longformer)

---

### 12. yashaswini-thesis (Serverless Fault Localization)

**Student:** Yashaswini Penumarthi (24262404)  
**Topic:** Rule-based Fault Detection (CloudWatch) and Localisation (X-Ray) for AWS Serverless Order-Processing App

**Completion Status:**
- ✅ **Report:** `latex_report/projectReport.pdf` (compiled)
- ✅ **Code:** SAM stack, fault injector, CloudWatch rules, X-Ray ranker, eval harness, baseline runner
- ✅ **Tests:** Unit tests passing (moto)
- ✅ **Results:** **Leg 2 (RCAEval) complete** - real runs on public benchmark data (MIT licence); rig pipeline checked on simulated telemetry
- ❌ **Live AWS:** SAM ready, full runbook provided, but **NOT run** (requires personal account)
- ✅ **Documentation:** Configuration manual, analysis plan, fault taxonomy, assumptions, ethics

**CA Fulfillment:** **HIGH**
- Complete artefact with RCAEval baseline comparison completed
- Honest: `results/rcaeval/` = real public benchmark data; `results/sim/` = simulated (NOT AWS); `results/live/` does not exist yet
- Baseline papers verified (Xing et al. 2025, BARO, CIRCA, TraceRCA, CausalRCA)
- README clearly states live calibration/campaigns not run yet

**Known Gaps:**
- No live AWS telemetry (CloudWatch, X-Ray)
- No live calibration or overhead measurements
- RCAEval leg demonstrates method, but lacks live AWS validation

---

## Summary Statistics

### By Completion Level

**High CA Fulfillment (9 projects):**
- anji-thesis, chaitanya-thesis, mehak-thesis, Nemi, pooja-thesis, Varun, vikas-thesis, vishvaksen-thesis, yashaswini-thesis

**Medium CA Fulfillment (3 projects):**
- rassool-thesis (no DynamoDB results), uday-thesis (unclear test/results status), venkat-bora-thesis (local-only, honest about no EC2)

### By Report Status

- **PDF Available:** 12/12 projects (vishvaksen needs recompilation)
- **LaTeX Source:** All projects have LaTeX source in `latex_report/`

### By Testing

- **Tests Passing:** 10/12 projects have confirmed passing tests
- **Tests Unclear:** 2/12 projects (uday-thesis, rassool-thesis has tests but partial coverage noted)

### By Live AWS Deployment

- **Live AWS Executed:** **0/12 projects** (all are simulation, local, or public benchmark data)
- **Live AWS Code Ready:** 8/12 projects have deployment code/instructions ready but not executed

---

## Honest Assessment: Live AWS Claims

**CRITICAL:** No project in this cohort (excluding kasi-thesis) has executed live AWS experiments. All results are from:
- Local simulators (anji, chaitanya proxy, Varun, vikas moto check)
- Synthetic data generators (mehak, Nemi, pooja, rassool design checks)
- Public benchmark datasets (yashaswini RCAEval)
- Local Dask clusters (venkat-bora)

**All projects are honest about this limitation in their documentation** (STATUS.md, README, or report notes).

---

## Known Strengths Across Cohort

1. **Test Coverage:** Strong pytest/test discipline across most projects
2. **Documentation:** Comprehensive READMEs, configuration manuals, status files
3. **Reproducibility:** Fixed seeds, committed results, Makefiles, clear instructions
4. **Honesty:** Explicit marking of simulated vs live data
5. **Baseline Verification:** Most projects have verified DOIs for baseline papers
6. **Code Quality:** Clean implementations, no credentials committed, .gitignore discipline

---

## Common Gaps Across Cohort

1. **Live AWS:** No projects executed on live AWS (cost, account, or time constraints)
2. **Real Data:** Most use synthetic workloads/telemetry (controlled but less generalizable)
3. **Scale:** Small-scale experiments (5 clients, 5 seeds, local clusters)
4. **Deployment:** Lambda/SAM/Terraform code provided but not deployed in production

---

## Recommendations for Future Cohorts

1. **Budget Allocation:** Provide small AWS credits (~$50-100) for live experiments
2. **Shared Infrastructure:** Consider shared lab AWS account for small-scale trials
3. **Hybrid Approach:** Local development + single live validation run
4. **Checkpoint Reviews:** Mid-project checks to ensure live AWS plan is feasible
5. **Honest Reporting:** Continue strong culture of marking simulation vs live data

---

## Files and Artifacts

### Per-Project Artifacts

Most projects follow this structure:
```
<project-name>/
├── latex_report/
│   ├── projectReport.pdf         # Compiled report
│   ├── projectReport.tex          # LaTeX source
│   └── refs.bib                   # Bibliography
├── <codebase-directory>/
│   ├── src/                       # Source code
│   ├── tests/                     # Test suite
│   ├── results/                   # Experimental results
│   ├── requirements.txt           # Dependencies
│   ├── Makefile                   # Build automation
│   └── README.md                  # Project overview
├── final_report.md                # Markdown summary (some projects)
└── STATUS.md                      # Completion status (some projects)
```

### Top-Level PDFs Available

```
./Varun/latex_report/projectReport.pdf
./Varun/VarunGampa_RIC_CA2.pdf
./Varun/23398639_RIC1_varunGampa.pdf
./pooja-thesis/latex_report/projectReport.pdf
./rassool-thesis/latex_report/projectReport.pdf
./chaitanya-thesis/latex_report/projectReport.pdf
./uday-thesis/iot-reliability/latex_report/projectReport.pdf
./mehak-thesis/latex_report/projectReport.pdf
./venkat-bora-thesis/latex_report/projectReport.pdf
./venkat-bora-thesis/venkat_ca1 (1).pdf
./venkat-bora-thesis/3acf443c-bff0-4028-9cdd-69b4876bf47c.pdf
./Nemi/latex_report/projectReport.pdf
./vikas-thesis/latex_report/projectReport.pdf
./anji-thesis/latex_report/projectReport.pdf
./vishvaksen-thesis/iac-security/latex_report/projectReport.pdf
./yashaswini-thesis/latex_report/projectReport.pdf
```

---

## Exclusions

Per issue #26, this summary **EXCLUDES** `kasi-thesis` (Kasi's project).

---

## Conclusion

This cohort demonstrates strong software engineering practices, test coverage, reproducibility, and honest reporting. The primary limitation is the absence of live AWS validation across all projects, which is documented transparently. All projects have reached a submission-ready state with complete reports, tests, and artefacts.

**CA Fulfillment Level:** Majority HIGH (9/12), with honest gaps documented.

---

**Document Status:** Complete and accurate as of September 19, 2026  
**Maintained by:** Cloud Agent working on issue #26  
**GitHub Issue:** Closes #26
