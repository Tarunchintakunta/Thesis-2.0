# Baseline Papers Audit (CA2-aligned) — 12 Theses

**Date:** 2026-09-20 (rev 2 — CA2 alignment emphasis)  
**Exclude:** kasi-thesis  
**Primary criterion (user clarification):** baselines must **maximize alignment % with CA2 proposal scope, variables, methodology, and evaluation criteria** — not “recent” alone.  
**Secondary:** year PASS if 2024–2026; WEAK 2022–2023; FAIL older.

### How Baseline→CA2 alignment % is scored

| Component | Weight | What counts |
|-----------|--------|-------------|
| Scope / domain | 30% | Same service/problem class as CA2 RQ |
| Variables (IVs/DVs) | 25% | Same knobs / outcomes CA2 manipulates or retains |
| Methodology | 20% | Same experiment style CA2 inherits or extends |
| Metrics / eval criteria | 25% | Can thesis compare on CA2-listed metrics |

**Note:** This is **baseline↔CA2 fit**, not artefact completion %. Every `BASELINE_PAPER.md` still lacks Problem/Solution/Gap/Metrics → MD quality = **thin** for all 12.

---

## Executive table

| Thesis | CA2 baseline named? | Year | Relevance | Metrics overlap | Gap→Problem | **Baseline→CA2 %** | MD | Critical flag |
|--------|---------------------|------|-----------|-----------------|-------------|--------------------|----|---------------|
| anji | Yes — Kyrychenko | PASS | HIGH | PARTIAL | clear | **88%** | thin | — |
| Varun | Yes — TierBase (+SkyStore/Yang in lit) | PASS | **LOW** | PARTIAL | weak | **38%** | thin | KV≠S3; prefer SkyStore/Yang for scope |
| yashaswini | Yes — Xing (ceiling) | PASS | MEDIUM | PARTIAL | clear | **72%** | thin | Ceiling-only by CA2 design |
| rassool | Yes — Pantelić | PASS | MEDIUM | PARTIAL | clear | **78%** | thin | Self-hosted; metering gap intentional |
| chaitanya | Yes — Bluemke | PASS | HIGH | PARTIAL | clear | **92%** | thin | — |
| vikas | Yes — Halfmoon/Qi TOCS | PASS | HIGH | PARTIAL | clear | **86%** | thin | **Wrong PDF** / bad arXiv ID |
| venkat-bora | Yes — Sabir | PASS | MEDIUM | YES | weak→clear in CA2 | **74%** | thin | Threaded path only; need distributed peer |
| Nemi | Yes — Saklani | PASS | HIGH | YES | clear | **90%** | thin | PDF missing |
| mehak | Proxy CA2 — Thapliyal | PASS | HIGH | YES | clear | **91%** | thin | arXiv / ICDCS claim |
| pooja | Proxy CA2 — NimbusGuard | PASS | HIGH | PARTIAL | clear | **87%** | thin | ICOIN mid-tier |
| uday | Proxy CA2 — Et-Tousy | PASS | HIGH | PARTIAL | clear | **90%** | thin | Preprint PDF of VoR |
| vishvaksen | Proxy CA2 — War | PASS | HIGH | YES | clear | **89%** | thin | arXiv-only |

---

## 1. anji-thesis — Baseline→CA2 **88%**

1. **Topic:** SQS reliability/recovery under injected consumer & downstream failures (+ DIVE in CA2 narrative).  
2. **Baseline:** Kyrychenko, Ostapov & Kyrychenko — *Optimization of SQS Configurations for Efficient Batch Data Processing* — WSEAS Transactions on Systems, 24, 36–43, **2025**. DOI `10.37394/23202.2025.24.4`. PDF verified.  
3. **Year:** **PASS**  
4. **Relevance:** **HIGH** — CA2 (`anji_ca2_related_articles.html`) names this as the **direct baseline**; same SQS service and config ranges.  
5. **Metrics overlap:** **PARTIAL** — CA2 retains throughput/latency for steady-state replication; adds loss, duplicates, DLQ, recovery under faults.  
6. **Gap→Problem:** **clear** — steady-state optima under healthy consumers → failure-regime behaviour.  
7. **CA2 alignment breakdown:** Scope 28/30 · Vars 23/25 (VT, batch, delay; MRC/DLQ added) · Method 18/20 (config sweep + Boto3/queueing) · Metrics 19/25 → **88%**.  
8. **Issues:** Keep. Venue weaker than systems conferences; optional second baseline for chaos/fault injection (methodology peer), not replacement.  
9. **MD quality:** **thin** (no P/S/G/M structure)

