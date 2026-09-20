# Baseline Papers Audit — 12 Theses (excl. kasi-thesis)

**Date:** 2026-09-20  
**Scope:** `BASELINE_PAPER.md` for each listed thesis + PDF first-page verification where present + STATUS / intro / bib for topic & gap  
**Method note:** Every `BASELINE_PAPER.md` is a thin citation stub (no Problem / Solution / Gap / Metrics sections). Gap and metrics judgements below are reconstructed from STATUS, LaTeX intros, and PDF abstracts—not from the MD files themselves.

---

## Executive summary

| # | Thesis | Year | Relevance | Metrics | Gap→Problem | MD quality | Flag |
|---|--------|------|-----------|---------|-------------|------------|------|
| 1 | anji | PASS (2025) | HIGH | PARTIAL | clear | thin | WSEAS venue |
| 2 | Varun | PASS (2025) | **LOW** | PARTIAL | weak | thin | **TierBase = KV store, not S3** |
| 3 | yashaswini | PASS (2025) | MEDIUM | PARTIAL | clear | thin | Xing = ceiling-only / Sensors |
| 4 | rassool | PASS (2026) | MEDIUM | PARTIAL | clear | thin | Pantelić self-hosted SQL/NoSQL |
| 5 | chaitanya | PASS (2025) | HIGH | PARTIAL | clear | thin | — |
| 6 | vikas | PASS (2025 TOCS) | HIGH | PARTIAL | clear | thin | **Wrong PDF attached** + bad arXiv ID |
| 7 | venkat-bora | PASS (2025) | MEDIUM | YES | weak | thin | MATLAB LU vs cloud Dask |
| 8 | Nemi | PASS (2026) | HIGH | YES | clear | thin | PDF missing; ICISS venue |
| 9 | mehak | PASS (2026) | HIGH | YES | clear | thin | arXiv preprint (ICDCS-accepted claim) |
| 10 | pooja | PASS (2026) | HIGH | PARTIAL | clear | thin | ICOIN + arXiv OA |
| 11 | uday | PASS (2026) | HIGH | PARTIAL | clear | thin | PDF is Research Square preprint of JNSM |
| 12 | vishvaksen | PASS (2025) | HIGH | YES | clear | thin | **arXiv-only preprint** |

**Universal MD finding:** All 12 `BASELINE_PAPER.md` files lack Problem/Solution/Gap/Metrics structure → content quality = **thin** everywhere.

---

## 1. anji-thesis

1. **Topic:** Reliability and recovery of Amazon SQS under injected consumer/downstream failures (localsim).  
2. **Baseline:** Kyrychenko, Ostapov & Kyrychenko — *Optimization of SQS Configurations for Efficient Batch Data Processing* — WSEAS Transactions on Systems, Vol. 24, pp. 36–43, **2025**. DOI `10.37394/23202.2025.24.4`. PDF present and matches.  
3. **Year / recency:** **PASS**  
4. **Relevance:** **HIGH** — same service (SQS), same config knobs (batch size, visibility timeout); thesis extends steady-state optimization into fault injection.  
5. **Metrics overlap:** **PARTIAL** — baseline: throughput, response time, queue length, utilization; thesis: loss, duplicates, DLQ, recovery time (+ throughput/latency for replication). Steady-state comparison possible; fault metrics are new.  
6. **Gap→Problem:** **clear** — intro states Kyrychenko optima assume healthy components; thesis asks whether those optima transfer under failure.  
7. **Issues / replacement:** Keep. Venue is WSEAS (weaker than IEEE/ACM); optional secondary baseline from stronger SQS/queueing venue if examiners push venue quality.  
8. **MD quality:** **thin**

---

## 2. Varun *(special scrutiny: TierBase / S3 FinOps)*

1. **Topic:** Predictive S3 storage-class recommendation, forecasting, and savings estimation (FinOps).  
2. **Baseline (as cited in `BASELINE_PAPER.md`):** Shen et al. — *TierBase: A Workload-Driven Cost-Optimized Key-Value Store* — **ICDE 2025**. DOI `10.1109/ICDE65448.2025.00049`; open PDF arXiv:2505.06556. PDF present.  
   - **PDF-verified title/authors:** Zhitao Shen et al. (Ant Group / Guangzhou Univ / SJTU) — distributed **key-value store** cost model (cache↔storage tiers; Redis/Memcached/Cassandra/HBase class).  
   - **Bib error:** `Varun/latex_report/refs.bib` retitles it as “Cloud Object Storage” — that title is **not** on the PDF.  
