# MASTER PROMPT — Kasireddy Vadicharla (25104047)
## Source-Free Log Anomaly Detection for AWS Serverless Applications
### Fully executable local research project for Claude Code / Claude

**Output artefact this prompt produces:** complete MSc Cloud Computing Research Project portfolio (code, experiments, plots, research-paper-style report ≤20 pages, configuration manual, weekly activity logs scaffold).
**Execution mode:** local-first (LocalStack preferred; real AWS only if credentials and budget are explicitly available). Never invent citations. Never invent experimental numbers — run the pipeline.

---

## 1. Role & Mission

You are a senior research engineer and academic writing assistant acting as **Claude Code** for an NCI MSc in Cloud Computing Research Project. Your mission is to **fully execute** the project end-to-end on the local machine:

1. Scaffold reproducible infrastructure-as-code for a sample AWS serverless app (Lambda + API Gateway + DynamoDB), runnable on **LocalStack** (default) or real AWS.
2. Emit CloudWatch-compatible logs; parse them with a **fixed** Drain configuration (version pinned; never retuned between detector arms).
3. Implement **three detectors** on identical chronologically split traffic:
   - **D1 — Source-free one-class:** OC-SVM and/or Isolation Forest trained only on the application's own clean unlabelled logs.
   - **D2 — Transfer baseline (replicate):** Zhao et al. (2025) **ELFA-Log**-style cross-system detector (pseudo-labelling + feature alignment) using a labelled public Loghub corpus as source.
   - **D3 — Operational reference:** CloudWatch-style threshold alarms (error count / latency / throttle proxies).
4. Inject faults drawn from Xie et al. (2025) serverless fault distribution; evaluate F1 / precision / recall / elasticity false-alarm rate.
5. Produce plots, statistical tests, research-paper-style report, and configuration manual meeting the NCI Cloud Computing rubric.

**Non-negotiable principles**
- Web-verified citations only; if a paper cannot be verified, omit it or mark `[UNVERIFIED — do not cite]`.
- Chronological train→eval split (Le & Zhang, 2022). No random interleaving of future logs into training.
- Fix the parser once; report version and config hash.
- Certify a clean training window before source-free training (Albert, 2024 contamination warning).
- Report negative results honestly.
- Strip all request/account identifiers before analysis.

---

## 2. Student Identity

| Field | Value |
|---|---|
| Name | Kasireddy Vadicharla |
| Student ID | 25104047 |
| Programme | MSc in Cloud Computing |
| Institution | National College of Ireland (NCI) |
| Module | Research Project (Credit Level 9; Cloud Computing marking scheme) |
| Title | Source-Free Log Anomaly Detection for AWS Serverless Applications: Measuring the Accuracy Forfeited When No Labelled Source Exists |
| Keywords | log anomaly detection, serverless computing, source-free learning, AWS Lambda, observability |

All generated documents, README headers, report title page, and config manuals must carry this identity.

---

## 3. Rubric Mapping (NCI MSc Cloud Computing Research Project)

Use `master_rubric.md` and the Cloud Computing–specific scheme:

| Assessment | Weight | How this project satisfies it |
|---|---|---|
| Weekly progress monitoring | **12%** | Maintain `docs/weekly_activity/` with dated summaries of research activities each week (scaffolded templates + filled examples for the 12-week plan). |
| Project Final Submission | **88%** | Research-paper-style report (≤20 pages, NCI template sections), ICT artefact (code + models + results), Configuration Manual (separate), presentation/demo video scripts, examiner Q&A prep. |

**Learning outcomes to evidence explicitly in the report**
- **LO1** Analyse/select/implement research methods → controlled comparison, hypotheses, paired stats, power calculation.
- **LO2** Critically analyse state of the art → §5 literature synthesis (updated beyond RiC proposal; no copy-paste).
- **LO3** Architect/implement ICT solution → LocalStack serverless app, parsers, three detectors, fault injector.
- **LO4** Evaluate on identified measures → F1/P/R, delay, elasticity FAR; Holm–Bonferroni; CIs.
- **LO5** Future research / commercialisation → multi-service topologies, online adaptation, hybrid source-free+transfer.
- **LO6** Present/defend → viva script, demo script, artefact walkthrough.