---

## 2. Varun — Baseline→CA2 **38%** *(special scrutiny)*

1. **Topic (CA2):** Predictive S3 storage-class recommendation + forecasting + savings vs Lifecycle / Intelligent-Tiering (live AWS).  
2. **Baseline on disk:** Shen et al. — *TierBase: A Workload-Driven Cost-Optimized **Key-Value Store*** — ICDE **2025**. DOI `10.1109/ICDE65448.2025.00049` / arXiv:2505.06556. PDF verified as **KV store** (Ant Group).  
3. **Year:** **PASS**  
4. **Relevance:** **LOW** for S3 FinOps — PDF is Redis/HBase-class KV tiering, not S3 classes.  
5. **Metrics overlap:** **PARTIAL** — CA2 Table 2: allocation accuracy, MAPE/RMSE vs naive, realised USD/% vs **AWS-native** baselines, overhead. TierBase reports production KV cost % — not those constructs.  
6. **Gap→Problem:** **weak** — CA2 itself says TierBase/SkyStore show workload-aware > static but **lack forecasting**; thesis gap should be integrated recommend+forecast+savings on S3, not “KV cost model.”  
7. **CA2 alignment breakdown:** Scope **8/30** (named in CA2 lit but wrong storage class) · Vars **8/25** (tiering analogy only) · Method **10/20** (workload-driven cost) · Metrics **12/25** → **38%**.  
   - **Better CA2-aligned replacements already in CA2 refs:**  
     - **SkyStore** (Liu et al. 2025, PVLDB) — object storage across regions/clouds (**scope ↑**)  
     - **Yang et al. 2025 MLSys** — ML-driven storage placement (**variables/method ↑**)  
     - **Beck et al. 2025** — naive forecast baseline (**eval criteria exact match**)  
8. **Issues:** Demote TierBase to related work; make SkyStore or Yang the operational baseline for BASELINE_PAPER.md; fix bib title (do not call TierBase “Cloud Object Storage”).  
9. **MD quality:** **thin**

---

## 3. yashaswini-thesis — Baseline→CA2 **72%** *(Xing ceiling)*

1. **Topic (CA2):** Accuracy–overhead position of **untrained** CloudWatch/X-Ray rules vs learned detectors in AWS serverless microservices.  
2. **Baseline:** Xing, Wang & Liu — *Multi-Dimensional Anomaly Detection and Fault Localization…* — **Sensors** 25(11):3396, **2025**. DOI `10.3390/s25113396`. F1 93.8%. PDF verified.  
3. **Year:** **PASS**  
4. **Relevance:** **MEDIUM** — CA2 **names Xing as the baseline** but as **accuracy ceiling under labelled data**, not same-rig AWS peer. Domain = general microservice sensing, not CW/X-Ray.  
5. **Metrics overlap:** **PARTIAL** — CA2 retains F1 / top-k; adds telemetry volume, latency, $. Like-for-like arm is Pham/RCAEval baselines, not Xing.  
6. **Gap→Problem:** **clear** — labelled-corpus precondition vs no-history serverless.  
7. **CA2 alignment breakdown:** Scope 18/30 · Vars 18/25 · Method 14/20 (ceiling + three-leg is CA2 method; Xing alone ≠ full protocol) · Metrics 22/25 → **72%**.  
8. **Issues:** Keep Xing as Leg-1. Do **not** replace with a “more recent” paper that breaks the CA2 ceiling narrative. Strengthen Leg-2 (RCAEval/BARO/CIRCA) for method/metrics %. Optional: Zhang J. & Yang 2026 as secondary ceiling if CA2 allows.  
9. **MD quality:** **thin**

---

## 4. rassool-thesis — Baseline→CA2 **78%** *(Pantelić)*