3. **Year / recency:** **PASS**  
4. **Relevance:** **LOW** — TierBase optimizes Ant Group KV-store space/performance cost, not Amazon S3 storage classes, Lifecycle, or Intelligent-Tiering. Shared theme (“tiering / cost”) is analogy only; domain mismatch confirmed by PDF abstract.  
5. **Metrics overlap:** **PARTIAL** — both discuss cost reduction / allocation; TierBase reports production cost % and space-performance model; thesis uses allocation accuracy, MAPE, USD savings vs Lifecycle/IT — not the same constructs.  
6. **Gap→Problem:** **weak** — intro filler claims “bridging the gap identified in Shen et al.” with a “temporal recency buffer,” which does not map to TierBase’s KV cost-model gap.  
7. **Issues / replacement:** **Replace or demote TierBase.** Prefer S3/object-storage FinOps baselines already named in STATUS (e.g. SkyStore / Liu et al. 2025, Yang et al. 2025 MLSys, Beck et al. 2025 naive forecast). Fix bib title to match PDF. Do not claim TierBase as an S3 baseline.  
8. **MD quality:** **thin**

---

## 3. yashaswini-thesis *(special scrutiny: Xing ceiling)*

1. **Topic:** Lightweight (rule-based) fault detection/localisation in AWS serverless microservices vs deep-learning accuracy, plus monitoring overhead.  
2. **Baseline:** Xing, Wang & Liu — *Multi-Dimensional Anomaly Detection and Fault Localization in Microservice Architectures: A Dual-Channel Deep Learning Approach with Causal Inference for Intelligent Sensing* — **Sensors** 25(11):3396, **2025**. DOI `10.3390/s25113396`. PDF present and matches. Reported F1 **93.8%**, localisation precision 87.6%.  
3. **Year / recency:** **PASS**  
4. **Relevance:** **MEDIUM** — same *problem family* (microservice anomaly detection + localisation) but **not** AWS serverless/CloudWatch/X-Ray; dual-channel DL + causal inference on general microservice KPIs. Thesis correctly uses it as Leg-1 **accuracy ceiling**, not same-rig peer.  
5. **Metrics overlap:** **PARTIAL** — F1 / localisation precision conceptually comparable; overhead ($) and Top-k on RCAEval are thesis-side; Xing does not share the AWS overhead or RCAEval protocol.  
6. **Gap→Problem:** **clear** (in proposal/STATUS) — Xing’s accuracy presupposes labelled training corpus unavailable to new cost-constrained serverless services; thesis measures untrained rule-based retention of accuracy + overhead.  
7. **Issues / replacement:** Keep Xing as **ceiling citation only** (already framed). Strengthen like-for-like with RCAEval published methods (BARO, CIRCA, TraceRCA). Do not treat Xing F1=0.938 as defeated on the same rig. MDPI *Sensors* is published OA but not a systems venue.  
8. **MD quality:** **thin**

---

## 4. rassool-thesis *(Pantelić concern)*

1. **Topic:** DynamoDB partition-key design × capacity mode performance–cost under serverless workloads.  
2. **Baseline:** Pantelić et al. — *Benchmarking SQL and NoSQL Persistence in Microservices Under Variable Workloads* — **Future Internet** 18:53, **2026**. DOI `10.3390/fi18010053`. PDF present and matches. Single-node containerized SQL/NoSQL (not AWS DynamoDB).  
3. **Year / recency:** **PASS**  
4. **Relevance:** **MEDIUM** — workload profiles (read/write/mixed, concurrency) transfer; engine is self-hosted SQL/NoSQL, **not** DynamoDB partition keys or on-demand/provisioned metering.  
5. **Metrics overlap:** **PARTIAL** — shared: latency (p95), throughput, CPU/memory; thesis adds throttle rate, RCU/WCU, $/10k ops (absent from baseline by design).  
6. **Gap→Problem:** **clear** — intro explicitly: Pantelić omits metered cost, throttling, consumed capacity; thesis adds those on DynamoDB.  
7. **Issues / replacement:** Acceptable as **methodological** baseline if gap is stated honestly. Stronger DynamoDB-native alternatives (adaptive capacity / hot-key / serverless DB papers) would raise relevance. MDPI *Future Internet* venue is mid-tier.  
8. **MD quality:** **thin**

---

## 5. chaitanya-thesis