**Report structure (mandatory sections, ≤20 pages)**
Abstract; Introduction; Literature Survey; Research Methodology; Design and Implementation Specifications; Evaluation (Results & Critical Analysis); Conclusions and Discussion; References. Separate Configuration Manual (not counted in page limit). Outputs Summary ≤2 pages if required by handbook.

**Ethics (Cloud Computing)**
- Scenario 2A (public secondary datasets — Loghub): cite licence/URL granting use.
- Scenario 3 (target systems): only researcher's own LocalStack/AWS account; no third-party systems.
- No human participants → Scenario 1 N/A. Complete Declaration of Ethics Consideration Form notes in `docs/ethics/`.

---

## 4. Research Question, Objectives, Hypotheses

### Research Question (RQ)
**How much detection accuracy (F1) does a source-free one-class detector forfeit, relative to a transfer-based detector supplied with a labelled public source (Zhao et al., 2025 ELFA-Log procedure), when both are evaluated on the same AWS serverless application's CloudWatch logs under faults injected from a published serverless fault distribution, and how do both compare to CloudWatch threshold alarms under benign elasticity?**

### Objectives
1. **O1 — Labelled evaluation workload:** Deploy instrumented serverless app; inject faults on a recorded schedule (permission denial, configuration error, dependency timeout, resource exhaustion) aligned to Xie et al. (2025).
2. **O2 — Source-free accuracy:** Train one-class detector(s) solely on certified-clean unlabelled app logs; measure P/R/F1 on injected anomalies.
3. **O3 — Transfer accuracy:** Replicate ELFA-Log-style pseudo-labelling + feature alignment from labelled Loghub source → unlabelled target; measure P/R/F1 on the **identical** injected intervals.
4. **O4 — Elasticity false alarms:** During a fault-free control period with cold starts and scale-up bursts, report false-alarm rate for all three approaches.

### Hypotheses (two-sided; α = 0.05; Holm–Bonferroni)
- **H1 (primary):** H0: F1(source-free) = F1(transfer); H1: F1(source-free) ≠ F1(transfer).
- **H2 (category coverage):** H0: F1 does not differ across the four fault categories within an approach; H1: at least one differs.
- **H3 (elasticity FAR):** H0: elasticity-induced false-alarm rate does not differ between approaches; H1: it differs.

### Decision rule (pre-registered)
Source-free is a **viable substitute** if it falls within **10 F1 points** of transfer **and** exceeds threshold alarms. Practical significance threshold = 10 F1 points. Target: 60 injections × 4 categories = **240** anomalous intervals (power for ~10-point paired F1 difference at 80%).

### Independent / dependent variables
- **IV:** Detection approach ∈ {source-free one-class, ELFA-Log-style transfer, CloudWatch thresholds}.
- **Conditioning factor:** Fault category ∈ {permission, config, timeout, resource exhaustion}.
- **DV (primary):** F1 against injected ground truth.
- **DV (secondary):** Precision, recall, detection delay, elasticity FAR.

---

## 5. Literature Review Synthesis + Verified Bibliography (≥20)

### 5.1 Synthesis (write into the report; expand beyond the RiC proposal — do not copy-paste)

**Baseline to replicate (STARRED)**  
★ **Zhao, X., Guo, K., Huang, M., Qiu, S. & Lu, L. (2025).** *ELFA-Log: Cross-System Log Anomaly Detection via Enhanced Pseudo-Labeling and Feature Alignment.* *Computers*, 14(7), 272. https://doi.org/10.3390/computers14070272  
Transfer via entropy-based high-confidence pseudo-labels + distance-based feature alignment. Removes need for **target** labels but still needs a **labelled source**. Authors note degradation on structurally divergent targets; evaluation on public benchmarks only. **This project's operational baseline:** implement the ELFA-Log procedure (or faithful re-implementation of pseudo-labelling + feature alignment) with Loghub as source and the serverless CloudWatch stream as target.

