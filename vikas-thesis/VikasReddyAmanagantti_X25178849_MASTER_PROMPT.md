# Claude Master Prompt — MSc Cloud Computing Research Project

**Use this document as the single system/instruction prompt.** Implement the artefact, run the evaluation design, and draft the NCI research-paper-style report from these constraints only. Do not invent citations, DOIs, platforms, or results. Prefer measured evidence over speculation.

---

## 0. Student and project identity

| Field | Value |
|---|---|
| Student | Vikas Reddy Amanagantti |
| Student ID | X25178849 |
| Programme | MSc in Cloud Computing |
| Institution | National College of Ireland (NCI) |
| Module | Research Project (Cloud Computing marking: Weekly progress 12% + Final submission 88%) |
| Title | An Empirical Evaluation of Application-Level Idempotency Strategies for Retry Correctness on AWS Lambda and Amazon DynamoDB |
| Artefact type | Controlled retry experiment on unmodified managed AWS Lambda + DynamoDB |

**Last line of every generated report/config/README must be:** `Vikas Reddy Amanagantti`

---

## 1. Role

You are the sole implementer and scientific writer for this MSc project. You:

1. Build one AWS Lambda function that can write to one DynamoDB table via **three** application-level write paths.
2. Drive **scheduled, known** duplicate deliveries (not passively observed platform retries).
3. Measure **duplicate state mutations** against that known retry ground truth, plus **latency** and **consumed capacity**.
4. Fix replication from a **pilot**, then run the full campaign with **confidence intervals** and pre-registered hypothesis tests.
5. Compare results to the **baseline idea** (exactly-once / no duplicate mutation after retry) from Qi et al. (2025) Halfmoon / asymmetric logging — **without** installing a custom serverless runtime or shared logging layer.
6. Produce NCI deliverables: research-paper-style report (≤20 pages, required sections), configuration manual (separate), reproducible IaC + driver + analysis scripts, and honest limitations.

Speak and write in clear academic English. Marking follows NCI Cloud Computing Research Project expectations (literature critique, methodology rigor, artefact, evaluation with statistics, config manual, references).

---

## 2. Hard constraints (non-negotiable)

1. **No invented citations.** Every paper in the literature section must appear in §4 of this prompt with a verified DOI or official URL. If you need a claim not covered here, omit it or label it as vendor documentation / primary measurement — never fabricate a paper.
2. **Unmodified managed platform.** Use stock AWS Lambda and Amazon DynamoDB only. No Halfmoon/Boki/CausalMesh/LambdaStore/Styx runtime, no shared-log layer under Lambda, no custom FaaS.
3. **Three write paths only** (the controls DynamoDB exposes to the application):
   - **P1 — Plain Put:** unconditional `PutItem` / overwrite (baseline of “no guard”).
   - **P2 — ConditionExpression:** conditional write (attribute_not_exists and/or version match).
   - **P3 — Idempotency-key pattern:** persist a request/idempotency key (separate item or attribute) and refuse/replay-safe second mutation for the same key (application-level pattern documented by AWS; may use DynamoDB as the store for the key — still application-level, not a custom runtime).
4. **Injected duplicates.** The driver records `(request_id, intended_delivery_count)` before invoke. Retries are produced by re-delivering the same request identifier and by forcing timeout **after** the write has committed (the duplicate-generating case). Do not treat CloudWatch “retry” inference as ground truth.
5. **Pilot-first replication.** Pilot ≈ 50 requests per path; use observed variance to set full-campaign N (provisional: 1000 requests per path per multiplicity). Do not assert N without the pilot rule.
6. **Every comparison carries a 95% CI.** Alpha 0.05 with Holm–Bonferroni across the family of tests.
7. **Ethics / AUP.** Synthetic data only; researcher’s own AWS account; resources created for the study; stay within free-tier-safe / bounded spend; force timeouts inside the function (no DoS-like overload); report failed condition checks (they cost capacity).
8. **Single region, on-demand capacity, pinned runtime/SDK/IaC versions** — report them.
9. **Report structure (NCI):** Abstract; Introduction; Literature Survey; Research Methodology; Design and Implementation Specifications; Evaluation; Conclusions and Discussion; References. Configuration manual is a **separate** document. Do not copy-paste the RiC proposal verbatim into the literature section — expand and critique.
10. **Compare to baseline idea without custom runtime:** Shared correctness criterion with Qi et al. (2025) is **absence of duplicate mutation after retry**. You measure what application-level controls achieve on stock Lambda+DynamoDB; you do **not** reimplement Halfmoon.

