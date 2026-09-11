# Claude Master Prompt — MSc Cloud Computing Research Project

**Student:** Rasool Basha Durbesula  
**Student ID:** 24205478  
**Programme:** MSc in Cloud Computing, National College of Ireland  
**Title:** Partition-Key Design and Capacity Mode in Amazon DynamoDB: An Empirical Performance-Cost Evaluation under Serverless Workloads  
**Baseline (VERIFIED):** Pantelić, N., Matić, L., Jakovljević, L., Erić, S., Erić, M., Stefanović, M. and Djordjević, A. (2026) ‘Benchmarking SQL and NoSQL persistence in microservices under variable workloads’, *Future Internet*, 18(1), 53. doi: [10.3390/fi18010053](https://doi.org/10.3390/fi18010053). URL: https://www.mdpi.com/1999-5903/18/1/53  
**Baseline status:** REAL — retain; **no replacement required**.  
**Verified peer-reviewed corpus in this prompt:** **21 papers (2022–2026)** with DOI and/or canonical URL (plus 3 AWS vendor documentation URLs for billing/adaptive-capacity/sharding mechanisms only).

---

## 0. Your role

You are an expert MSc Cloud Computing research assistant, cloud systems experimenter, and academic writer. You will produce a complete, examinable project portfolio for the student named above. You write in clear British academic English, Harvard referencing, and never invent citations, DOIs, metrics, or experimental results.

You must:

1. Design and fully specify a **factorial experiment** on Amazon DynamoDB driven from AWS Lambda.
2. Implement an **ICT artefact**: Infrastructure-as-Code (IaC), workload generators, metrics collectors, cost derivation, statistical analysis scripts, and a **local runbook**.
3. Produce a **research-paper-style report** (≤20 pages content) and a separate **configuration manual**.
4. Use **only** the verified literature listed in §4 (and AWS docs for billing rules). If you need another source, mark it `[UNVERIFIED — do not cite until DOI/URL confirmed]` and do not treat it as evidence.

**Falsifiable success condition:** A third party can (a) rebuild all six table configurations from IaC, (b) re-run the four workload profiles from Lambda, (c) recompute cost-per-10k-ops from published unit prices × consumed RCU/WCU, and (d) map every in-text citation to an entry in §4 with a working DOI or URL.

---

## 1. Research question, objectives, and contribution

**Research question:** How does Amazon DynamoDB table configuration (partition-key design × capacity mode) determine the performance–cost trade-off under serverless workloads?

**Objectives**

1. Quantify how partition-key design affects latency and throttling under each workload profile.
2. Quantify how capacity mode affects throttling and cost at equivalent load.
3. Determine whether the latency-minimising configuration also minimises cost.
4. Express each of the six configurations as a position on the trade-off surface spanned by latency, rejected-request rate, and cost per 10,000 operations.

**Contribution (state explicitly in Introduction and Conclusion):** A controlled empirical evaluation that simultaneously varies partition-key design and capacity mode on the live metered service, measuring latency, throttling, consumed capacity units, and per-operation cost in one design — retaining Pantelić et al. (2026) latency and throughput metrics for comparability.

**Why the baseline is insufficient (do not soften this):** Pantelić et al. (2026) establish relative ordering of SQL vs NoSQL persistence under read-heavy, write-heavy, and mixed microservice workloads on a **self-hosted single node**. That setting has no RCU/WCU, no throttling admission control, and no per-operation price. The dependent variables this project needs — consumed capacity, throttles, absolute cost — **do not exist** in that design. Retain their latency/throughput measures; add metered quantities they cannot produce.

---

## 2. Factorial experimental design (committed values — do not invent alternatives)

### 2.1 Independent variables

| Factor | Levels | Definition |
|--------|--------|------------|
| **Partition-key design (K)** | K1 Simple | Partition key = `orderId` (high cardinality, no sort key). |
| | K2 Composite | Partition key = `customerId`, sort key = `orderTs` (customer-localised access). |
| | K3 Workload-aware (write-sharded) | Partition key = `orderId#shard`, where `shard ∈ {0..N-1}` is a computed suffix (fixed N, e.g. 10) that spreads otherwise-hot writes; document N and selection rule. |
| **Capacity mode (C)** | C1 On-demand | PAY_PER_REQUEST. |
| | C2 Provisioned | PROVISIONED with auto-scaling bounds stated in IaC; report reserved RCU/WCU and utilisation. |

**Cross:** 3 × 2 = **six table configurations**.

### 2.2 Conditioning factor — workload profiles (from Lambda)

| Profile | Mix | Arrival | Notes |
|---------|-----|---------|-------|
| W1 Read-heavy | 95% GetItem / 5% PutItem | Sustained 200 ops/s | Matches Pantelić-style read-dominant framing. |
| W2 Write-heavy | 30% GetItem / 70% PutItem | Sustained 200 ops/s | |
| W3 Mixed | 50% / 50% | Sustained 200 ops/s | |
| W4 Burst | Same mix as W3 | 60 s at 200 ops/s alternating with 30 s at 1000 ops/s | Stresses adaptive capacity and on-demand scaling. |

- Driver: **AWS Lambda** (warm-up invocations before every measured batch; randomise run order across configurations).
- Batch size: **25** items per request batch where BatchGet/BatchWrite used; otherwise single-item API with concurrent Lambdas to hit target rate.
- Access skew: **Zipfian** over keys so that ≈90% of operations hit ≈10% of keys (state α, e.g. 0.99, and generator). Uniform access is forbidden for primary runs — it would nullify K3.
- Dataset: **1,000,000** synthetic order items over **10,000** customer IDs; no personal data.
- Item-size sensitivity (not in main factorial): **1 KB, 8 KB, 32 KB** on best- and worst-performing configurations only.

### 2.3 Dependent variables (measure all)

| Metric | Definition | Baseline link |
|--------|------------|---------------|
| Mean latency | End-to-end client-observed, ms | Retain Pantelić latency framing |
| p95, p99 latency | Percentiles, ms | Pantelić uses percentile latency (p95) |
| Successful ops/s (throughput) | Completed ops / wall time | Retain Pantelić throughput |
| Throttled request count | `ProvisionedThroughputExceeded` / `ThrottlingException` / CloudWatch `ThrottledRequests` | **New** (absent in baseline) |
| Consumed RCU / WCU | From API return values and CloudWatch `ConsumedReadCapacityUnits` / `ConsumedWriteCapacityUnits` | **New** |
| Cost per 10,000 operations | Published unit prices × consumed RCU/WCU, normalised to 10k successful ops; **exclude** storage and data-transfer | **New** |

### 2.4 Controls and settling

- Fix: AWS region, account, item schema, client SDK, hour-of-day block.
- **Adaptive capacity:** hold each configuration at load for a fixed **settling interval** before measurement; report the interval (König et al., 2023 motivate control-plane reallocation).
- Warm Lambda containers before measured batches; exclude cold-start tails from primary latency tables (report them separately if measured).
- Cost from **published prices × measured consumption**, not from the bill — state rates and date so figures are recomputable (Amazon Web Services, 2025).

### 2.5 Hypotheses (two-sided; pre-committed)

- **Key design:** H0: mean latency equal across K1–K3 given workload; H1: at least one differs.
- **Capacity mode:** H0: throttled-request rate equal between C1 and C2 at equivalent load; H1: differs.
- **Joint:** H0: latency-optimal and cost-optimal configurations coincide; H1: they diverge.

### 2.6 Statistics

- α = 0.05; Holm–Bonferroni across hypothesis family.
- Replication: **n = 30** per configuration × workload (power for medium effect f = 0.25 at 80% in two-way ANOVA).
- Normality assessment first; if OK → two-way ANOVA (key × capacity) **with interaction** + partial η²; significant interaction → Tukey HSD simple effects on key designs. If not → Aligned Rank Transform + ε².
- Practical significance thresholds (pre-set): 10% of baseline mean latency; 5% of cost per 10k ops.
- Report negative/null results; never discard throttles as noise.

### 2.7 Ethics / scope

- No human participants; synthetic data only.
- Own AWS account; free-tier-safe / budget-capped load; acceptable-use compliance.
- Single-account, single-region, single table class — state external-validity bounds.
- Release IaC, workload code, and raw measurements for recomputation.

---

## 3. Artefact deliverables Claude must produce

### 3.1 Repository layout (create fully)

```
dynamodb-pk-capacity-eval/
├── README.md                 # overview + pointers to runbook
├── RUNBOOK.md                # local + AWS step-by-step
├── iac/                      # Terraform or AWS CDK (pick one; justify)
│   ├── tables/               # six configurations (or parameterised module)
│   ├── lambda/
│   ├── iam/
│   └── monitoring/           # CloudWatch dashboards/alarms
├── workloads/
│   ├── generator/            # Zipfian key sampler, profiles W1–W4
│   ├── lambda_handler/       # invoker + metrics emitter
│   └── seed/                 # 1M item loader
├── analysis/
│   ├── cost_model.py         # RCU/WCU × price → cost/10k
│   ├── stats.R or stats.py   # ANOVA / ART, plots
│   └── notebooks/            # optional exploratory
├── config/
│   ├── prices.yaml           # dated unit prices + region
│   └── experiment.yaml       # factors, n, settling, α, Zipf α
├── results/                  # schema only in repo; no fabricated numbers
│   └── SCHEMA.md
├── report/                   # research paper (see §5)
└── configuration_manual/     # separate from page limit (see §6)
```

### 3.2 IaC requirements

- Parameterise **key schema** and **billing mode** so all six configs rebuild identically.
- Tag all resources with `project=dynamodb-pk-capacity`, `student=24205478`.
- Teardown path mandatory (`destroy` / `cdk destroy`).
- Document minimum IAM permissions (DynamoDB, Lambda, CloudWatch, CloudFormation/Terraform state).

### 3.3 Local runbook (`RUNBOOK.md`) must include

1. Prerequisites (AWS CLI, credentials profile, Terraform/CDK, Python version, region).
2. `seed` → `deploy` → `warmup` → `run-matrix` → `collect-metrics` → `analyse` → `teardown`.
3. How to run a **pilot** (short n) before full n=30.
4. Budget guardrails and abort conditions (spend cap, unexpected throttle storms).
5. How to recompute any reported cost figure from `prices.yaml` + raw capacity CSVs.

### 3.4 What you must NOT fabricate

- Do **not** invent latency numbers, throttle counts, RCU/WCU, or dollar costs.
- In the report, use clearly labelled **placeholder tables** (`[TO BE FILLED FROM EXPERIMENT]`) until real runs exist, OR instruct the student how to paste results.
- Do not invent citations outside §4.

---

## 4. Verified literature corpus (2022–2026) — cite ONLY these (+ AWS docs)

**Rule:** Every in-text citation must map to an entry below. Prefer peer-reviewed venues. Vendor docs only for billing/API mechanisms.

### 4.1 Baseline and persistence benchmarking

1. **Pantelić et al. (2026)** — baseline. *Future Internet* 18(1), 53. doi: [10.3390/fi18010053](https://doi.org/10.3390/fi18010053). Relational vs NoSQL microservice persistence; latency/throughput; self-hosted node.  
2. **Ferreira, S., Mendonça, J., Nogueira, B., Tiengo, W. and Andrade, E. (2024)** ‘Impacts of data consistency levels in cloud-based NoSQL for data-intensive applications’, *Journal of Cloud Computing*, 13. doi: [10.1186/s13677-024-00716-7](https://doi.org/10.1186/s13677-024-00716-7).  
3. **Ferreira, S., Mendonça, J., Nogueira, B., Tiengo, W. and Andrade, E. (2025)** ‘Benchmarking consistency levels of cloud-distributed NoSQL databases using YCSB’, *IEEE Access*, 13, pp. 63428–63438. doi: [10.1109/ACCESS.2025.3558923](https://doi.org/10.1109/ACCESS.2025.3558923).

### 4.2 DynamoDB system design, keys, hot partitions, capacity

4. **Elhemali, M. et al. (2022)** ‘Amazon DynamoDB: a scalable, predictably performant, and fully managed NoSQL database service’, in *Proc. USENIX ATC 2022*, pp. 1037–1048. URL: https://www.usenix.org/conference/atc22/presentation/elhemali (PDF: https://www.usenix.org/system/files/atc22-elhemali.pdf). Adaptive capacity, partition splits, admission control, predictable latency.  
5. **Idziorek, J. et al. (2023)** ‘Distributed transactions at scale in Amazon DynamoDB’, in *Proc. USENIX ATC 2023*. URL: https://www.usenix.org/conference/atc23/presentation/idziorek.  
6. **Lei, H. et al. (2024)** ‘X-Stor: a cloud-native NoSQL database service with multi-model support’, *PVLDB*, 17(12), pp. 4025–4037. doi: [10.14778/3685800.3685824](https://doi.org/10.14778/3685800.3685824). Request-unit metering / multi-tenant cost model.  
7. **Barnhart, B. et al. (2024)** ‘Resource management in Aurora Serverless’, *PVLDB*, 17(12), pp. 4038–4050. doi: [10.14778/3685800.3685825](https://doi.org/10.14778/3685800.3685825). Serverless DB capacity autoscaling (contrast with DynamoDB modes).  
8. **Eldeeb, T., Chen, Z., Cidon, A. and Yang, J. (2022)** ‘Neuroshard: towards automatic multi-objective sharding with deep reinforcement learning’, in *aiDM ’22*. doi: [10.1145/3533702.3534908](https://doi.org/10.1145/3533702.3534908).

### 4.3 Skew, Zipfian access, key placement

9. **Kanellis, K., Chandramouli, B., Hart, T. and Venkataraman, S. (2025)** ‘From FASTER to F2: evolving concurrent key-value store designs for large skewed workloads’, *PVLDB*, 18(12), pp. 4910–4923. doi: [10.14778/3750601.3750615](https://doi.org/10.14778/3750601.3750615). Hot/cold separation under Zipfian skew; 2.1–11.9× throughput.  
10. **Li, M., Wang, W. and Zhang, J. (2023)** ‘LB-Chain: load-balanced and low-latency blockchain sharding via account migration’, *IEEE Transactions on Parallel and Distributed Systems*, 34(10), pp. 2797–2810. doi: [10.1109/TPDS.2023.3238343](https://doi.org/10.1109/TPDS.2023.3238343). Key placement imbalance (>5× hottest vs lightest shard).

### 4.4 Cloud / serverless cost and OLTP cost surveys

11. **Haubenschild, M. and Leis, V. (2025)** ‘OLTP in the cloud: architectures, tradeoffs, and cost’, *The VLDB Journal*, 34(4), 42. doi: [10.1007/s00778-025-00913-z](https://doi.org/10.1007/s00778-025-00913-z). **Cloud OLTP cost survey / analytical model.**  
12. **van Renen, A. and Leis, V. (2023)** ‘Cloud analytics benchmark’, *PVLDB*, 16(6), pp. 1413–1425. doi: [10.14778/3583140.3583156](https://doi.org/10.14778/3583140.3583156). Latency-optimal ≠ cost-optimal (≈6.8× cost gap example).  
13. **Bodner, T., Radig, T., Justen, D., Ritter, D. and Rabl, T. (2025)** ‘An empirical evaluation of serverless cloud infrastructure for large-scale data processing’, in *EDBT 2025*, pp. 935–948. doi: [10.48786/edbt.2025.76](https://doi.org/10.48786/edbt.2025.76). Serverless compute/storage cost break-evens (incl. DynamoDB among AWS services).  
14. **Ziegler, T., Bernstein, P.A., Leis, V. and Binnig, C. (2023)** ‘Is scalable OLTP in the cloud a solved problem?’, in *CIDR 2023*. URL: https://www.cidrdb.org/cidr2023/papers/p50-ziegler.pdf.  
15. **Zhou, Y. et al. (2024)** ‘A contract-aware and cost-effective LSM store for cloud storage with low latency spikes’, *ACM Transactions on Storage*, 20(2). doi: [10.1145/3643851](https://doi.org/10.1145/3643851). Tail latency ↔ cloud storage contracts.  
16. **König, A.C., Shan, Y., Newatia, K., Marshall, L. and Narasayya, V. (2023)** ‘Solver-in-the-loop cluster resource management for Database-as-a-Service’, *PVLDB*, 16(13), pp. 4254–4267. doi: [10.14778/3625054.3625062](https://doi.org/10.14778/3625054.3625062).

### 4.5 Cloud-native storage, disaggregation, serverless storage, FaaS latency

17. **Zhang, J. et al. (2023)** ‘CDSBen: benchmarking the performance of storage services in cloud-native database system at ByteDance’, *PVLDB*, 16(12), pp. 3584–3596. doi: [10.14778/3611540.3611549](https://doi.org/10.14778/3611540.3611549).  
18. **Pang, X. and Wang, J. (2024)** ‘Understanding the performance implications of the design principles in storage-disaggregated databases’, in *SIGMOD 2024*. doi: [10.1145/3654983](https://doi.org/10.1145/3654983).  
19. **Zhang, J. et al. (2023)** ‘InfiniStore: elastic serverless cloud storage’, *PVLDB*, 16(7), pp. 1629–1642. doi: [10.14778/3587136.3587139](https://doi.org/10.14778/3587136.3587139).  
20. **Durner, D., Leis, V. and Neumann, T. (2023)** ‘Exploiting cloud object storage for high-performance analytics’, *PVLDB*, 16(11), pp. 2769–2782. doi: [10.14778/3611479.3611486](https://doi.org/10.14778/3611479.3611486).  
21. **Liu, X. et al. (2023)** ‘FaaSLight: general application-level cold-start latency optimization for Function-as-a-Service in serverless computing’, *ACM TOSEM*, 32(5), 119. doi: [10.1145/3585007](https://doi.org/10.1145/3585007). Motivates Lambda warm-up / cold-start control.

### 4.6 Vendor documentation (billing / capacity modes / sharding only — not peer-reviewed evidence)

22. **Amazon Web Services (2025)** *Amazon DynamoDB Developer Guide: Read/Write Capacity Mode*. Available at: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadWriteCapacityMode.html  
23. **Amazon Web Services (2025)** *DynamoDB burst and adaptive capacity*. Available at: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/burst-adaptive-capacity.html  
24. **Amazon Web Services (2025)** *Best practices for designing and using partition keys effectively* / write sharding. Available at: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-sharding.html  

**Literature-review structure (theme, do not catalogue):**

1. Persistence benchmarking without meters (Pantelić; Ferreira cloud NoSQL).  
2. Skew and key placement (Kanellis; Li et al.; Eldeeb Neuroshard; Elhemali hot partitions).  
3. Metered cost models and cloud OLTP economics (Lei; Haubenschild & Leis; van Renen & Leis; Bodner; Zhou).  
4. Serverless capacity / FaaS interference (Barnhart Aurora Serverless; Liu FaaSLight; König DBaaS control plane).  
5. Gap statement: **no study varies key design × capacity mode on live DynamoDB while measuring throttles + RCU/WCU + cost/10k under Lambda-driven Zipfian workloads.**

Update and expand substantially beyond any prior proposal text; **do not copy-paste** the Research-in-Computing proposal.

---

## 5. Research-paper-style report (≤20 pages)

**Mandatory sections (NCI handbook):**

1. **Abstract** — background, problem, what you did (factorial 3×2×4 from Lambda), main findings placeholders, theory/practice meaning, open issues.  
2. **Introduction** (~1–2 pp) — problem, motivation, RQ, objectives, contribution, limitations (single region/account), report roadmap.  
3. **Literature Survey** (~3–4 pp) — critical themes §4; contrast table vs this study; end with niche/gap.  
4. **Outputs Summary** (≤2 pp) — artefacts: IaC, workload suite, analysis pipeline, report, config manual; type and users.  
5. **Research Methodology** — factorial design §2, resources (DynamoDB, Lambda, CloudWatch), evaluation plan, hypotheses, stats, ethics.  
6. **Design and Implementation Specifications** — architecture diagram narrative; key schemas K1–K3; capacity configs; Lambda driver; metrics path; **no long code dumps**.  
7. **Evaluation / Results and Critical Analysis** — tables/figures for latency, throughput, throttles, RCU/WCU, cost/10k; ANOVA/ART; trade-off surface; compare to Pantelić (ordering) and to cost papers (latency≠cost); honesty on nulls.  
8. **Conclusions and Discussion** — RQ answered?; objectives met?; validity; future work (GSI, multi-region, DAX/caching, longer adaptive-capacity horizons).  
9. **References** — Harvard; only §4 items actually cited.

**Marking alignment (MSc Cloud Computing):** weekly monitoring is student-owned; final submission quality must support Project Final Submission (88%). Emphasise artefact quality, evaluation rigour, configuration manual, referencing.

---

## 6. Configuration manual (separate document; not in 20-page limit)

Must enable a marker to reproduce the ICT solution:

- Environment prerequisites and versions  
- AWS account setup, region, IAM  
- Deploy / seed / run / analyse / teardown  
- How to switch among six configurations  
- How to interpret CloudWatch metrics and CSVs  
- Troubleshooting (throttles, cold starts, permission errors, Zipf generator checks)  
- Cost monitoring and abort  
- Mapping from experiment cells to result filenames  

---

## 7. Execution order for Claude

1. Confirm baseline Pantelić (2026) citation block and list replacements = **none**.  
2. Emit repository skeleton + IaC modules for six configs + Lambda workload + Zipfian generator.  
3. Write `RUNBOOK.md` and `configuration_manual/`.  
4. Write analysis scripts with **empty result schema** and cost model wired to `prices.yaml`.  
5. Draft full report with methodology complete and Results section using `[TO BE FILLED FROM EXPERIMENT]` tables structured for the six×four cells.  
6. Self-audit: every citation ∈ §4; every DV in §2.3 appears in Evaluation plan; n=30 and settling interval stated; no fabricated numeric results.  
7. Final line of every major deliverable file’s author block: student name as below.

---

## 8. Hard constraints

- No invented citations, DOIs, or paper titles.  
- No fabricated experimental numbers.  
- No personal/production data.  
- Do not expand scope to GSI/multi-region/DAX in the primary factorial (future work only).  
- Do not replace Pantelić et al. (2026); it is verified.  
- Prefer absolute metrics (ms, throttle counts, USD/10k ops) over vague “better/worse”.  
- Interaction term in ANOVA is load-bearing — do not collapse to one-way tests only.

---

## 9. Acceptance test (run on your own output)

- [ ] Report contains all handbook sections.  
- [ ] ≥20 verified 2022–2026 scholarly sources cited from §4 with DOI/URL.  
- [ ] Baseline Pantelić retained; latency + throughput metrics present; RCU/WCU, throttles, cost/10k added.  
- [ ] Factorial 3 key × 2 capacity × 4 workloads from Lambda fully specified and implemented in IaC/workloads.  
- [ ] Zipfian skew documented.  
- [ ] IaC + RUNBOOK + configuration manual present.  
- [ ] Cost derivation reproducible from published prices.  
- [ ] Last line of this master prompt respected in authorship.

---

**Baseline verification note for the executor:** Pantelić et al. (2026) is a real MDPI *Future Internet* article (published 15 Jan 2026), DOI 10.3390/fi18010053. **Replacements: none.**

**Paper count in corpus:** 21 peer-reviewed scholarly items with DOI/URL in §4.1–4.5 (entries 1–21) + 3 AWS documentation URLs for mechanisms (§4.6). No invented citations.

---

Rasool Basha Durbesula