**Label cost & protocol sensitivity**  
Ali et al. (2025) show semi-supervised methods trail supervised by large F1 margins (and OC-SVM further); differences among semi-supervised families often non-significant — deficit is labels, not model family. Albert (2024) shows unsupervised heuristics can recover accuracy **if** training is clean; contamination collapses accuracy (~0.99 → ~0.03). Le & Zhang (2022) show chronological vs random splitting can halve F-measure — published numbers are often optimistic. Yu et al. (2024) show classical ML can match/beat deep models at far lower cost.

**Parsers & detectors**  
Drain (He et al., 2017) and Spell (Du & Li, 2016) are standard parsers; Zhu et al. (2019) benchmark many. Khan et al. (2024) find parsing accuracy weakly/negatively correlated with detection F1 — **fix the parser**. DeepLog (Du et al., 2017), LogAnomaly (Meng et al., 2019), LogBERT (Guo et al., 2021), LogRobust (Zhang et al., 2019), NeuralLog (Le & Zhang, 2021), LogGPT (Han et al., 2023), and Sun et al. (2026) LogRoBERTa span the deep sequence family. One-class baselines: OC-SVM (Schölkopf et al., 2001), Isolation Forest (Liu et al., 2008). PLELog (Yang et al., 2021) and FreeLog (Zhao, Jia et al., 2025) address limited/zero target labels; MetaLog (Zhang et al., 2024) uses meta-learning for cross-system generalisation.

**Serverless telemetry gap**  
Wen et al. (2023): only ~1.22% of serverless studies address testing/debugging. Nguyen et al. (2025): warm/cold latency swings (~37×) look like anomalies; ground-truth labels unobtainable by observation. Xie et al. (2025): 546 real serverless faults — Permission Denied most frequent symptom (~10.81%), Incorrect Code Logic leading root cause (~17.95%). Eismann et al. (2021) characterise serverless apps; Huang et al. (2024) FaaSRCA show multimodal RCA for FaaS. Loghub (Zhu et al., 2023) supplies labelled public corpora for the transfer source.

**Niche (justify RQ)**  
No prior study jointly: (a) trains with **no labelled source at all**, (b) on **serverless CloudWatch** telemetry, (c) against **injected known** faults, (d) with **ELFA-Log-style transfer** as comparator plus operational alarms. This project measures the **accuracy forfeited** when the labelled source transfer assumes does not exist.

### 5.2 Verified bibliography (use these; Harvard or IEEE per NCI template)

**2022–2026 (core; ≥20 including starred baseline)**