1. **Topic:** Isolate Lambda Init Duration (cold start) across runtimes, package size, memory, warming.  
2. **Baseline:** Bluemke & Zdanowski — *Evaluation of configurations of AWS Lambda functions* — **Intl. Journal of Electronics and Telecommunications**, 71(3), **2025**. DOI `10.24425/ijet.2025.153619`. PDF present and matches.  
3. **Year / recency:** **PASS**  
4. **Relevance:** **HIGH** — same platform (AWS Lambda), configuration/cost-performance evaluation; thesis isolates Init Duration and expands runtimes/package/warming.  
5. **Metrics overlap:** **PARTIAL** — baseline: duration/cost by memory & arch; thesis: Init Duration, Duration, billed duration, cost — comparable family, finer cold-start split.  
6. **Gap→Problem:** **clear** — STATUS/abstract: prior configs report aggregate duration; this work isolates initialization.  
7. **Issues / replacement:** Keep. Venue is specialist (PAS/IJET), not top systems, but domain fit is strong.  
8. **MD quality:** **thin**

---

## 6. vikas-thesis *(PDF / arXiv integrity)*

1. **Topic:** Application-level idempotency on Lambda+DynamoDB (plain put / conditional / idempotency key) vs retry duplicates.  
2. **Baseline (intended, from bib/STATUS):** Qi, Feng, Liu & Jin — *Efficient fault tolerance for stateful serverless computing with asymmetric logging* (Halfmoon journal) — **ACM TOCS** 43(1–2), **2025**. DOI `10.1145/3725985`. Precursor: SOSP’23 Halfmoon DOI `10.1145/3600006.3613154`.  
3. **Year / recency:** **PASS** (TOCS 2025; SOSP precursor 2023 is WEAK if used alone—journal version saves recency).  
4. **Relevance:** **HIGH** — shared correctness criterion (no duplicate state mutation after retry); gap is custom runtime vs managed application-level primitives.  
5. **Metrics overlap:** **PARTIAL** — both care about duplicates / overhead; Halfmoon reports latency & logging overhead on custom runtime; thesis: duplicate-mutation rate, latency, consumed WCU on stock Lambda+DynamoDB.  
6. **Gap→Problem:** **clear** — custom-runtime exactly-once unavailable on managed FaaS; measure app-level paths.  
7. **Issues / replacement:**  
   - **Critical:** File `Qi_et_al_2025_Halfmoon_TOCS_baseline.pdf` is **not Halfmoon**. First page is Nahum et al., *Decongestion by Representation…*, ICLR 2024, **arXiv:2306.10606** (marketplace ML).  
   - `BASELINE_PAPER.md` wrongly pairs Halfmoon with `arXiv:2306.10606`. Halfmoon has **no** that arXiv ID; use TOCS DOI / author PDF.  
   - **Action:** Replace PDF with TOCS Halfmoon (or SOSP’23 PDF); delete wrong arXiv ID from MD. Citation text in bib is fine.  
8. **MD quality:** **thin** (+ factual error on arXiv)

---

## 7. venkat-bora-thesis

1. **Topic:** Multi-threaded vs distributed matrix scaling (multiply / LU) on cloud infrastructure (local Dask in practice).  
2. **Baseline:** Sabir & Alebrahim — *Coarse-Grained Column Agglomeration Parallel Algorithm for LU Factorization Using Multi-Threaded MATLAB* — **Mathematics** 13:298, **2025**. DOI `10.3390/math13020298`. PDF present and matches. Four-core Xeon, MATLAB R2020b.  
3. **Year / recency:** **PASS**  
4. **Relevance:** **MEDIUM** — shared LU / multi-thread matrix theme; baseline is MATLAB on a workstation, not cloud EC2/Dask or distributed network costs.  
5. **Metrics overlap:** **YES** — time, speedup, accuracy; thesis also memory/CPU — compatible core set.  
6. **Gap→Problem:** **weak** — “extend multi-threaded LU with Dask comparison” is incremental; cloud-network gap underspecified given local-only execution.  
7. **Issues / replacement:** Prefer a 2024–2026 cloud/HPC distributed linear-algebra or Dask/Ray scaling paper if claiming cloud infrastructure. Keep Sabir only as local multi-thread reference.  
8. **MD quality:** **thin**

---

## 8. Nemi