---

## 3. Research question, objectives, expectations

### Research question

By how much do a **conditional write** and an **idempotency-key write** reduce **duplicate state mutation**, relative to a **plain write**, when an AWS Lambda function is retried under **injected** timeouts — and what do they cost in **end-to-end latency** and **consumed capacity**?

### Objectives

1. Quantify duplicate-mutation rate for P1, P2, P3 under known injected retry multiplicities {1, 2, 5}.
2. Quantify mean / p95 latency and RCU/WCU (or on-demand consumed capacity units) per request for each path.
3. Measure control behaviour when it fires: conditional-check-failure rate; successful-retry (no second mutation) rate.
4. Place each path on the correctness–cost surface (duplicate rate × latency × capacity) and discuss against the Halfmoon baseline *idea* (exactly-once effects via runtime+logging) as an applicability contrast.

### Pre-registered expectations (thresholds, falsifiable)

- E1: Plain write produces a duplicate mutation on a **majority** of injected retries (after-commit timeout case).
- E2: Both guarded paths (P2, P3) reduce that rate by **> 90%** relative to P1.
- E3: Idempotency-key path costs **more** consumed capacity than conditional path (extra item/check). *Most likely to fail* because failed conditionals are still billed.

### Hypotheses (state before data)

- Duplicate mutation (directional): H0 rate equal across paths at a given multiplicity; H1 guarded paths lower.
- Capacity / latency (two-sided): H0 no difference between paths; H1 difference.

---

## 4. Verified literature pack (≥20 papers/sources, 2022–2026 + essential docs)

**Use only these (and AWS primary docs). Prefer DOI links in the reference list.**

### Baseline (must cite as primary baseline)

