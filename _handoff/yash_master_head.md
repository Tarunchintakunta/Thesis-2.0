# Claude Master Prompt — MSc Cloud Computing Research Project

**Student:** Yashaswini Penumarthi  
**Student ID:** 24262404  
**Programme:** MSc in Cloud Computing, National College of Ireland  
**Module:** Research Project (Level 9, 25 credits; weekly progress monitoring 12% + final submission 88%)  
**Title:** Lightweight Fault Detection and Localisation in AWS Serverless Microservices: Accuracy and Monitoring Overhead against Deep-Learning Baselines

**Role of this document:** Paste this entire file into Claude (or an equivalent coding/research agent) as the single master instruction. Claude must produce (1) a complete, runnable local codebase for the AWS serverless order-processing artefact, (2) a research-paper-style report (≤20 pages, NCI template sections), and (3) a separate configuration manual. Do not invent citations. Use only the verified bibliography below (or additional sources Claude itself verifies with DOI/URL before citing). Prefer Harvard referencing consistent with the proposal.

---

## 1. Research framing (do not dilute)

### Research question
What accuracy–overhead position does rule-based fault detection and localisation occupy relative to learned deep baselines in AWS serverless microservices?

### Problem
The highest published microservice detectors train deep models on large labelled telemetry corpora. A newly deployed, cost-constrained serverless service has no such corpus and no training-compute budget, so those methods are inapplicable—not merely expensive. How much accuracy a rule-based CloudWatch + X-Ray alternative forfeits, and what continuous monitoring costs in volume, latency and money, is unquantified when accuracy and overhead are never measured together on common terms.

### Niche (four conditions; prior work satisfies ≤2)
1. Evaluate an **untrained** detection/localisation method.  
2. Compare it against **learned baselines on common data**.  
3. Measure **localisation as well as detection**.  
4. Report **monitoring overhead** (telemetry volume, added latency, estimated cost).

### Contribution to deliver
A jointly reported accuracy–overhead position for rule-based detection/localisation in serverless microservices, plus a three-leg comparison protocol that makes an untrained method and a trained method legible to one another.

### Pre-committed, refutable expectations (state in Introduction; test in Evaluation)
- Rule-based arm concedes **≤10 percentage points of F1** vs the strongest reproducible baseline on common benchmark data.  
- Rule-based arm concedes **>10 points in top-3 localisation** accuracy.  
- Rule-based arm reduces **telemetry volume by ≥50%** relative to full tracing/logging under the stated sampling policy.  
Decision rule: competitive if F1 within 10 pp of strongest reproducible baseline **and** telemetry volume reduced by ≥ half.

### Scope limits (state early; never over-claim)
Single AWS account/region; one order-processing topology; synthetic traffic only; external validity does not extend to multi-provider or large heterogeneous estates. Multi-service topologies, online rule adaptation, hybrid rule+model detection, and cross-provider replication are future work.

---

## 2. Verified primary baseline and benchmark (DO NOT SWAP unless verification fails)

### Primary accuracy ceiling (citation arm — not same-rig)
**Xing, S., Wang, Y. and Liu, W. (2025)** ‘Multi-dimensional anomaly detection and fault localization in microservice architectures: a dual-channel deep learning approach with causal inference for intelligent sensing’, *Sensors*, 25(11), 3396.  
DOI: https://doi.org/10.3390/s25113396  

**Verified claims to cite exactly:** dual-channel TCN+VAE with contrastive learning and causal inference; semi-supervised evaluation; **detection F1-score 93.8%** (also report accuracy 95.4% and fault-component localisation precision 87.6% when discussing localisation). Use as the **published accuracy ceiling under ideal labelled-data conditions**, explicitly **not** a same-rig comparison.

### Comparison substrate (like-for-like arm)
**Pham, L., Zhang, H., Ha, H., Salim, F. and Zhang, X. (2025)** ‘RCAEval: a benchmark for root cause analysis of microservice systems with telemetry data’, in *Companion Proceedings of the ACM Web Conference 2025*. New York: ACM, pp. 777–780.  
DOI: https://doi.org/10.1145/3701716.3715290  
Code/data: https://github.com/phamquiluan/RCAEval  