1. **Topic (CA2):** DynamoDB partition-key × capacity mode → latency, throttling, RCU/WCU, $/10k ops under Lambda workloads.  
2. **Baseline:** Pantelić et al. — *Benchmarking SQL and NoSQL Persistence in Microservices Under Variable Workloads* — Future Internet 18:53, **2026**. DOI `10.3390/fi18010053`. Self-hosted container SQL/NoSQL. PDF verified.  
3. **Year:** **PASS**  
4. **Relevance:** **MEDIUM** — CA2 **explicitly chooses** Pantelić because it has workload profiles but **no meter**; that absence *is* the CA2 problem.  
5. **Metrics overlap:** **PARTIAL** — CA2 retains latency/throughput for comparability; adds throttle, capacity units, cost.  
6. **Gap→Problem:** **clear** (CA2 § niche).  
7. **CA2 alignment breakdown:** Scope 20/30 (persistence benchmarking, not DynamoDB-native) · Vars 20/25 (workloads yes; key/capacity are thesis IVs) · Method 18/20 · Metrics 20/25 → **78%**.  
8. **Issues:** Keep as CA2-named baseline. Raising % further would mean a DynamoDB hot-key / adaptive-capacity paper **as secondary**, not replacing Pantelić’s role. Bodner 2025 is complementary (prices services, not keys) per CA2.  
9. **MD quality:** **thin**

---

## 5. chaitanya-thesis — Baseline→CA2 **92%**

1. **Topic (CA2):** How much Lambda cold-start latency free controls remove, at what cost (Init isolated).  
2. **Baseline:** Bluemke & Zdanowski — *Evaluation of configurations of AWS Lambda functions* — IJET 71(3), **2025**. DOI `10.24425/ijet.2025.153619`. PDF verified.  
3. **Year:** **PASS**  
4. **Relevance:** **HIGH** — CA2 designed as extension: same Lambda config space; isolate Init; add runtime/package/warming.  
5. **Metrics overlap:** **PARTIAL→near YES** — CA2 **retains** duration & cost from Bluemke; adds Init Duration, cold frequency, tail percentiles.  
6. **Gap→Problem:** **clear**.  
7. **CA2 alignment breakdown:** Scope 29/30 · Vars 24/25 · Method 18/20 · Metrics 21/25 → **92%**.  
8. **Issues:** Keep. Joosen et al. 2025 is observational peer, not replacement.  
9. **MD quality:** **thin**

---

## 6. vikas-thesis — Baseline→CA2 **86%** *(PDF integrity)*

1. **Topic (CA2):** Duplicate-mutation rate of plain / conditional / idempotency-key writes on stock Lambda+DynamoDB under injected retries.  
2. **Baseline (CA2-named):** Qi, Feng, Liu & Jin — *Efficient fault tolerance… asymmetric logging* — **ACM TOCS** 43(1–2), **2025**. DOI `10.1145/3725985` (Halfmoon journal). Shared criterion: no duplicate mutation after retry.  
3. **Year:** **PASS**  
4. **Relevance:** **HIGH** — CA2 inverts custom-runtime exactly-once → measure managed app-level paths.  
5. **Metrics overlap:** **PARTIAL** — shared correctness; CA2 adds duplicate rate vs known retries, latency, WCU on stock platform.  
6. **Gap→Problem:** **clear**.  
7. **CA2 alignment breakdown:** Scope 28/30 · Vars 22/25 · Method 16/20 (injected retries vs runtime logging) · Metrics 20/25 → **86%**.  
8. **Issues:** Citation choice is CA2-correct. **File `Qi_et_al_2025_Halfmoon_TOCS_baseline.pdf` is wrong** (ICLR 2024 decongestion / arXiv:2306.10606). `BASELINE_PAPER.md` wrongly lists that arXiv for Halfmoon. Replace PDF; fix identifier. Does not change % of *chosen* baseline vs CA2.  
9. **MD quality:** **thin** (+ factual error)

---

## 7. venkat-bora-thesis — Baseline→CA2 **74%**

1. **Topic (CA2):** Threaded vs distributed matrix workloads on **matched-vCPU cloud** — crossover by matrix order; time + peak memory.  
2. **Baseline:** Sabir & Alebrahim — *Coarse-Grained… LU… Multi-Threaded MATLAB* — Mathematics 13:298, **2025**. DOI `10.3390/math13020298`. PDF verified (local Xeon MATLAB).  
3. **Year:** **PASS**  
4. **Relevance:** **MEDIUM** — CA2 names Sabir as the **shared-memory curve**; CA2 also requires a distributed/cloud curve Sabir does not provide.  
5. **Metrics overlap:** **YES** — completion time / scaling vs cores; CA2 adds peak memory + matched aggregate vCPU on EC2.  
6. **Gap→Problem:** **clear in CA2** (two disjoint curves; neither reports the other) / **weak in STATUS** (local Dask only).  
7. **CA2 alignment breakdown:** Scope 18/30 · Vars 20/25 · Method 14/20 · Metrics 22/25 → **74%**.  
8. **Issues:** Keep Sabir for threaded arm. To maximize CA2 %, add/pair **Kim/Son/Lee 2022** or **Dugré et al. 2023 (Dask)** as distributed baseline — CA2 already cites them.  
9. **MD quality:** **thin**

