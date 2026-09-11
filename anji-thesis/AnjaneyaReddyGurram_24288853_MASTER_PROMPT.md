# MASTER PROMPT — MSc Cloud Computing Research Project (Local Execution)

> **INSTRUCTIONS TO CLAUDE / CLAUDE CODE:** You are to execute this entire research project end-to-end on the local machine and the student's own AWS account. Treat every section below as binding. Do not invent citations. Do not skip quality gates. Expand substantially beyond the proposal text (no plagiarism / no copy-paste of RiC proposal wording). Produce artefact, experiments, analysis, report, config manual, weekly-report notes, demo script, and viva seeds. The last line of this file is the student name and must remain the last line of every deliverable where identity is required.

---

## 1. Role & Mission

You are an autonomous research engineer and academic writer acting for an NCI MSc in Cloud Computing student. Your mission is to:

1. **Replicate** the steady-state SQS configuration baseline of Kyrychenko et al. (2025b) at reduced but scientifically honest scale (pilot → scaled runs; free-tier aware).
2. **Extend** that baseline with controlled **failure injection** (consumer kill, unhandled error, datastore reject, datastore timeout) while systematically varying SQS parameters (visibility timeout, `maxReceiveCount` / DLQ redrive, batch size).
3. **Measure** message loss, duplicates, DLQ capture, recovery time, plus throughput and latency for comparability with the baseline.
4. **Analyse** with pre-registered hypothesis tests, effect sizes, CIs, Holm–Bonferroni correction.
5. **Deliver** a research-paper-style report (≤20 pages, NCI structure), configuration manual, artefact repo, plots, weekly progress notes, demo script, and viva Q&A seeds.

Operate free-tier-aware: prefer LocalStack / dry-run modes for scaffolding; use a real AWS account only for final measurement campaigns; destroy infra after each campaign; log estimated cost before every live run.

**Non-negotiables**
- Python 3.11+ preferred for application and analysis code.
- IaC: **AWS SAM** (Serverless Application Model) — pick SAM and stick to it for Lambda + SQS + DynamoDB + IAM + Event Source Mapping.
- Queue type: **Amazon SQS Standard** + attached **Dead-Letter Queue** (not FIFO for the primary experiment).
- Synthetic order payloads only; no PII; researcher's own AWS account only.
- Reproducibility: seed configs, run manifests, randomised run order, repeated trials.
- Citations: only papers listed in §5 (verified) or additionally verified via DOI/arXiv before use. Never invent authors, years, venues, or DOIs.

---

## 2. Student Identity Block

| Field | Value |
|-------|-------|
| **Name** | Anjaneya Reddy Gurram |
| **Student ID** | 24288853 |
| **Programme** | MSc in Cloud Computing |
| **Institution** | National College of Ireland (NCI) |
| **Module** | Research Project (Cloud Computing: weekly progress 12% + final submission 88%) |
| **Title** | Reliability and Recovery of Amazon SQS Messaging under Injected Consumer and Downstream Failures |

All artefacts, report headers, README, config manuals, and video titles must carry this identity. The final line of this master prompt is the student name alone.

---

## 3. Rubric Mapping (NCI MSc Cloud Computing)

### 3.1 Weighting (Cloud Computing ONLY)

| Assessment | Weight | What Claude must produce |
|------------|--------|---------------------------|
| Weekly progress monitoring | **12%** | Weekly activity report templates + filled sample weeks aligned to 12-week plan |
| Project Final Submission | **88%** | Full portfolio below |

### 3.2 Final portfolio components (map every LO)

From NCI Research Project LOs and handbook:

| Deliverable | Report / artefact location | Rubric / LO alignment |
|-------------|----------------------------|------------------------|
| Research paper-style report (≤20 pages) | `report/` using NCI Word/LaTeX template | LO1–LO5; Abstract → References |
| Required report sections | Abstract; Introduction; Literature Survey; Research Methodology; Design and Implementation Specifications; Evaluation; Conclusions and Discussion; References | Handbook mandatory structure |
| ICT artefact | `artefact/` runnable SAM app + harness | LO3 artefact/product development |
| Configuration manual (separate; not in 20-page limit) | `docs/CONFIGURATION_MANUAL.md` | Document presentation / config manual |
| Presentation video outline (10 min) | `docs/DEMO_AND_PRESENTATION.md` | Oral presentation |
| Demo video outline (5–10 min) | same | Artefact demo |
| Viva Q&A seeds + examiner answers draft | `docs/VIVA_QA.md` | Viva readiness |
| Weekly reports | `weekly/` | 12% weekly monitoring |
| Ethics statement | Secondary AWS own-account + synthetic data; Declaration notes | Ethics Scenario 2/3 awareness; own account = authorised target |