1. **Topic:** SecureFL-IDS — privacy-preserving federated intrusion detection (FL + DP) for cloud-native settings.  
2. **Baseline:** Saklani, Chohan & Sharma — *Privacy Preserving Cloud Native Intrusion Detection Using Federated Learning and Differential Privacy* — **2026 8th ICISS**, pp. 387–392. DOI `10.1109/iciss67859.2026.11454085`. **PDF not present** (paywall noted in MD).  
3. **Year / recency:** **PASS**  
4. **Relevance:** **HIGH** — same problem (PP FL-DP IDS, cloud-native); thesis reproduces then adds adaptive DP, compression, hybrid model.  
5. **Metrics overlap:** **YES** — accuracy, F1, communication (MB/round) aligned with STATUS replication targets.  
6. **Gap→Problem:** **clear** — related work lists fixed-ε DP, comm overhead, architecture limits; SecureFL-IDS targets those.  
7. **Issues / replacement:** Keep domain. Obtain IEEE PDF. Venue is ICISS (specialist conference)—acceptable but not top-tier security. Without PDF, claims about baseline numbers (~91.8%) are second-hand.  
8. **MD quality:** **thin**

---

## 9. mehak-thesis

1. **Topic:** Cross-head fusion for MHSA cluster telemetry / SLA monitoring (fix underprediction gap).  
2. **Baseline:** Thapliyal — *A Multi-Head Attention Approach for SLA Compliance Monitoring in Data Centers* — **arXiv:2605.05354** (PDF states accepted **IEEE ICDCS 2026**). PDF present and matches.  
3. **Year / recency:** **PASS**  
4. **Relevance:** **HIGH** — thesis reproduces one-head-per-metric MHSA and targets the paper’s underprediction behaviour with fusion.  
5. **Metrics overlap:** **YES** — accuracy, macro-F1, transient recall, underprediction bias used as reproduction targets.  
6. **Gap→Problem:** **clear** — STATUS: confirm systematic underprediction; fusion as targeted fix.  
7. **Issues / replacement:** Keep. **Preprint caveat:** currently arXiv; ICDCS acceptance claimed on PDF—prefer citing ICDCS proceedings when available. Domain (colo power/temp/humidity SLA) ≠ generic cloud cluster metrics; synthetic telemetry narrows external validity but mapping is intentional.  
8. **MD quality:** **thin**

---

## 10. pooja-thesis

1. **Topic:** Stability-aware predictive Kubernetes autoscaling (vs aggressive proactive / reactive HPA).  
2. **Baseline:** Wanigasooriya & Ekanayake — *NimbusGuard: A Novel Framework for Proactive Kubernetes Autoscaling Using Deep Q-Networks* — **IEEE ICOIN 2026**, pp. 726–731. DOI `10.1109/ICOIN68469.2026.11480646`; OA arXiv:2604.11017. PDF present (arXiv OA) and matches.  
3. **Year / recency:** **PASS**  
4. **Relevance:** **HIGH** — same domain (proactive K8s autoscaling vs HPA); thesis addresses agility–instability / scaling-event volatility.  
5. **Metrics overlap:** **PARTIAL** — both: SLA/performance vs cost/efficiency; thesis emphasises scaling events & pod volatility (stability), not DQN reward identically.  
6. **Gap→Problem:** **clear** — STATUS: reproduce agility–instability trade-off; stability-aware controller cuts events/volatility.  
7. **Issues / replacement:** Keep. ICOIN is a mid-tier networking conference; arXiv OA copy is fine if DOI cited. Prefer published IEEE PDF when accessible.  
8. **MD quality:** **thin**

---

## 11. uday-thesis

1. **Topic:** Federated QoS offload decisions for OneM2M IoT middleware (vs centralized RF).  
2. **Baseline:** Et-Tousy, Zyane & Sharif — *Adaptive QoS Management in OneM2M Standard: Machine Learning and Deep Learning for IoT Network Optimization* — **Journal of Network and Systems Management**, **2026**. DOI `10.1007/s10922-026-10071-4`. PDF on disk is **Research Square preprint** (`10.21203/rs.3.rs-7987618/v1`, posted Nov 2025); VoR note on PDF confirms JNSM publication 6 May 2026.  
3. **Year / recency:** **PASS**  
4. **Relevance:** **HIGH** — same OneM2M QoS / offload problem; thesis implements federated alternative the paper flags as future work.  
5. **Metrics overlap:** **PARTIAL** — baseline: accuracy, RTT, success rate, CPU/RAM; thesis: accuracy / macro-F1 of offload classifier (centralized vs federated vs single-site)—classifier metrics overlap; full QoS loop metrics less so.  
6. **Gap→Problem:** **clear** — STATUS: reproduce centralized RF; build federated alternative proposed as future work.  
7. **Issues / replacement:** Keep. Prefer publisher JNSM PDF over Research Square when possible; citation DOI is the published version (good).  
8. **MD quality:** **thin**