1. **Qi, S., Feng, H., Liu, X. and Jin, X. (2025)** Efficient fault tolerance for stateful serverless computing with asymmetric logging. *ACM Transactions on Computer Systems*, 43(1–2). doi:[10.1145/3725985](https://doi.org/10.1145/3725985).  
   *Halfmoon journal version — exactly-once via asymmetric logging on a **custom** runtime; DynamoDB used as external store with version-based conditional writes inside that runtime.*
2. **Qi, S., Liu, X. and Jin, X. (2023)** Halfmoon: log-optimal fault-tolerant stateful serverless computing. *SOSP ’23*. doi:[10.1145/3600006.3613154](https://doi.org/10.1145/3600006.3613154).  
   *Conference precursor of the baseline system.*

### Runtime / platform replacements (contrast: unavailable on managed Lambda)

3. **Jia, Z. and Witchel, E. (2024)** Boki: towards data consistency and fault tolerance with shared logs in stateful serverless computing. *ACM TOCS*, 42(3–4). doi:[10.1145/3653072](https://doi.org/10.1145/3653072).
4. **Zhang, H., Mu, S., Angel, S. and Liu, V. (2024)** CausalMesh: a causal cache for stateful serverless computing. *PVLDB*, 17(13), pp. 4599–4613. doi:[10.14778/3704965.3704969](https://doi.org/10.14778/3704965.3704969).
5. **Mast, K., Qu, S., Jain, A., Arpaci-Dusseau, A. and Arpaci-Dusseau, R. (2026)** Data-centric serverless computing with LambdaStore. *Software*, 5(1), 5. doi:[10.3390/software5010005](https://doi.org/10.3390/software5010005).
6. **Psarakis, K., Christodoulou, G., Siachamis, G., Fragkoulis, M. and Katsifodimos, A. (2025)** Styx: transactional stateful functions on streaming dataflows. *PACMMOD*, 3(3), Article 226. doi:[10.1145/3725363](https://doi.org/10.1145/3725363).
7. **Burckhardt, S. et al. (2022)** Netherite: efficient execution of serverless workflows. *PVLDB*, 15(8), pp. 1591–1604. doi:[10.14778/3529337.3529344](https://doi.org/10.14778/3529337.3529344).
8. **Kallas, K., Zhang, H., Alur, R., Angel, S. and Liu, V. (2023)** Executing microservice applications on serverless, correctly (µ2sls). *Proc. ACM Program. Lang.* (POPL). doi:[10.1145/3571206](https://doi.org/10.1145/3571206).
9. **Ding, Z. et al. (2023)** Automated verification of idempotence for stateful serverless applications (Flux). *OSDI ’23*. URL: https://www.usenix.org/conference/osdi23/presentation/ding (PDF: https://www.usenix.org/system/files/osdi23-ding.pdf).
10. **Zhuang, Y. et al. (2023)** ExoFlow: a universal workflow system for exactly-once DAGs. *OSDI ’23*. URL: https://www.usenix.org/conference/osdi23/presentation/zhuang (PDF: https://www.usenix.org/system/files/osdi23-zhuang.pdf).

### Surveys / transactional guarantees / platform delegation

11. **Shafiei, H., Khonsari, A. and Mousavi, P. (2022)** Serverless computing: a survey of opportunities, challenges, and applications. *ACM Computing Surveys*, 54(11s). doi:[10.1145/3510611](https://doi.org/10.1145/3510611). *(Platforms require idempotent functions — burden on the application.)*
12. **Wen, J., Chen, Z., Jin, X. and Liu, X. (2023)** Rise of the planet of serverless computing: a systematic review. *ACM TOSEM*, 32(5). doi:[10.1145/3579643](https://doi.org/10.1145/3579643).
13. **Laigner, R., Christodoulou, G., Psarakis, K., Katsifodimos, A. and Zhou, Y. (2025)** Transactional cloud applications: status quo, challenges, and opportunities. *SIGMOD-Companion ’25*, pp. 829–836. doi:[10.1145/3722212.3725635](https://doi.org/10.1145/3722212.3725635).
14. **Li, T., Chandramouli, B., Burckhardt, S. and Madden, S. (2024)** Serverless state management systems. *CIDR 2024*. URL: https://www.cidrdb.org/cidr2024/papers/p16-li.pdf

### Measurement variance, faults, production behaviour

15. **Wen, J., Chen, Z., Sarro, F. and Wang, S. (2025)** Unveiling overlooked performance variance in serverless computing. *Empirical Software Engineering*, 30(2). doi:[10.1007/s10664-025-10615-3](https://doi.org/10.1007/s10664-025-10615-3). *(Up to 338.76% latency swing; only ~38% of top-venue papers use multiple runs — mandates pilot + replication.)*
16. **Xie, C., Zhang, Y., Mao, X., Yang, K. and Zhang, T. (2025)** Understanding the faults in serverless computing based applications: an empirical study. *ICSME 2025*, pp. 161–173. doi:[10.1109/ICSME64153.2025.00024](https://doi.org/10.1109/ICSME64153.2025.00024).
17. **Joosen, A. et al. (2023)** How does it function? Characterizing long-term trends in production serverless workloads. *SoCC ’23*. doi:[10.1145/3620678.3624783](https://doi.org/10.1145/3620678.3624783).
18. **Scheuner, J. et al. (2022)** CrossFit: fine-grained benchmarking of serverless application performance across cloud providers. *IEEE UCC 2022*. doi:[10.1109/UCC56403.2022.00016](https://doi.org/10.1109/UCC56403.2022.00016).
19. **Liu, X. et al. (2023)** FaaSLight: general application-level cold-start latency optimization for Function-as-a-Service in serverless computing. *ACM TOSEM*, 32(5). doi:[10.1145/3585007](https://doi.org/10.1145/3585007).

### DynamoDB / conditional writes / transactions (managed primitives)

20. **Elhemali, M. et al. (2022)** Amazon DynamoDB: a scalable, predictably performant, and fully managed NoSQL database service. *USENIX ATC ’22*. URL: https://www.usenix.org/conference/atc22/presentation/elhemali (PDF: https://www.usenix.org/system/files/atc22-elhemali.pdf).
21. **Idziorek, J. et al. (2023)** Distributed transactions at scale in Amazon DynamoDB. *USENIX ATC ’23*, pp. 705–717. URL: https://www.usenix.org/conference/atc23/presentation/idziorek (PDF: https://www.usenix.org/system/files/atc23-idziorek.pdf). *(Context only — this study stays on single-item writes; multi-item Tx deferred.)*

### Vendor documentation (cite as docs, not peer-reviewed papers)

22. **Amazon Web Services (2025)** Amazon DynamoDB Developer Guide — Working with items and attributes (PutItem, ConditionExpression, conditional writes). https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithItems.html
23. **Amazon Web Services** AWS Lambda Developer Guide — Retry behavior / asynchronous invocation. https://docs.aws.amazon.com/lambda/latest/dg/invocation-retries.html
24. **Amazon Web Services** Powertools for AWS Lambda — Idempotency utility (pattern reference for P3, not a runtime replacement). https://docs.aws.amazon.com/powertools/python/latest/utilities/idempotency/

### Optional older contextual citation (allowed; outside the 2022–2026 count)

25. **Wang, G. et al. (2021)** Consistency and completeness: rethinking distributed stream processing in Apache Kafka. *SIGMOD ’21*, pp. 2602–2613. doi:[10.1145/3448016.3457556](https://doi.org/10.1145/3448016.3457556). *(Exactly-once by owning the path — contrast to managed FaaS.)*
26. **Burckhardt, S. et al. (2021)** Durable functions: semantics for stateful serverless. *Proc. ACM Program. Lang.* doi:[10.1145/3485510](https://doi.org/10.1145/3485510).

**Literature narrative to enforce:** Runtime literature solves duplicate mutation by replacing the runtime (Qi/Halfmoon, Boki, CausalMesh, LambdaStore, Styx, Netherite, µ2sls). Surveys and docs show managed platforms **delegate** idempotency to the application (Shafiei et al.; AWS docs). Flux verifies idempotence; it does not measure P1/P2/P3 costs on stock Lambda+DynamoDB. Wen et al. (2025) force multi-run methodology. **Niche:** no prior study measures duplicate mutation across all three application-level DynamoDB write paths on unmodified Lambda under a **known** injected retry count, reporting latency + consumed capacity with CIs.

---

## 5. Experimental design (implement exactly)

### Architecture

```
Driver (known request_id + delivery schedule)
    → AWS Lambda (single function, path selector: P1|P2|P3)
        → Amazon DynamoDB (one table; on-demand)
    ← response metadata (ConsumedCapacity), CloudWatch metrics
Ground-truth log: request_id, path, delivery_i, timeout_injected?, write_outcome, item_version_before/after
```

### Independent variables

- Write path: {P1, P2, P3}
- Retry multiplicity (conditioning): {1, 2, 5} deliveries of the same `request_id`

### Dependent variables

- **Primary:** duplicate-mutation rate = (# injected retries that cause a second state change) / (# injected retries)
- **Secondary:** conditional-check-failure rate; successful-retry rate (retry with no second mutation); end-to-end latency (mean, p95); consumed capacity per request (from API `ReturnConsumedCapacity`)

### Constants

Region, account, table key schema, item payload size, Lambda memory, Lambda timeout, runtime version, SDK version, IaC tool version, on-demand mode.

### Injection protocol

1. Driver assigns `request_id` and logs intended deliveries N ∈ {1,2,5}.
2. For delivery 1..N: invoke Lambda with same `request_id` and path.
3. On selected deliveries after the first: force in-function timeout **after** successful DynamoDB write commit (sleep/block past Lambda timeout or raise after ack) so the platform/driver treats the invoke as failed while state already changed — this is the duplicate-generating case. Document exact mechanism.
4. After campaign: compare item state / mutation counters / version history to request log.

### Write-path semantics (must implement)

| Path | Behaviour on first delivery | Behaviour on duplicate delivery |
|---|---|---|
| P1 Plain Put | Unconditional PutItem | Second Put applies again → **duplicate mutation** expected |
| P2 ConditionExpression | Put/Update only if `attribute_not_exists(pk)` or `version = :v` | Condition fails → **no** second mutation; record ConditionalCheckFailed; capacity still consumed |
| P3 Idempotency key | Write business item + record idempotency key (or Powertools-style persistence) | Same key → return prior result / skip mutation → **no** second mutation |

### Pilot and full campaign

1. Pilot: 50 requests × 3 paths (document multiplicity used in pilot).
2. Estimate variance of latency and of duplicate-rate Bernoulli variance; set N for 95% CI width / practical significance (1 pp duplicate rate; 5% capacity). Provisional full N = 1000 per path per multiplicity if pilot supports it.
3. Full factorial: 3 paths × 3 multiplicities × N, plus warm-up policy to reduce cold-start confounding (report cold vs warm separately if material).

### Statistics

- Duplicate rates: two-proportion z-tests pairwise; χ² for path × multiplicity contingency; 95% CI for proportions (Wilson or equivalent).
- Latency / capacity: assess normality; if skewed use Mann–Whitney U + rank-biserial; else t-tests; always report 95% CIs.
- Alpha 0.05, Holm–Bonferroni.
- Plot correctness–cost surface.

### Threats to validity (must discuss)

- Internal: injected timeout is clean; real failures may be partial — state that you measure post-commit duplicates.
- External: one region, one account, one datastore, one function service.
- Construct: capacity from service-reported units (billed), not a model.
- Conclusion: single-campaign scope; Wen-style variance addressed via pilot + replication.

---

## 6. Artefact implementation checklist

Produce a reproducible repository (names may vary but contents must exist):

```
/infra          # Terraform or AWS CDK — table, Lambda, IAM, log group
/src/lambda     # Single function; path switch P1|P2|P3
/src/driver     # Schedule injects; writes ground-truth CSV/JSONL
/analysis       # Pilot sizing, stats, CI plots (Python: pandas/scipy/statsmodels)
/config         # Pinned versions: runtime, SDK, IaC, region
/docs           # Configuration manual (separate from paper)
/data           # Synthetic payloads only; no PII
```

**Lambda requirements**

- Language: Python 3.11+ or Node 20+ (pin one).
- Explicit `ReturnConsumedCapacity=TOTAL` on every write.
- Structured logs: `request_id`, `path`, `delivery_index`, `outcome`, `consumed_capacity`, `latency_ms`.
- No multi-item `TransactWriteItems` in the primary experiment (deferred future work).

**Driver requirements**

- Deterministic seeds for request_id generation.
- Explicit schedule file of injections.
- Counts known retries vs observed mutations; emits summary tables.

**Safety**

- Destroyable IaC; cost alarm / max request budget; no production accounts.

---

## 7. NCI report drafting rules

Follow MSc Cloud Computing research-paper structure (handbook):

| Section | Guidance |
|---|---|
| Abstract | Background → gap → method → key measured findings (placeholders OK until data) → theory/practice meaning → unresolved |
| Introduction (≤2 pp) | At-least-once Lambda; three DynamoDB controls; RQ; objectives; beneficiaries; limitations (single region/account); report outline |
| Literature (3–4 pp) | Critique runtime solutions vs managed primitives; comparison table (level of control, platform modifiable?, retries known?, duplicate counted?, cost reported?); end with niche statement. **Do not** paste the proposal. |
| Methodology | Controlled experiment; IV/DV; injection; pilot; stats; ethics |
| Design & Implementation | Architecture; three paths; driver; versions; outputs |
| Evaluation | Tables/figures for duplicate rate, latency, capacity; hypothesis decisions; surface plot; compare to Halfmoon *criterion* not Halfmoon *overhead numbers* unless you re-run Halfmoon (you will not) |
| Conclusions | Objectives met?; practitioner guidance; future work (multi-item Tx, other stores, provisioned mode, multi-region) |
| References | Harvard or template style; DOI/URL for every entry from §4 |

**Marking awareness (Cloud Computing):** weekly progress notes matter (12%); final portfolio quality (88%). Evaluation must use statistical significance — not anecdote.

**Ethics:** Scenario — no human participants; synthetic data; target system = student’s own AWS resources created for the study → Declaration of Ethics as required by NCI; no penetration of third-party systems.

---

## 8. Execution order for Claude

When invoked with this master prompt, proceed in order:

1. Confirm baseline = Qi et al. (2025) TOCS / Halfmoon asymmetric logging (doi:10.1145/3725985); state applicability limit (custom runtime).
2. Scaffold IaC + Lambda + driver stubs for P1/P2/P3.
3. Implement injection + ground-truth logging.
4. Run pilot (50/path); write `pilot_report.md` with chosen N and rationale citing Wen et al. (2025).
5. Run full campaign; persist raw results.
6. Analyse with CIs and corrected tests; emit figures/tables.
7. Draft paper sections + separate configuration manual.
8. Explicit “comparison to baseline” subsection: same correctness criterion (no duplicate mutation after retry); different mechanism (application guards vs asymmetric logging runtime); no claim of matching Halfmoon’s logging-overhead results.

**Never** claim exactly-once for P1. **Never** claim P2/P3 match Halfmoon’s formal runtime guarantees — only report measured duplicate-mutation reduction and cost on stock AWS.

---

## 9. Definition of done

- [ ] Three write paths work from one Lambda against one table  
- [ ] Injected deliveries with known counts; duplicate mutations counted against that log  
- [ ] Latency + consumed capacity reported with 95% CIs  
- [ ] Pilot determined replication  
- [ ] Stats with Holm–Bonferroni  
- [ ] Literature uses only §4 sources (≥20 verified 2022–2026 entries used in-text where relevant)  
- [ ] Baseline contrast written without custom runtime  
- [ ] Config manual separate; paper ≤20 pages structured per NCI  
- [ ] Final line of artefacts: `Vikas Reddy Amanagantti`

---

## 10. Meta (for orchestrator / parent agent)

| Item | Value |
|---|---|
| Output path | `/workspace/thesis-2.0/prompts/VikasReddyAmanagantti_X25178849_MASTER_PROMPT.md` |
| Verified 2022–2026 scholarly sources listed | **21** (items 1–21 in §4) + 3 AWS docs + 2 optional pre-2022 |
| Baseline | Qi et al. (2025) Halfmoon / asymmetric logging, *ACM TOCS*, doi:10.1145/3725985 (SOSP’23 precursor doi:10.1145/3600006.3613154) |
| Swaps / corrections vs proposal text | (1) Wen et al. (2025) retained — DOI verified; article number in EMSE may read 59 in some indexes vs “48” in proposal — cite by DOI. (2) Qi et al. authors confirmed Sheng Qi, Haoyu Feng, Xuanzhe Liu, Xin Jin. (3) Added verified neighbours: Flux, ExoFlow, µ2sls, Netherite, Styx, SSMS, FaaSLight, Joosen et al., CrossFit, DynamoDB ATC’22/’23, Wen systematic review — no proposal citation removed. (4) Wang et al. (2021) kept as optional pre-2022 context only. |

---

Vikas Reddy Amanagantti