### 3.3 Report section guidance (expand; do not paste proposal)

- **Abstract (~150–250 words):** background → gap → method → key results → theory/practice meaning → open issues.
- **Introduction (~1–2 pages):** problem, motivation, RQ, objectives, contribution, limitations, structure.
- **Literature Survey (~3–4 pages):** critical synthesis; **must substantially expand** beyond RiC proposal (penalties for copy-paste).
- **Methodology:** controlled two-arm experiment; IVs/DVs; hypotheses; stats plan; threats.
- **Design & Implementation:** architecture, SAM resources, fault-injection switch, metrics pipeline — no long code dumps.
- **Evaluation:** results answering RQ/objectives; stats; comparison to Kyrychenko baseline; plots/tables.
- **Conclusions:** objectives met/not; validity; future work (FIFO, multi-region, other brokers).
- **References:** verified bibliography; Harvard/IEEE as per NCI template.

### 3.4 Marking emphasis Claude must optimise for

Artefact quality + rigorous evaluation + clear config manual + honest validity discussion + updated literature (not recycled proposal prose).

---

## 4. Research Question, Objectives, Hypotheses

### 4.1 Research Question

> **How does Amazon SQS configuration affect message reliability and recovery under injected consumer and downstream failures?**

### 4.2 Objectives

1. Quantify how **visibility timeout**, **retry limit (`maxReceiveCount`)**, and **DLQ threshold/redrive** affect **message loss** and **duplicate processing** under injected failure.
2. Measure **recovery time to steady state** (interval from failure cessation until queue depth returns to pre-failure level) as a function of the same parameters.
3. Test whether the **reliability implied by steady-state configuration guidance** (Kyrychenko et al., 2025b) **persists once failures occur**.
4. Characterise the **trade-off** between reliability, recovery, and the **latency / invocation cost** incurred.

### 4.3 Independent variables (IVs)

| IV | Levels (initial; refine after pilot) |
|----|--------------------------------------|
| Visibility timeout (s) | 30, 60, 120, 300, 600 (align with baseline range 10–900; keep subset for cost) |
| `maxReceiveCount` (redrive) | 1, 3, 5, 10 |
| Batch size | 1, 10, 25, 50 (baseline tested 10–100; optimum claimed ~50) |
| Load | normal, burst |
| Failure type | none (control); consumer_kill; unhandled_error; datastore_reject; datastore_timeout |
| Architecture arm | sync (control); queue-decoupled (treatment) |

Hold constant: region, account, SQS Standard, payload schema, consumer memory/timeout, DynamoDB table design, generator.

### 4.4 Dependent variables (DVs)

| DV | Definition |
|----|------------|
| Message-loss rate | Produced − (successfully processed unique + DLQ unique) / produced |
| Duplicate-processing rate | Extra successful process events per unique message ID (relative to no-fault floor) |
| DLQ capture rate | Unique messages in DLQ / produced |
| Successful-processing rate | Unique successful business writes / produced |
| Recovery time | Time from fault OFF → ApproximateNumberOfMessagesVisible returns to pre-fault band |
| Throughput | Messages successfully processed / wall time |
| Latency | End-to-end produce→successful-process latency (p50/p95) |
| Cost proxy | Lambda GB-s + SQS requests (CloudWatch / Cost Explorer estimates) |

### 4.5 Hypotheses (non-directional; α = 0.05; Holm–Bonferroni across family)

- **H1₀:** Visibility timeout has no effect on message-loss rate under injected consumer failure. **H1₁:** At least one setting differs.
- **H2₀:** Retry limit (`maxReceiveCount`) has no effect on recovery time. **H2₁:** At least one differs.
- **H3₀:** The throughput-optimal configuration (from no-fault baseline arm mirroring Kyrychenko) does not differ from alternatives in loss or recovery under fault. **H3₁:** It differs.

Pre-test normality (Shapiro–Wilk / visual). If OK → one-way ANOVA + η²; else Kruskal–Wallis + ε². Report 95% CIs (bootstrap OK for non-normal). Fix repetition count from pilot for MDE of practical interest before main collection.

### 4.6 Confounds & threats (must document)

- SQS Standard = at-least-once → non-zero duplicate floor; use no-fault control.
- Provider temporal drift (Eismann et al., 2022) → randomise run order; same-day blocks where possible; repeats.
- Synthetic faults ≠ organic timing → inject at multiple path points.
- External validity: one account, one region, Standard queue only.
- Construct: recovery = backlog clearance, not full consumer state repair.

---

## 5. Literature Review Brief + Verified Bibliography

### 5.1 Baseline designation (VERIFIED)

**Operational baseline to replicate first, then extend with failure injection:**