1. ★ Zhao, X., Guo, K., Huang, M., Qiu, S. and Lu, L. (2025) 'ELFA-Log: cross-system log anomaly detection via enhanced pseudo-labeling and feature alignment', *Computers*, 14(7), 272. https://doi.org/10.3390/computers14070272
2. Ali, S., Boufaied, C., Bianculli, D., Branco, P. and Briand, L. (2025) 'A comprehensive study of machine learning techniques for log-based anomaly detection', *Empirical Software Engineering*, 30(5), 129. https://doi.org/10.1007/s10664-025-10669-3
3. Albert, R.-G. (2024) 'System logs anomaly detection. Are we on the right path?', *Applied Artificial Intelligence*, 39(1), 2440692. https://doi.org/10.1080/08839514.2024.2440692
4. Khan, Z.A., Shin, D., Bianculli, D. and Briand, L.C. (2024) 'Impact of log parsing on deep learning-based anomaly detection', *Empirical Software Engineering*, 29(6), 139. https://doi.org/10.1007/s10664-024-10533-w
5. Le, V.-H. and Zhang, H. (2022) 'Log-based anomaly detection with deep learning: how far are we?', in *Proceedings of the 44th International Conference on Software Engineering*. New York: ACM, pp. 1356–1367. https://doi.org/10.1145/3510003.3510155
6. Nguyen, C., Elmroth, E. and Bhuyan, M. (2025) 'Silent failures in stateless systems: rethinking anomaly detection for serverless computing', in *Proceedings of the 2025 IEEE International Conference on Service-Oriented System Engineering*. Piscataway: IEEE, pp. 8–19. https://doi.org/10.1109/SOSE67019.2025.00006
7. Sun, Y., Keung, J., Yang, Z., Liu, S. and Yu, H.K. (2026) 'Improving anomaly detection in software logs through hybrid language modeling and reduced reliance on parser', *Automated Software Engineering*, 33(1), 12. https://doi.org/10.1007/s10515-025-00548-y
8. Wen, J., Chen, Z., Jin, X. and Liu, X. (2023) 'Rise of the planet of serverless computing: a systematic review', *ACM Transactions on Software Engineering and Methodology*, 32(5), Article 131. https://doi.org/10.1145/3579643
9. Xie, C., Zhang, Y., Mao, X., Yang, K. and Zhang, T. (2025) 'Understanding the faults in serverless computing based applications: an empirical study', in *Proceedings of the 2025 IEEE International Conference on Software Maintenance and Evolution*. Piscataway: IEEE, pp. 161–173. https://doi.org/10.1109/ICSME64153.2025.00024
10. Yu, B., Yao, J., Fu, Q., Zhong, Z., Xie, H., Wu, Y., Ma, Y. and He, P. (2024) 'Deep learning or classical machine learning? An empirical study on log-based anomaly detection', in *Proceedings of the IEEE/ACM 46th International Conference on Software Engineering*. New York: ACM, pp. 1–13. https://doi.org/10.1145/3597503.3623308
11. Zhang, C., Jia, T., Shen, G., Zhu, P. and Li, Y. (2024) 'MetaLog: generalizable cross-system anomaly detection from logs with meta-learning', in *Proceedings of the IEEE/ACM 46th International Conference on Software Engineering*. New York: ACM, Article 154. https://doi.org/10.1145/3597503.3639205
12. Zhao, X., Jia, T., He, M., Wu, Y., Li, Y. and Huang, G. (2025) 'From few-label to zero-label: an approach for cross-system log-based anomaly detection with meta-learning', in *Proceedings of the ACM International Conference on the Foundations of Software Engineering (FSE Companion / Ideas, Visions and Reflections)*. New York: ACM. https://doi.org/10.1145/3696630.3728519
13. Zhu, J., He, S., He, P., Liu, J. and Lyu, M.R. (2023) 'Loghub: a large collection of system log datasets for AI-driven log analytics', in *Proceedings of the 2023 IEEE International Symposium on Software Reliability Engineering (ISSRE)*. Piscataway: IEEE. https://doi.org/10.1109/ISSRE59848.2023.00071
14. Huang, J., Chen, P., Yu, G., Wang, Y., Huang, H. and He, Z. (2024) 'FaaSRCA: full lifecycle root cause analysis for serverless applications', in *Proceedings of the 2024 IEEE International Symposium on Software Reliability Engineering (ISSRE)*. Piscataway: IEEE, pp. 415–426. https://doi.org/10.1109/ISSRE62328.2024.00047
15. Han, X., Yuan, S. and Trabelsi, M. (2023) 'LogGPT: log anomaly detection via GPT', in *Proceedings of the 2023 IEEE International Conference on Big Data (BigData)*. Piscataway: IEEE. https://doi.org/10.1109/BigData59044.2023.10386543
16. Eismann, S., Scheuner, J., van Eyk, E., Schwinger, M., Grohmann, J., Herbst, N., Abad, C.L. and Iosup, A. (2021) 'The state of serverless applications: collection, characterization, and community consensus', *IEEE Transactions on Software Engineering*, 48(10), pp. 4152–4166. https://doi.org/10.1109/TSE.2021.3113940

**Foundational (required coverage — parsers / detector families / one-class)**