**Verified facts:** 735 labelled failure cases; three microservice systems (Online Boutique, Sock Shop, Train Ticket); metrics + logs + traces; **15 reproducible baselines** (metric-based, trace-based, multi-source including TraceRCA-style and BARO/CIRCA-family methods); AC@k / Avg@k evaluation. **Confirmed real — use as the mandatory common-data arm.** Align injected fault taxonomy on the AWS artefact to RCAEval fault categories where possible.

### If Xing were ever unreachable (fallback instruction only)
Closest verified deep microservice detection+localisation alternative already in the bibliography: **Lee et al. (2023) Eadro** (joint detection+localisation, multi-source) or **Zhang, J. and Yang (2026)** (CPU-only spatiotemporal deep detection). Prefer Xing; do not invent a substitute F1.

---

## 3. Verified bibliography (≥20 sources, 2022–2026, with DOI/URL)

Claude must cite **at least 20** of the following (all verified). TraceRCA (2021) may be cited as the TraceRCA-style progenitor but **does not count** toward the 2022–2026 quota. Do not fabricate DOIs.

### Deep / learned microservice detection & localisation
1. Xing, Wang and Liu (2025) — Sensors — https://doi.org/10.3390/s25113396  
2. Zhang, J. and Yang, H. (2026) ‘CPU-only spatiotemporal anomaly detection in microservice systems via dynamic graph neural networks and LSTM’, *Symmetry*, 18(1), 87. — https://doi.org/10.3390/sym18010087  
3. Zhang, W., Yang, Z., Peng, F., Zhang, L., Chen, Y. and Chen, R. (2026) ‘GALR: graph-based root cause localization and LLM-assisted recovery for microservice systems’, *Electronics*, 15(1), 243. — https://doi.org/10.3390/electronics15010243  
4. Lee, C., Yang, T., Chen, Z., Su, Y. and Lyu, M.R. (2023) ‘Eadro: an end-to-end troubleshooting framework for microservices on multi-source data’, in *ICSE 2023*. — https://doi.org/10.1109/ICSE48619.2023.00150  
5. Zhang, C., Peng, X., Sha, C., Zhang, K., Fu, Z., Wu, X., Lin, Q. and Zhang, D. (2022) ‘DeepTraLog: trace-log combined microservice anomaly detection through graph-based deep learning’, in *ICSE 2022*. — https://doi.org/10.1145/3510003.3510180  

### TraceRCA-style / unsupervised / attribute & spectrum localisation
6. Zhang, C., Dong, Z., Peng, X., Zhang, B. and Chen, M. (2024) ‘Trace-based multi-dimensional root cause localization of performance issues in microservice systems’ (TraceContrast), in *ICSE 2024*. — https://doi.org/10.1145/3597503.3639088  
7. Yu, G. et al. (2023) ‘Nezha: interpretable fine-grained root causes analysis for microservices on multi-modal observability data’, in *ESEC/FSE 2023*. — https://doi.org/10.1145/3611643.3616249  
8. Pham, L., Ha, H. and Zhang, H. (2024) ‘BARO: robust root cause analysis for microservices via multivariate Bayesian online change point detection’, *Proceedings of the ACM on Software Engineering*, 1(FSE). — https://doi.org/10.1145/3660805  
9. Li, M. et al. (2022) ‘Causal inference-based root cause analysis for online service systems with intervention recognition’ (CIRCA), in *KDD 2022*. — https://doi.org/10.1145/3534678.3539041  
10. Xin, R., Chen, P. and Zhao, Z. (2023) ‘CausalRCA: causal inference based precise fine-grained root cause localization for microservice applications’, *Journal of Systems and Software*, 203, 111724. — https://doi.org/10.1016/j.jss.2023.111724  
11. Li, Z. et al. (2021) ‘Practical root cause localization for microservice systems via trace analysis’ (TraceRCA), in *IWQoS 2021*. — https://doi.org/10.1109/IWQOS52092.2021.9521340 *(foundational TraceRCA-style; cite for method lineage; outside 2022–2026 count)*  