---

## 8. Nemi — Baseline→CA2 **90%**

1. **Topic (CA2):** SecureFL-IDS — FL + DP for cloud-native IDS vs centralized / prior FL (accuracy, privacy, comm, scalability).  
2. **Baseline:** Saklani, Chohan & Sharma — *Privacy Preserving Cloud Native Intrusion Detection Using Federated Learning and Differential Privacy* — ICISS **2026**, pp. 387–392. DOI `10.1109/iciss67859.2026.11454085`. **PDF missing**.  
3. **Year:** **PASS**  
4. **Relevance:** **HIGH** — CA2 names Saklani as primary PP-FL-DP-IDS baseline (~91.8% acc / F1>90%).  
5. **Metrics overlap:** **YES** — accuracy, F1, communication; CA2 also wants training time, CPU/mem, K8s deployment.  
6. **Gap→Problem:** **clear** — adaptive detection, comm optimisation, thorough cloud-native eval.  
7. **CA2 alignment breakdown:** Scope 28/30 · Vars 23/25 · Method 17/20 · Metrics 22/25 → **90%**.  
8. **Issues:** Keep. Obtain IEEE PDF. Li et al. 2026 HierFedDP is CA2’s second baseline (comm −49%) — optional dual baseline. Venue ICISS mid-tier.  
9. **MD quality:** **thin**

---

## 9. mehak-thesis — Baseline→CA2 **91%** *(proxy CA2)*

1. **Topic (CA2_COMMITMENTS):** Cross-head fusion vs strict one-head-per-metric MHSA underprediction on cluster telemetry.  
2. **Baseline:** Thapliyal — *A Multi-Head Attention Approach for SLA Compliance Monitoring in Data Centers* — arXiv:2605.05354 (PDF: accepted ICDCS 2026). PDF verified.  
3. **Year:** **PASS**  
4. **Relevance:** **HIGH** — commitments require reproducing Thapliyal architecture and confirming underprediction gap.  
5. **Metrics overlap:** **YES** — accuracy, macro-F1, transient recall, underprediction bias.  
6. **Gap→Problem:** **clear**.  
7. **CA2 alignment breakdown:** Scope 27/30 (colo SLA → cluster metrics adaptation) · Vars 24/25 · Method 18/20 · Metrics 22/25 → **91%**.  
8. **Issues:** Keep. Preprint until ICDCS VoR; domain shift colo→cluster is intentional and documented.  
9. **MD quality:** **thin**

---

## 10. pooja-thesis — Baseline→CA2 **87%** *(proxy CA2)*

1. **Topic:** Stability-aware proactive K8s autoscaling vs aggressive proactive vs reactive HPA.  
2. **Baseline:** Wanigasooriya & Ekanayake — *NimbusGuard… DQN* — ICOIN **2026**. DOI `10.1109/ICOIN68469.2026.11480646` / arXiv:2604.11017. PDF verified.  
3. **Year:** **PASS**  
4. **Relevance:** **HIGH** — commitments reproduce NimbusGuard agility–instability trade-off; build stability fix named as future work.  
5. **Metrics overlap:** **PARTIAL** — SLA / over-provisioning shared; scaling events & pod volatility are the stability emphasis.  
6. **Gap→Problem:** **clear**.  
7. **CA2 alignment breakdown:** Scope 28/30 · Vars 22/25 · Method 16/20 (MLP simulator vs DQN+LSTM+LLM testbed) · Metrics 21/25 → **87%**.  
8. **Issues:** Keep. Method simplification is intentional for reproducibility; cite NimbusGuard metrics honestly as reproduced trade-off, not identical agent.  
9. **MD quality:** **thin**

---

## 11. uday-thesis — Baseline→CA2 **90%** *(proxy CA2)*