17. He, P., Zhu, J., Zheng, Z. and Lyu, M.R. (2017) 'Drain: an online log parsing approach with fixed depth tree', in *Proceedings of the 2017 IEEE International Conference on Web Services (ICWS)*. Piscataway: IEEE, pp. 33–40. https://doi.org/10.1109/ICWS.2017.13
18. Du, M. and Li, F. (2016) 'Spell: streaming parsing of system event logs', in *Proceedings of the 2016 IEEE International Conference on Data Mining (ICDM)*. Piscataway: IEEE, pp. 859–864. https://doi.org/10.1109/ICDM.2016.0103
19. Du, M., Li, F., Zheng, G. and Srikumar, V. (2017) 'DeepLog: anomaly detection and diagnosis from system logs through deep learning', in *Proceedings of the 2017 ACM SIGSAC Conference on Computer and Communications Security*. New York: ACM, pp. 1285–1298. https://doi.org/10.1145/3133956.3134015
20. Meng, W., Liu, Y., Zhu, Y., Zhang, S., Pei, D., Liu, Y., Chen, Y., Zhang, R., Tao, S., Sun, P. and Zhou, R. (2019) 'LogAnomaly: unsupervised detection of sequential and quantitative anomalies in unstructured logs', in *Proceedings of the Twenty-Eighth International Joint Conference on Artificial Intelligence (IJCAI)*. pp. 4739–4745. https://doi.org/10.24963/ijcai.2019/658
21. Guo, H., Yuan, S. and Wu, X. (2021) 'LogBERT: log anomaly detection via BERT', in *Proceedings of the 2021 International Joint Conference on Neural Networks (IJCNN)*. Piscataway: IEEE. https://doi.org/10.1109/IJCNN52387.2021.9534113
22. Zhang, X., Xu, Y., Lin, Q., Qiao, B., Zhang, H., Dang, Y., Xie, C., Yang, X., Cheng, Q., Li, Z., Chen, J., He, X., Yao, R., Lou, J.-G., Chintalapati, M., Shen, F. and Zhang, D. (2019) 'Robust log-based anomaly detection on unstable log data', in *Proceedings of the 2019 27th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering (ESEC/FSE)*. New York: ACM, pp. 807–817. https://doi.org/10.1145/3338906.3338931
23. Le, V.-H. and Zhang, H. (2021) 'Log-based anomaly detection without log parsing', in *Proceedings of the 2021 36th IEEE/ACM International Conference on Automated Software Engineering (ASE)*. Piscataway: IEEE, pp. 492–504. https://doi.org/10.1109/ASE51524.2021.9678773
24. Zhu, J., He, S., Liu, J., He, P., Xie, Q., Zheng, Z. and Lyu, M.R. (2019) 'Tools and benchmarks for automated log parsing', in *Proceedings of the 2019 IEEE/ACM 41st International Conference on Software Engineering: Software Engineering in Practice (ICSE-SEIP)*. Piscataway: IEEE, pp. 121–130. https://doi.org/10.1109/ICSE-SEIP.2019.00021
25. Yang, L., Chen, J., Wang, Z., Wang, W., Jiang, J., Dong, X. and Zhang, W. (2021) 'Semi-supervised log-based anomaly detection via probabilistic label estimation', in *Proceedings of the 43rd International Conference on Software Engineering (ICSE)*. Piscataway: IEEE, pp. 1448–1460. https://doi.org/10.1109/ICSE43902.2021.00130
26. Liu, F.T., Ting, K.M. and Zhou, Z.-H. (2008) 'Isolation forest', in *Proceedings of the 2008 Eighth IEEE International Conference on Data Mining*. Piscataway: IEEE, pp. 413–422. https://doi.org/10.1109/ICDM.2008.17
27. Schölkopf, B., Platt, J.C., Shawe-Taylor, J., Smola, A.J. and Williamson, R.C. (2001) 'Estimating the support of a high-dimensional distribution', *Neural Computation*, 13(7), pp. 1443–1471. https://doi.org/10.1162/089976601750264965

**Baseline status:** Zhao et al. (2025) ELFA-Log **verified via DOI 10.3390/computers14070272** — use as operational baseline. **No replacement required.** Closest related zero-label comparator for discussion: FreeLog (Zhao, Jia et al., 2025).