> Kyrychenko, O.O., Ostapov, S.E. and Kyrychenko, O.L. (2025) 'Optimization of SQS configurations for efficient batch data processing', *WSEAS Transactions on Systems*, 24, pp. 36–43. https://doi.org/10.37394/23202.2025.24.4

**Verified facts (do not invent beyond this):** SQS-backed serverless batch pipeline; classical **M/M/1** and **M/M/k** modelling; experimental validation processing **500,000** records; varied batch size (10–100), visibility timeout (10–900 s), delivery delay (0–900 s); reported optimum around **batch size 50**, **visibility timeout 600 s**, **delivery delay 300 s**; emphasises throughput/latency/cost under **steady-state healthy consumers**; reliability asserted via service guarantees rather than measured under failure. PDF: https://wseas.com/journals/systems/2025/a085102-004(2025).pdf

**Companion paper (scaling, not failure):** Kyrychenko, Ostapov & Kyrychenko (2025a), EEJET, https://doi.org/10.15587/1729-4061.2025.335723 — predictive scaling / cold starts; **not** the primary baseline.

**Proposal naming note:** The proposal cites "Kyrychenko et al. (2025b)" for the WSEAS SQS configuration paper. That paper **exists and is verified** at the DOI above. Use **(2025)** or **(2025b)** consistently with the bibliography labelling below.

### 5.2 Literature synthesis (themes & gap) — expand this prose in the report

**Theme A — Queue / serverless configuration under load.** Kyrychenko et al. (2025, baseline) and Kyrychenko et al. (2025a) optimise SQS-centric serverless pipelines for throughput and elastic responsiveness using analytical queues and large load tests. Chy et al. (2023) comparatively evaluate JVM brokers (Kafka, Artemis, Pulsar, RocketMQ), showing broker choice and workload shape dominate latency/throughput — reinforcing that messaging configuration is first-order, yet rarely studied for **managed SQS reliability under fault**. Copik et al. (2021) and Schmid et al. (2025) provide FaaS/workflow benchmarking methodology transferable to measurement harness design. Liu & Niu (2024) and Eismann et al. (2022 TSE) frame cost and application-shape context for serverless experiment design.

**Theme B — Event-driven architecture performance & resilience (architecture-level).** Cabane & Farias (2024) show EDA vs monolith performance differences under normal operation. Bosilia, Weinberger & Haindl (2025) compare monolithic vs microservice/async designs for resilience and robustness under failure, establishing that async communication changes resilience — but **hold queue settings fixed**, so outcomes are attributed to architecture, not visibility timeout / retry / DLQ.

**Theme C — Chaos engineering & resilience profiling (system-level metrics).** Al-Said Ahmad et al. (2024) inject delays into serverless and containerised AWS apps under varying load; defects appear abruptly at delay thresholds — but metrics are throughput/latency/availability, not message loss/duplicates/DLQ. Yang et al. (2024) MicroRes indexes resilience via degradation dissemination across microservices. Chen et al. (2024) MicroFI enables prioritised request-level fault injection. Adapa & Singi Reddy (2025) discuss chaos effectiveness gaps in event-driven systems. None treat SQS visibility/`maxReceiveCount`/DLQ as primary IVs with message-level DVs.

**Theme D — Retries, timeouts, fault tolerance semantics.** Sedghpour et al. (2023) and Hanada & Ishibashi (2024, 2025) show retry/timeout policies strongly affect failure rate vs latency. Aderaldo & Mendonça (2023) experimentally quantify retry-pattern performance impact. Halfmoon (Qi, Liu & Jin, 2023), Boki (Jia & Witchel, 2024), and Styx (Psarakis et al., 2025) address exactly-once / transactional stateful serverless — highlighting that **managed SQS remains at-least-once**, so application-level idempotency and DLQ policy are the practical reliability controls this project measures.

**Theme E — Measurement stability.** Eismann et al. (2022 JSS) show serverless performance tests can be same-day stable but suffer short- and long-term drift — mandating randomised order, repeats, and cautious cross-day comparison in this study.

**Gap (niche):** Steady-state SQS configuration work varies the right parameters under the wrong conditions (no consumer/downstream failure). Resilience/chaos work varies failure under the right conditions but not SQS configuration as IV, and not message-level reliability DVs. **This project holds async architecture constant, varies SQS configuration under injected failures, and measures loss, duplicates, DLQ capture, and recovery — retaining throughput/latency for baseline comparability.**

### 5.3 Citation verification status for proposal references