---

## 12. vishvaksen-thesis

1. **Topic:** Hybrid rule+ML IaC misconfiguration detection addressing comment-ablation precision collapse.  
2. **Baseline:** War, Rawass, Kabore, Samhi, Klein & Bissyandé — *Detection of Security Smells in IaC Scripts through Semantics-Aware Code and Language Processing* — **arXiv:2509.18790**, 23 Sep **2025** (University of Luxembourg). PDF present; **preprint only** (STATUS/bib: peer-review not confirmed).  
3. **Year / recency:** **PASS**  
4. **Relevance:** **HIGH** — thesis reproduces comment-removal ablation and builds hybrid detector for enumerable patterns.  
5. **Metrics overlap:** **YES** — Precision, Recall, F1 (same family; thesis uses simpler TF-IDF vs CodeBERT/LongFormer by design).  
6. **Gap→Problem:** **clear** — precision collapses without NL context; hybrid rules recover precision for easy patterns.  
7. **Issues / replacement:** Keep for gap mapping. **Venue risk:** arXiv-only—monitor for peer-reviewed version; optionally add Rahman ICSE/TOSEM or GLITCH as published anchors.  
8. **MD quality:** **thin**

---

## Special-scrutiny verdicts

### Varun + TierBase
**Confirmed concern.** PDF abstract: “Space-Performance Cost Model for **key-value store**… TierBase, a distributed key-value store developed by Ant Group.” Not S3 object storage. Relevance **LOW** for an S3 FinOps thesis. Bib currently mislabels title as object storage—do not rely on that. Replace with SkyStore / S3-class recommenders already listed in STATUS.

### Yashaswini + Xing
**Confirmed ceiling concern.** Xing is a strong published accuracy reference (Sensors 2025, F1 93.8%) but is Leg-1 citation-only, different telemetry stack, not AWS serverless. Gap mapping is clear; same-rig comparison must stay on RCAEval baselines. Do not over-claim “within 10 pp of Xing” without same-rig data.

### Rassool + Pantelić
**Partially confirmed.** Pantelić is recent and methodologically useful (workload profiles) but self-hosted SQL/NoSQL—not DynamoDB. Gap→metering mapping is **clear** in the intro; relevance stays **MEDIUM**, not HIGH.

### Preprint vs published
| Thesis | Status |
|--------|--------|
| mehak / Thapliyal | arXiv; PDF claims ICDCS 2026 acceptance |
| pooja / NimbusGuard | ICOIN 2026 DOI + arXiv OA PDF |
| uday / Et-Tousy | JNSM published DOI; disk PDF = Research Square preprint |
| vishvaksen / War | **arXiv only** — highest venue risk |
| vikas | Citation = strong TOCS; **attached PDF wrong** |
| Nemi | IEEE ICISS — PDF missing |

---

## Cross-cutting recommendations

1. **Enrich every `BASELINE_PAPER.md`** with Problem / Solution / Gap / Metrics / Comparable-metrics / Venue notes (currently universal **thin**).  
2. **Immediate fixes:** Varun (replace TierBase or demote); Vikas (replace wrong PDF + fix arXiv ID).  
3. **Prefer published VoR PDFs** for mehak, uday, pooja, Nemi when obtainable.  
4. **Do not invent** Problem/Solution/Gap inside MD without grounding in the PDF + thesis intro.

---

## Evidence sources (per thesis)

| Thesis | BASELINE_PAPER.md | PDF | Topic/gap sources |
|--------|-------------------|-----|-------------------|
| anji | yes | Kyrychenko…pdf | STATUS; introduction.tex |
| Varun | yes | Shen…TierBase.pdf | STATUS; PDF abstract; refs.bib |
| yashaswini | yes | Xing…Sensors.pdf | STATUS; proposal extract; evaluation.tex |
| rassool | yes | Pantelic…pdf | STATUS; introduction.tex |
| chaitanya | yes | Bluemke…pdf | STATUS |
| vikas | yes | **mismatch** | STATUS; refs.bib; PDF first page |
| venkat-bora | yes | Sabir…pdf | STATUS |
| Nemi | yes | **absent** | STATUS; README; refs.bib |
| mehak | yes | Thapliyal…pdf | STATUS |
| pooja | yes | NimbusGuard…pdf | STATUS; refs.bib |
| uday | yes | EtTousy…preprint.pdf | STATUS; refs.bib; PDF VoR note |
| vishvaksen | yes | War…arXiv.pdf | STATUS; refs.bib |