---

## 6. Local Code Plan (Artefact Architecture)

### 6.1 Repository layout
```
thesis-2.0/
  KasireddyVadicharla_25104047/
    README.md
    pyproject.toml / requirements.txt
    configs/
      drain.yaml                 # FIXED parser config + version pin
      detectors.yaml             # OC-SVM, IForest, ELFA-Log hyperparams
      alarms.yaml                # threshold definitions
      experiment.yaml            # seeds, windows, injection schedule
    infra/
      terraform/ or serverless.yml / CDK / SAM
      localstack/docker-compose.yml
      lambda_app/                # sample Order/API CRUD service
        handler.py
        template.yaml
    src/
      collect/                   # pull/simulate CloudWatch logs
      parse/                     # Drain (primary), Spell (ablation only if time)
      features/                  # template sequences, count vectors, TF-IDF/semantic
      detectors/
        oneclass_ocsvm.py
        oneclass_iforest.py
        transfer_elfa.py         # pseudo-label + feature alignment
        thresholds.py
      inject/                    # fault injector (4 categories)
      eval/                      # metrics, stats, plots
      pipeline.py                # end-to-end orchestration
    data/
      raw/  interim/  processed/  external/loghub/
    results/
      metrics/  figures/  tables/  stats/
    docs/
      report/                    # research paper style report
      config_manual/
      weekly_activity/
      ethics/
      viva/
    scripts/
      00_bootstrap.sh
      01_deploy_app.sh
      02_generate_traffic.sh
      03_inject_faults.sh
      04_train_eval.sh
      05_stats_plots.sh
      06_build_report.sh
```

### 6.2 Sample serverless application
- **API Gateway** HTTP API → **Lambda** (Python 3.11) → **DynamoDB** single-table (orders/items).
- Structured JSON logs: `request_id`, `route`, `status`, `latency_ms`, `cold_start`, `error_type`, `memory_mb`, `downstream_ms`.
- LocalStack via Docker Compose; IAM role simulated; CloudWatch Logs group `/aws/lambda/kasireddy-orders`.
- Workload generator: Locust or custom asyncio client with diurnal pattern + burst scale-ups to induce **benign elasticity** (cold starts).

### 6.3 Parser (fixed)
- Primary: **Drain** (drain3 or logparser Drain) — pin version in `requirements.txt` and `configs/drain.yaml` (`depth`, `st`, `max_child`, `sim`).
- Record config SHA256; **never** change between D1/D2/D3.
- Optional mention of Spell in lit review; do not switch parsers mid-experiment (Khan et al., 2024).

### 6.4 Three detectors
| ID | Name | Training data | Method |
|---|---|---|---|
| D1 | Source-free one-class | Clean target window only | OC-SVM (RBF) + Isolation Forest; report both, primary = better on validation slice carved from clean window chronologically |
| D2 | Transfer (ELFA-Log-style) | Labelled Loghub source (e.g. HDFS or BGL) + unlabelled target | Train source encoder/classifier; entropy-based high-confidence pseudo-labels on target; distance-based feature alignment loss; evaluate on target injected intervals |
| D3 | Threshold alarms | None (rules) | Error-rate, p99 latency, throttle/timeout count thresholds calibrated on clean window percentiles (e.g. 99th) |

### 6.5 Fault injection (Xie et al., 2025-aligned)
| Category | Injection mechanism (LocalStack/AWS) |
|---|---|
| Permission denial | Remove DynamoDB action from Lambda execution role / deny policy |
| Configuration error | Point env var `TABLE_NAME` to wrong/nonexistent table |
| Dependency timeout | Proxy/throttle DynamoDB responses; inject sleep/timeout in stub |
| Resource exhaustion | Lower Lambda memory (e.g. 128MB) below working set; force OOM/slow paths |

Schedule: 60 injections × 4 categories = 240 anomalous intervals; each with recorded `[t_start, t_end]` ground-truth. Interleave with normal traffic. Separate **fault-free control period** for elasticity FAR.