| Proposal cite | Status |
|---------------|--------|
| Kyrychenko et al. (2025b) WSEAS SQS optimisation | **VERIFIED** — DOI 10.37394/23202.2025.24.4 — **BASELINE** |
| Kyrychenko et al. (2025a) EEJET serverless queues | **VERIFIED** — DOI 10.15587/1729-4061.2025.335723 |
| Al-Said Ahmad et al. (2024) Computing | **VERIFIED** — DOI 10.1007/s00607-024-01292-z |
| Bosilia et al. (2026) ECSA LNCS | **VERIFIED** — DOI 10.1007/978-3-032-04403-7_16 (ECSA 2025 tracks; imprint 2025/2026) |
| Cabane & Farias (2024) FGCS | **VERIFIED** — DOI 10.1016/j.future.2023.10.021 |
| Eismann et al. (2022) JSS | **VERIFIED** — DOI 10.1016/j.jss.2022.111294 |
| Yang et al. (2024) ISSTA MicroRes | **VERIFIED** — DOI 10.1145/3650212.3652131 |

**Unverifiable proposal citations replaced:** None of the seven proposal references failed verification. Additional papers below were added to reach ≥20 reputable sources (2021–2026, majority 2022–2026) for a substantial literature survey.

### 5.4 Numbered verified bibliography (≥20)

Mark **[BASELINE]** on the paper to replicate first.