### Threshold / training-less / statistical detectors
12. El Khairi, A., Caselli, M., Peter, A. and Continella, A. (2024) ‘ReplicaWatcher: training-less anomaly detection in containerized microservices’, in *NDSS 2024*. — https://doi.org/10.14722/ndss.2024.24286  
13. Liu, J., Yang, T., Chen, Z., Su, Y., Feng, C., Yang, Z. and Lyu, M.R. (2023) ‘Practical anomaly detection over multivariate monitoring metrics for online services’, in *ISSRE 2023*, pp. 36–45. — https://doi.org/10.1109/ISSRE59848.2023.00045  
14. Schmidl, S., Wenig, P. and Papenbrock, T. (2022) ‘Anomaly detection in time series: a comprehensive evaluation’, *Proceedings of the VLDB Endowment*, 15(9), pp. 1779–1797. — https://doi.org/10.14778/3538598.3538602  

### Benchmarks & datasets
15. Pham, L., Zhang, H., Ha, H., Salim, F. and Zhang, X. (2025) RCAEval — https://doi.org/10.1145/3701716.3715290 — https://github.com/phamquiluan/RCAEval  
16. Hardt, M. et al. (2024) ‘The PetShop dataset — finding causes of performance issues across microservices’, *Proceedings of Machine Learning Research*, 236, pp. 957–978. — https://proceedings.mlr.press/v236/hardt24a.html — https://github.com/amazon-science/petshop-root-cause-analysis  

### Monitoring overhead, sampling, serverless tracing (CloudWatch / X-Ray adjacent)
17. Huang, H. et al. (2024) ‘TraStrainer: adaptive sampling for distributed traces with system runtime state’, *Proceedings of the ACM on Software Engineering*, 1(FSE), pp. 473–493. — https://doi.org/10.1145/3643748  
18. Mertz, J. and Nunes, I. (2023) ‘Software runtime monitoring with adaptive sampling rate to collect representative samples of execution traces’, *Journal of Systems and Software*, 202, 111708. — https://doi.org/10.1016/j.jss.2023.111708  
19. Eder, C., Winzinger, S. and Lichtenthäler, R. (2023) ‘A comparison of distributed tracing tools in serverless applications’, in *IEEE SOSE 2023*, pp. 98–105. — https://doi.org/10.1109/SOSE58276.2023.00018  

### Official AWS primary sources (cite for CloudWatch metrics, X-Ray traces, pricing, sampling)
20. Amazon Web Services (n.d.) *Amazon CloudWatch User Guide* — https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/  
21. Amazon Web Services (n.d.) *AWS X-Ray Developer Guide* — https://docs.aws.amazon.com/xray/latest/devguide/  
22. Amazon Web Services (n.d.) *AWS Lambda Developer Guide* (tracing with X-Ray; CloudWatch Logs/Metrics) — https://docs.aws.amazon.com/lambda/latest/dg/  
23. Amazon Web Services (n.d.) *Amazon CloudWatch Pricing* — https://aws.amazon.com/cloudwatch/pricing/  
24. Amazon Web Services (n.d.) *AWS X-Ray Pricing* — https://aws.amazon.com/xray/pricing/  

**Coverage checklist for Literature Survey:** microservice RCA (items 1–11, 15–16); CloudWatch/X-Ray and serverless tracing overhead (19–24); threshold / training-less detectors (12–14); TraceRCA-style methods (6–11); monitoring overhead & sampling (17–18, 19).

---

## 4. What Claude must build (ICT artefact)

### 4.1 Order-processing serverless microservices (AWS)
Declare **all** infrastructure as code (AWS SAM or Terraform; prefer SAM + Python 3.11/3.12). Topology (minimum viable, research-honest):

| Component | Role |
|-----------|------|
| API Gateway HTTP API | Order create / get / cancel endpoints |
| Lambda `orders-api` | Validate + orchestrate |
| Lambda `inventory` | Stock check (invoked sync or async) |
| Lambda `payments` | Payment authorisation stub |
| Lambda `notifications` | Event notification stub |
| DynamoDB `Orders` table | Order state (on-demand billing) |
| CloudWatch Metrics + Logs | Per-function Errors, Duration, Throttles, Invocations; structured logs |
| AWS X-Ray | Active tracing on API Gateway + Lambdas; service map / trace segments |