### 6.6 Train / eval protocol
1. Collect Phase A: clean traffic → certify no injected faults → train D1.
2. Chronological split only (Le & Zhang, 2022): all training timestamps < all evaluation timestamps.
3. Collect Phase B: mixed normal + scheduled injections → evaluate D1, D2, D3 on identical windows.
4. Collect Phase C: fault-free elasticity bursts → FAR.
5. Metrics: Precision, Recall, F1, detection delay; per-category and micro/macro; 95% CIs.
6. Stats: Shapiro–Wilk → paired t-test + Cohen's d **or** Wilcoxon + rank-biserial; McNemar for category pairs; Holm–Bonferroni.

### 6.7 Metrics under elasticity
Tag each false positive in Phase C with `cold_start=true` or `scale_burst=true` when applicable; report FAR_elasticity = FP_elasticity / windows_control.

---

## 7. Step-by-Step Claude Commands (Execute in Order)

Copy/paste these as sequential Claude Code tasks. Do not skip gates.

### Phase 0 — Bootstrap
```
Create the repository layout under /workspace/thesis-2.0/KasireddyVadicharla_25104047/
exactly as §6.1. Write README with student identity, RQ, and how to run LocalStack.
Pin Python 3.11, create requirements.txt with: boto3, localstack, drain3, scikit-learn,
numpy, pandas, scipy, matplotlib, seaborn, pyyaml, torch (if needed for ELFA-Log encoder),
statsmodels, jinja2. Add .gitignore for data/raw and secrets. NEVER commit AWS keys.
```

### Phase 1 — Infra + sample app
```
Implement infra/lambda_app: Python Lambda CRUD against DynamoDB, API Gateway routes
POST/GET /orders. Provide docker-compose for LocalStack (services: localstack).
Script scripts/01_deploy_app.sh to create table, function, API, log group.
Log every invocation as JSON to stdout (CloudWatch-compatible). Unit-test handler locally.
```

### Phase 2 — Traffic + log collection
```
Implement workload generator with warm steady state, cold-start bursts, and scale-up spikes.
Implement src/collect to pull logs from LocalStack CloudWatch or capture container logs.
Strip identifiers. Save to data/raw/ with UTC timestamps. Document in config manual.
```

### Phase 3 — Fixed Drain parser
```
Implement src/parse with Drain config from configs/drain.yaml. Persist templates and
structured sequences to data/processed/. Write config hash to results/parser_fingerprint.json.
Do not tune depth/st after fingerprint is written.
```

### Phase 4 — Fault injector
```
Implement src/inject for the four Xie-aligned categories with a YAML schedule
(configs/experiment.yaml). Record ground-truth intervals to data/processed/ground_truth.csv.
Ensure injections are reproducible via seed.
```

### Phase 5 — Detector D1 (source-free)
```
Implement OC-SVM and Isolation Forest on event-count / TF-IDF template features from the
certified-clean window only. Chronological holdout inside clean window for threshold/nu.
Persist models under results/models/d1/.
```

### Phase 6 — Detector D2 (ELFA-Log-style transfer) ★
```
Download Loghub sample (HDFS or BGL) into data/external/loghub/ under its licence.
Implement transfer_elfa.py: (1) train on labelled source features; (2) generate entropy-based
high-confidence pseudo-labels on unlabelled target; (3) feature-alignment / distance loss
between source and target embeddings; (4) classify target evaluation windows.
Document any simplifications vs Zhao et al. (2025) honestly in the report (faithful operational
replication, not claim of official code identity unless upstream code is used).
```

### Phase 7 — Detector D3 (thresholds)
```
Implement CloudWatch-like alarms: error count rate, latency p99, timeout count. Calibrate
thresholds on clean-window percentiles only. Evaluate on same intervals as D1/D2.
```

### Phase 8 — End-to-end experiment
```
Run scripts/04_train_eval.sh: Phase A clean train → Phase B inject+eval → Phase C elasticity.
Produce results/metrics/{d1,d2,d3}.csv and a combined results/metrics/summary.csv with
P, R, F1, delay, FAR_elasticity per approach and fault category.
```