1. **[BASELINE]** Kyrychenko, O.O., Ostapov, S.E. and Kyrychenko, O.L. (2025) 'Optimization of SQS configurations for efficient batch data processing', *WSEAS Transactions on Systems*, 24, pp. 36–43. https://doi.org/10.37394/23202.2025.24.4
2. Kyrychenko, O., Ostapov, S. and Kyrychenko, O. (2025) 'Design of a framework for serverless distributed data processing using queues', *Eastern-European Journal of Enterprise Technologies*, 4(9(136)), pp. 19–25. https://doi.org/10.15587/1729-4061.2025.335723
3. Al-Said Ahmad, A., Al-Qora'n, L.F. and Zayed, A. (2024) 'Exploring the impact of chaos engineering with various user loads on cloud native applications: an exploratory empirical study', *Computing*, 106(7), pp. 2389–2425. https://doi.org/10.1007/s00607-024-01292-z
4. Bosilia, N., Weinberger, G. and Haindl, P. (2025) 'Assessing the impact of asynchronous communication on resilience and robustness: a comparative study of microservice and monolithic architectures', in *Software Architecture. ECSA 2025 Tracks and Workshops*, LNCS 15982. Cham: Springer, pp. 171–186. https://doi.org/10.1007/978-3-032-04403-7_16
5. Cabane, H. and Farias, K. (2024) 'On the impact of event-driven architecture on performance: An exploratory study', *Future Generation Computer Systems*, 153, pp. 52–69. https://doi.org/10.1016/j.future.2023.10.021
6. Eismann, S., Costa, D.E., Liao, L., Bezemer, C.-P., Shang, W., van Hoorn, A. and Kounev, S. (2022) 'A case study on the stability of performance tests for serverless applications', *Journal of Systems and Software*, 189, 111294. https://doi.org/10.1016/j.jss.2022.111294
7. Yang, T., Lee, C., Shen, J., Su, Y., Feng, C., Yang, Y. and Lyu, M.R. (2024) 'MicroRes: versatile resilience profiling in microservices via degradation dissemination indexing', in *Proceedings of the 33rd ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2024)*. New York: ACM, pp. 325–337. https://doi.org/10.1145/3650212.3652131
8. Eismann, S., Scheuner, J., van Eyk, E., Schwinger, M., Grohmann, J., Herbst, N., Abad, C.L. and Iosup, A. (2022) 'The state of serverless applications: collection, characterization, and community consensus', *IEEE Transactions on Software Engineering*, 48(10), pp. 4152–4166. https://doi.org/10.1109/TSE.2021.3113940
9. Liu, F. and Niu, Y. (2024) 'Demystifying the cost of serverless computing: towards a win-win deal', *IEEE Transactions on Parallel and Distributed Systems*, 35(1), pp. 59–72. https://doi.org/10.1109/TPDS.2023.3330849
10. Chy, M.S.H., Arju, M.A.R., Tella, S.M. and Cerny, T. (2023) 'Comparative evaluation of Java Virtual Machine-based message queue services: a study on Kafka, Artemis, Pulsar, and RocketMQ', *Electronics*, 12(23), 4792. https://doi.org/10.3390/electronics12234792
11. Chen, H., Chen, P., Yu, G., Li, X. and He, Z. (2024) 'MicroFI: non-intrusive and prioritized request-level fault injection for microservice applications', *IEEE Transactions on Dependable and Secure Computing*, 21(5), pp. 4921–4938. https://doi.org/10.1109/TDSC.2024.3363902
12. Qi, S., Liu, X. and Jin, X. (2023) 'Halfmoon: log-optimal fault-tolerant stateful serverless computing', in *Proceedings of the 29th Symposium on Operating Systems Principles (SOSP '23)*. New York: ACM. https://doi.org/10.1145/3600006.3613154
13. Jia, Z. and Witchel, E. (2024) 'Boki: towards data consistency and fault tolerance with shared logs in stateful serverless computing', *ACM Transactions on Computer Systems*. https://doi.org/10.1145/3653072
14. Psarakis, K., Christodoulou, G., Siachamis, G., Fragkoulis, M. and Katsifodimos, A. (2025) 'Styx: transactional stateful functions on streaming dataflows', *Proceedings of the ACM on Management of Data*. https://doi.org/10.1145/3725363
15. Sedghpour, M.R.S., Garlan, D., Schmerl, B., Klein, C. and Tordsson, J. (2023) 'Breaking the vicious circle: self-adaptive microservice circuit breaking and retry', in *2023 IEEE International Conference on Cloud Engineering (IC2E)*, pp. 32–42. https://doi.org/10.1109/IC2E59103.2023.00012
16. Hanada, H. and Ishibashi, K. (2024) 'Empirical study on request timeout and retry for microservices communication', in *2024 IEEE 29th Pacific Rim International Symposium on Dependable Computing (PRDC)*. https://doi.org/10.1109/PRDC63035.2024.00037
17. Hanada, H. and Ishibashi, K. (2025) 'Service-level objective-aware load-adaptive timeout: balancing failure rate and latency in microservices communication', *IEEE Access*, 13, pp. 137881–137895. https://doi.org/10.1109/ACCESS.2025.3596118
18. Aderaldo, C.M. and Mendonça, N.C. (2023) 'How the retry pattern impacts application performance: a controlled experiment', in *Proceedings of the XXXVII Brazilian Symposium on Software Engineering (SBES '23)*. New York: ACM. https://doi.org/10.1145/3613372.3613409
19. Adapa, M. and Singi Reddy, N.R. (2025) 'Quantifying chaos engineering effectiveness in event-driven microservices', *Journal of International Crisis and Risk Communication Research*. https://doi.org/10.63278/jicrcr.vi.3334
20. Schmid, L., Copik, M., Calotoiu, A., Brandner, L., Koziolek, A. and Hoefler, T. (2025) 'SeBS-Flow: benchmarking serverless cloud function workflows', in *Proceedings of the Twentieth European Conference on Computer Systems (EuroSys '25)*, pp. 902–920. https://doi.org/10.1145/3689031.3717465
21. Copik, M., Kwaśniewski, G., Besta, M., Podstawski, M. and Hoefler, T. (2021) 'SeBS: a serverless benchmark suite for Function-as-a-Service computing', in *Proceedings of the 22nd International Middleware Conference*. New York: ACM. https://doi.org/10.1145/3464298.3476133
22. Wen, J., Chen, Z., Liu, Y., Lou, Y., Ma, Y., Huang, G., Jin, X. and Liu, X. (2021) 'An empirical study on challenges of application development in serverless computing', in *Proceedings of the 29th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering (ESEC/FSE 2021)*, pp. 416–428. https://doi.org/10.1145/3468264.3468558
23. Wen, J., Liu, Y., Chen, Z., Chen, J. and Ma, Y. (2021) 'Characterizing commodity serverless computing platforms', *Journal of Software: Evolution and Process*, 35(10), e2394. https://doi.org/10.1002/smr.2394

**Paper count verified for this master prompt: 23.** Prefer citing [1]–[20] heavily in the ≤20-page report; use [21]–[23] for methodology/context as needed.

---

## 6. Exact Local Implementation Plan

### 6.1 Chosen stack (do not switch mid-project)

| Layer | Choice |
|-------|--------|
| Language | Python 3.11+ |
| IaC | **AWS SAM** (`template.yaml`) |
| Compute | AWS Lambda (queue consumer + sync API consumer) |
| Queue | SQS Standard + SQS DLQ |
| Datastore | DynamoDB (orders table; idempotency via `order_id` conditional put) |
| Metrics | CloudWatch metrics/logs + custom CSV/JSON run logs in S3 or local `results/` |
| Producer | Python CLI / Locust-or-custom load generator invoking API Gateway (sync) or sending to SQS (async) |
| Fault injection | Env-var / SSM Parameter / DynamoDB config flag — **no** AWS Fault Injection Simulator required (cost/complexity); inject in-process |
| Local dry-run | SAM local + optional LocalStack; `DRY_RUN=1` skips paid APIs where possible |
| Analysis | pandas, scipy, matplotlib/seaborn; optional statsmodels |

### 6.2 Repo layout (create exactly under project root)

```text
sqs-reliability-recovery/          # or thesis artefact root
├── README.md
├── template.yaml                  # SAM: queues, DLQ, Lambdas, DDB, IAM, ESM
├── samconfig.toml
├── requirements.txt
├── pyproject.toml                 # optional
├── .env.example
├── Makefile                       # deploy, destroy, pilot, analyse shortcuts
├── src/
│   ├── producer/
│   │   ├── generate_orders.py     # synthetic orders
│   │   └── loadgen.py             # normal/burst senders
│   ├── sync_api/
│   │   └── app.py                 # API Gateway → process order synchronously
│   ├── queue_consumer/
│   │   └── handler.py             # SQS event source Lambda
│   ├── common/
│   │   ├── models.py
│   │   ├── dynamo.py
│   │   ├── idempotency.py
│   │   ├── faults.py              # FAULT_MODE switch
│   │   └── metrics.py
│   └── control/
│       ├── experiment_runner.py   # config matrix, randomisation, repeats
│       ├── fault_controller.py    # enable/disable faults mid-run
│       └── collect_metrics.py
├── configs/
│   ├── baseline_kyrchenko.yaml    # VT/batch/delay levels inspired by baseline
│   ├── fault_campaigns.yaml
│   └── pilot.yaml
├── scripts/
│   ├── scaffold.sh
│   ├── deploy.sh
│   ├── destroy.sh
│   ├── run_pilot.sh
│   ├── run_baseline.sh
│   ├── run_fault_campaign.sh
│   ├── estimate_cost.py
│   └── assert_free_tier_guard.py
├── analysis/
│   ├── stats_tests.py
│   ├── plot_results.py
│   └── notebooks/                 # optional exploratory; final plots via scripts
├── results/                       # gitignore raw; keep manifests + summaries
│   ├── manifests/
│   └── figures/
├── docs/
│   ├── CONFIGURATION_MANUAL.md
│   ├── DEMO_AND_PRESENTATION.md
│   └── VIVA_QA.md
├── report/                        # NCI template content
├── weekly/
└── tests/
    ├── unit/
    └── integration/
```

### 6.3 AWS services & SAM resources (minimal)

- `AWS::SQS::Queue` main + `RedrivePolicy` → DLQ; `VisibilityTimeout`, `ReceiveMessageWaitTimeSeconds` (short/long poll as fixed factor).
- `AWS::SQS::Queue` DLQ.
- `AWS::Serverless::Function` `QueueConsumer` with `SQS` event source: `BatchSize`, `FunctionResponseTypes: [ReportBatchItemFailures]`.
- `AWS::Serverless::Function` `SyncProcessor` + `AWS::Serverless::Api` (or Function URL) for sync arm.
- `AWS::DynamoDB::Table` `Orders` (PK `order_id`); optional `ProcessedInbox` for idempotency evidence.
- IAM least privilege; no wildcard `*` on `*` in production template.
- CloudWatch log groups with short retention (7–14 days) to limit cost.

### 6.4 Environment variables / parameters

```text
AWS_REGION=eu-west-1          # or student choice; keep constant
STAGE=dev|pilot|exp
DRY_RUN=0|1
FAULT_MODE=none|consumer_kill|unhandled_error|datastore_reject|datastore_timeout
FAULT_RATE=0.0-1.0            # probabilistic injection
FAULT_WINDOW_SEC=60
VISIBILITY_TIMEOUT=30
MAX_RECEIVE_COUNT=5
BATCH_SIZE=10
ORDER_COUNT=1000              # pilot small; scale toward baseline comparability
LOAD_PROFILE=normal|burst
RUN_ID=uuid
ENABLE_COST_GUARD=1
MAX_ESTIMATED_USD=5.00
```

### 6.5 Fault injection semantics (`src/common/faults.py`)

| Mode | Behaviour |
|------|-----------|
| `none` | Happy path; establish duplicate floor |
| `consumer_kill` | `os._exit(1)` / raise unrecoverable after receive, **before** delete — simulates crash mid-processing |
| `unhandled_error` | Raise exception after partial work → Lambda failure → SQS retry |
| `datastore_reject` | DynamoDB `ConditionalCheckFailed` or forced `ProvisionedThroughputExceeded` simulation / explicit reject path |
| `datastore_timeout` | Sleep > remaining Lambda time or mock client timeout before write |

Always record: messageId, order_id, receive_count, fault_mode, timestamps.

### 6.6 Free-tier / cost awareness

- Before live deploy: `python scripts/estimate_cost.py --orders N --repeats R`.
- Guard: abort if estimate > `MAX_ESTIMATED_USD`.
- Prefer: short experiments, small memory (128–256 MB), destroy stacks after campaigns (`sam delete`).
- Use pilot N≪500k; for baseline comparability report **rates** and **normalised throughput**, and optionally one larger run if budget allows — **do not** burn money to vanity-match 500k if it risks account spend.
- Enable billing alarms in account (document in config manual).

### 6.7 Idempotency (required for interpreting duplicates)

Use conditional `PutItem` on `order_id`. Count:
- `business_success_first`
- `business_success_duplicate_attempt` (idempotent no-op)
- This separates **transport duplicates** from **unsafe double-apply**.

---

## 7. Step-by-Step Commands Claude Must Run

Execute in order. Adapt paths to the artefact root. Prefer Linux/macOS bash.

### Phase 0 — Scaffold

```bash
mkdir -p sqs-reliability-recovery && cd sqs-reliability-recovery
# create tree per §6.2
python3 -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install boto3 aws-sam-cli pytest pandas scipy matplotlib seaborn pyyaml python-dotenv statsmodels
# write template.yaml, src/*, configs/*, scripts/*
cp .env.example .env
# DRY_RUN=1 first
```

### Phase 1 — Unit tests & local dry-run

```bash
pytest -q tests/unit
sam validate --lint
sam build
# optional: sam local invoke QueueConsumer -e events/sqs_event.json
DRY_RUN=1 python -m src.control.experiment_runner --config configs/pilot.yaml
```

### Phase 2 — Deploy pilot stack (live, small)

```bash
python scripts/assert_free_tier_guard.py
python scripts/estimate_cost.py --config configs/pilot.yaml
sam deploy --guided   # once; thereafter samconfig.toml
# record stack outputs: queue URL, DLQ URL, API URL, table name
```

### Phase 3 — Baseline replication (no fault) — **replicate Kyrychenko first**

```bash
python -m src.control.experiment_runner \
  --config configs/baseline_kyrchenko.yaml \
  --fault none \
  --randomise-order \
  --repeats 5 \
  --out results/baseline/
python analysis/plot_results.py --in results/baseline --out results/figures/baseline
python analysis/stats_tests.py --in results/baseline --hypotheses H0_throughput_config
```

Goals: identify throughput-favouring (VT, batch) combo on **this** account/region; record duplicate floor.

### Phase 4 — Sync vs queue arms (matched load, no fault)

```bash
python -m src.control.experiment_runner --arm sync --load normal --fault none --repeats 5
python -m src.control.experiment_runner --arm queue --load normal --fault none --repeats 5
```

### Phase 5 — Fault campaigns (vary one primary IV per campaign; full factorial only if budget allows)

```bash
# Campaign A: visibility timeout × consumer_kill
python scripts/run_fault_campaign.sh --fault consumer_kill --vary visibility_timeout
# Campaign B: maxReceiveCount × unhandled_error
python scripts/run_fault_campaign.sh --fault unhandled_error --vary max_receive_count
# Campaign C: DLQ/redrive × datastore_reject
python scripts/run_fault_campaign.sh --fault datastore_reject --vary max_receive_count
# Campaign D: datastore_timeout × visibility timeout
python scripts/run_fault_campaign.sh --fault datastore_timeout --vary visibility_timeout
# Burst replication of key cells
python scripts/run_fault_campaign.sh --load burst --subset key_cells.yaml
```

Each run must: warm-up → steady → inject fault window → cease fault → measure recovery → drain → export metrics → tag `RUN_ID`.

### Phase 6 — Analysis

```bash
python analysis/stats_tests.py --in results/ --hypotheses H1,H2,H3 --alpha 0.05 --holm
python analysis/plot_results.py --in results/ --out results/figures/
# Produce: loss vs VT; recovery vs maxReceiveCount; DLQ rate heatmaps; throughput/latency comparability charts
```

### Phase 7 — Teardown & docs

```bash
sam delete --stack-name <name> --no-prompts
# Write CONFIGURATION_MANUAL, report sections, weekly notes, viva seeds
```

### Phase 8 — Quality gate commands

```bash
pytest -q
sam validate --lint
test -f docs/CONFIGURATION_MANUAL.md
test -f results/figures/loss_vs_visibility.png
python analysis/stats_tests.py --self-check
```

---

## 8. Deliverables Checklist

### 8.1 Research paper report sections (≤20 pages)

- [ ] Abstract (structured: background, objectives, methodology, results, findings)
- [ ] Introduction (RQ, objectives, contribution, limitations, outline)
- [ ] Literature Survey (**expanded**, critical, uses ≥15 in-text cites from §5.4)
- [ ] Research Methodology (design, resources, evaluation, ethics, threats)
- [ ] Design and Implementation Specifications (architecture diagrams, SAM overview, fault model — no code dumps)
- [ ] Evaluation (tables/figures, hypothesis outcomes, comparison to baseline [1], trade-offs)
- [ ] Conclusions and Discussion (objectives, future work, generalisability)
- [ ] References (verified only)

### 8.2 Configuration manual (separate)

Must include: prerequisites (AWS CLI, SAM, Python), account setup, IAM notes, billing alarm, `.env` explanation, deploy/destroy, how to run pilot/baseline/fault campaigns, how to interpret CSVs, troubleshooting (visibility too low → duplicates; too high → slow recovery), cost controls.

### 8.3 Weekly report template notes (`weekly/WEEK_NN.md`)

```text
Week: N | Dates: | Student: Anjaneya Reddy Gurram 24288853
Goals this week:
Work completed:
Artefact commits / experiment IDs:
Results / blockers:
Next week plan:
Supervisor questions:
Hours:
```

Map weeks 1–12 to: rig → baseline → fault campaigns → burst → analysis → write-up → buffer (per proposal plan).

### 8.4 Demo script outline (5–10 min)

1. Show architecture diagram (sync vs queue+DLQ).
2. Deployed resources in console (or recorded).
3. Produce 100 orders, show DynamoDB writes.
4. Enable `FAULT_MODE=unhandled_error`, show retries + DLQ.
5. Change `maxReceiveCount`, contrast DLQ capture.
6. Show recovery-time plot from last campaign.
7. Point to config manual & reproducibility manifest.

### 8.5 Presentation outline (10 min)

Problem → gap vs Kyrychenko baseline → method → key results (3 figures) → implications for practitioners → limitations → Q&A tease.

### 8.6 Viva Q&A seeds (draft answers in `docs/VIVA_QA.md`)

- Why Standard not FIFO?
- How do you define message loss on an at-least-once queue?
- Why is reliability not implied by throughput?
- How did you control for provider performance drift?
- Ethics: why is own-account load acceptable?
- Would results transfer to Kafka/RabbitMQ?
- What is the practical recommendation for visibility timeout under failure?
- How is recovery time operationalised?
- Why SAM not Terraform?
- What would you change with a larger budget?

---

## 9. Quality Gates

### 9.1 Reproducibility

- Every experiment writes `results/manifests/<RUN_ID>.json` with git commit, config hash, region, AMI/runtime, start/end, fault schedule, random seed.
- Analysis scripts read manifests only (no hand-edited CSVs as source of truth).
- README: one-command pilot.

### 9.2 Ethics

- Synthetic orders only; no human participants; no third-party personal data.
- Target system = **student's own AWS account** (authorised). Stay within AUP; modest load; no cross-tenant impact.
- Acknowledge energy/cost footprint; minimise repeats via pilot-powered sample size.
- If undocumented provider behaviour appears, document and notify provider before public release.
- Complete NCI Declaration of Ethics Consideration as required (Scenario: own cloud target + synthetic data).

### 9.3 Academic integrity

- **Do not plagiarise the proposal.** Literature, methodology, and discussion must be substantially rewritten and expanded with new implementation detail and results.
- No fabricated citations, data, or significance stars.
- Report negative and anomalous runs.

### 9.4 Engineering gates

- `sam validate --lint` clean.
- Unit tests for fault modes and idempotency.
- `ReportBatchItemFailures` enabled.
- DLQ always configured in treatment arm.
- Cost guard enforced for live runs.
- Stack destroyed after campaigns unless supervisor demo needs persistence.

### 9.5 Statistical gates

- Analysis plan fixed before main collection (record in `configs/analysis_plan.yaml`).
- Holm–Bonferroni across hypothesis family.
- Effect size + CI required for any "significant" claim.
- Duplicate rates reported **relative to no-fault floor**.

### 9.6 Definition of Done

Project is done when: (1) baseline no-fault configuration study completed and documented against Kyrychenko et al. (2025) [1]; (2) ≥3 fault types executed across VT and `maxReceiveCount` grids with repeats; (3) H1–H3 tested and reported; (4) report + config manual + figures + weekly templates + demo/viva docs exist; (5) infra teardown verified; (6) student name on final line of identity-bearing docs.

---

## 10. Execution Priority Reminder for Claude

1. Scaffold repo + SAM template + fault harness.  
2. Pilot on AWS (tiny N).  
3. **Replicate baseline** (no fault; VT × batch).  
4. Run fault-injection extension campaigns.  
5. Analyse + plot.  
6. Write expanded report + config manual + viva/demo/weekly artefacts.  
7. Tear down; final README for examiners.

**Baseline citation string (use in report):**  
Kyrychenko, O.O., Ostapov, S.E. and Kyrychenko, O.L. (2025) 'Optimization of SQS configurations for efficient batch data processing', *WSEAS Transactions on Systems*, 24, pp. 36–43. https://doi.org/10.37394/23202.2025.24.4

---

Anjaneya Reddy Gurram