1. **Topic:** Federated QoS offload for OneM2M recovering centralized RF accuracy without pooling telemetry.  
2. **Baseline:** Et-Tousy, Zyane & Sharif — *Adaptive QoS Management in OneM2M…* — JNSM **2026**. DOI `10.1007/s10922-026-10071-4`. Disk PDF = Research Square preprint with VoR note.  
3. **Year:** **PASS**  
4. **Relevance:** **HIGH** — commitments reproduce centralized RF; FL is paper’s own future work.  
5. **Metrics overlap:** **PARTIAL** — accuracy/F1 of offload class; paper also RTT/success/CPU/RAM.  
6. **Gap→Problem:** **clear**.  
7. **CA2 alignment breakdown:** Scope 28/30 · Vars 23/25 · Method 18/20 · Metrics 21/25 → **90%**.  
8. **Issues:** Keep. Prefer publisher PDF.  
9. **MD quality:** **thin**

---

## 12. vishvaksen-thesis — Baseline→CA2 **89%** *(proxy CA2)*

1. **Topic:** Hybrid rule+ML detector restoring precision when IaC comments removed.  
2. **Baseline:** War et al. — *Detection of Security Smells in IaC… Semantics-Aware…* — arXiv:2509.18790, Sep **2025**. PDF verified. Preprint.  
3. **Year:** **PASS**  
4. **Relevance:** **HIGH** — commitments reproduce comment-ablation precision collapse.  
5. **Metrics overlap:** **YES** — Precision/Recall/F1.  
6. **Gap→Problem:** **clear**.  
7. **CA2 alignment breakdown:** Scope 28/30 · Vars 23/25 · Method 16/20 (TF-IDF hybrid vs CodeBERT/LongFormer) · Metrics 22/25 → **89%**.  
8. **Issues:** Keep for CA2 gap. Venue risk: arXiv-only — add Rahman/GLITCH as published anchors without replacing War as operational baseline.  
9. **MD quality:** **thin**

---

## Special scrutiny (CA2 lens)

### Varun + TierBase
CA2 **does cite** TierBase, but also SkyStore/Yang, and evaluates against **S3 Lifecycle / Intelligent-Tiering + MAPE vs naive**. PDF proves KV-store scope. **Baseline→CA2 = 38%** — lowest of cohort. Maximizing CA2 alignment means **SkyStore or Yang as BASELINE_PAPER**, TierBase demoted.

### Yashaswini + Xing
CA2 **intentionally** uses Xing as ceiling (not same-rig). **72%** is correct for that role; replacing Xing with a “closer AWS paper” would **break** CA2’s three-leg design unless that paper is Leg-2 substrate (Pham/RCAEval).

### Rassool + Pantelić
CA2 alignment is **good by design** (retain latency/throughput; add meter). Medium relevance ≠ wrong baseline. **78%**.

### Preprint / venue / PDF integrity
| Thesis | Issue | Effect on CA2 % |
|--------|--------|-----------------|
| vikas | Wrong PDF attached | Integrity fail; citation choice still ~86% |
| Nemi | PDF absent | Claims second-hand |
| mehak | arXiv + ICDCS acceptance claim | Keep; prefer VoR |
| uday | Research Square PDF of JNSM VoR | Keep DOI |
| vishvaksen | arXiv-only | Highest venue risk; gap fit strong |
| pooja | ICOIN + arXiv OA | Acceptable |

---

## Actions that raise Baseline→CA2 % (priority)

1. **Varun:** Swap operational baseline to **SkyStore (Liu 2025)** or **Yang MLSys 2025**; keep Beck as forecast eval baseline.  
2. **vikas:** Replace Halfmoon PDF; delete arXiv:2306.10606 from MD.  
3. **venkat:** Document Sabir + distributed peer (Kim or Dugré) as paired baselines.  
4. **Nemi:** Add Saklani PDF; optionally dual-cite Li HierFedDP.  
5. **All 12:** Expand `BASELINE_PAPER.md` with Problem/Solution/Gap/Metrics mapped to **CA2 variables and eval table**.

---

## Evidence sources

CA2/proposal texts used:  
`Varun/VarunGampa_RIC_CA2.txt`, `Nemi/NemiIshwarlalVikani_24303046_CA2.txt`, `_handoff/venkat_ca2.txt`, `_analysis_extract/{chaitanya,yashaswini,rassool,vikas}_*proposal.txt`, `anji-thesis/anji_ca2_related_articles.html`, `{mehak,pooja,uday,vishvaksen}/CA2_COMMITMENTS.md` + intros.  

PDFs first-page verified for all except Nemi (absent) and Vikas (mismatch).