### Phase 9 — Statistics & plots
```
Run src/eval stats: normality, paired tests, effect sizes, Holm–Bonferroni, 95% CIs.
Plots (matplotlib/seaborn, colour-blind safe): (1) F1 bar chart D1 vs D2 vs D3;
(2) per-category F1 grouped bars; (3) PR curves if scores available; (4) elasticity FAR;
(5) detection delay boxplots. Save to results/figures/. Export LaTeX/Markdown tables.
```

### Phase 10 — Report + config manual + weekly logs
```
Write docs/report/main.md (or .tex) following NCI sections; ≤20 pages equivalent;
update literature substantially beyond proposal; map results to H1–H3 and decision rule;
state limitations (single app, synthetic injections, LocalStack fidelity).
Write docs/config_manual/CONFIG_MANUAL.md: environment, LocalStack, deploy, run, reproduce seeds.
Scaffold 12 weekly activity reports under docs/weekly_activity/.
Write docs/viva/presentation_script.md and demo_script.md (10 min + 5–10 min).
Write docs/ethics/ETHICS_NOTES.md (Scenario 2A + own account Scenario 3).
```

### Phase 11 — Quality gate before "done"
```
Verify: (a) parser fingerprint unchanged across arms; (b) chronological split asserted in code;
(c) clean-window certification logged; (d) all DOIs in report match §5.2; (e) no fabricated metrics;
(f) README run instructions succeed from clean clone with LocalStack; (g) last line of this
prompt respected in student-facing docs authorship.
```

---

## 8. Deliverables Checklist

- [ ] ICT artefact: LocalStack serverless app + parsers + D1/D2/D3 + fault injector + pipeline
- [ ] `results/metrics/summary.csv` + statistical test outputs
- [ ] `results/figures/` publication-ready plots
- [ ] Research-paper-style report (≤20 pages) with mandatory sections
- [ ] Configuration Manual (separate)
- [ ] Weekly activity report templates (12) + filled examples aligned to plan
- [ ] Ethics notes (Loghub licence citation; own-account only)
- [ ] Presentation script (10 min) + Demo script (5–10 min)
- [ ] Examiner Q&A prep (methods, threats to validity, why Drain fixed, why chronological)
- [ ] `requirements.txt` / lockfile + seeds + parser fingerprint
- [ ] README with one-command reproduce path
- [ ] Explicit statement of F1 gap (transfer − source-free) and decision-rule outcome

---

## 9. Quality & Ethics Gates

1. **Citations:** Only §5.2 entries (or newly WebSearch-verified DOIs). Never invent papers.
2. **Baseline fidelity:** Document ELFA-Log replication steps and deviations; star Zhao et al. (2025) in lit review table.
3. **No peeking:** Freeze D1 training window before seeing Phase B outcomes.
4. **Honest negatives:** If source-free collapses under contamination or elasticity, that **is** the finding.
5. **Privacy:** Synthetic traffic only; strip IDs; no production customer data.
6. **Platform ToS:** Faults only in researcher's LocalStack/own AWS account; stay within free-tier-safe rates if using real AWS.
7. **Reproducibility:** Seeds, container tags, config hashes, and ground-truth CSV released with artefact.
8. **Rubric alignment:** Weekly 12% evidence trail; final 88% package complete.
9. **Page discipline:** Report ≤20 pages; put runbooks in Configuration Manual.
10. **Stop condition:** Do not claim "state-of-the-art detector"; claim a **measured forfeiture price** on serverless telemetry.

---

## 10. Closing Directive

Execute Phases 0–11 autonomously. Prefer LocalStack. Prefer scikit-learn one-class models for D1 speed; keep D2 as faithful ELFA-Log-style transfer. Measure the accuracy forfeited when no labelled source exists. Ship the portfolio for Kasireddy Vadicharla, 25104047, MSc Cloud Computing, National College of Ireland.

Kasireddy Vadicharla
