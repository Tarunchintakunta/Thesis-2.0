# Yashaswini Thesis Traceability Report (yashaswini-thesis ONLY)

**Scope:** `yashaswini-thesis/` + CA2 extract `_analysis_extract/yashaswini-thesis__YashaswiniPenumarthi_24262404_proposal.txt` only.  
**Do not mix with kasi-thesis or any other thesis.**  
**Alignment:** **62/100**

Sources used (verified in-tree):
- CA2: `_analysis_extract/yashaswini-thesis__YashaswiniPenumarthi_24262404_proposal.txt`
- STATUS: `yashaswini-thesis/serverless-fault-localisation/STATUS.md`
- Artefact: `yashaswini-thesis/serverless-fault-localisation/`
- Results: `results/sim/` (CSV + `summary.md`); `results/rcaeval/raw/{rules,baro,circa,tracerca,hybrid,causalrca}/`
- LaTeX: `yashaswini-thesis/latex_report/text/{abstract,introduction,methodology,design,implementation,evaluation,conclusion,relatedwork}.tex`
- Compiled PDF: `yashaswini-thesis/latex_report/projectReport.pdf` (**12 pages**)
- Bib: `latex_report/refs.bib` (4 entries, all `doi=`); `serverless-fault-localisation/bib/references.bib` (24 entries, 18 `doi=`, **0** `note = {doi: ...}`)
- Config manuals: `docs/CONFIGURATION_MANUAL.md`, `yashaswini_configuration_manual.md`
- Short MD report: `yashaswini_final_report.md`
- Baseline PDF: `baseline_papers/Xing_et_al_2025_Sensors_fault_localisation_baseline.pdf` (PRESENT)
- WhatsApp DOI rule: Moodle “DOI LATEX” — require `note = {doi: ...}` in bib fields (screenshot `WhatsApp Image 2026-09-20 at 12.19.52.jpeg`)
- Cloud Computing rubric (WhatsApp / MScCC-Marking Rubric): Spec 5%, Lit 8%, Artefact 27%, Eval 25%, Report 8%, Config Manual 5%, Viva 10% (+ weekly 12% outside final 88%)

**Independent recompute (this audit):** `python -m eval.leg2 --raw results/rcaeval/raw` → AC@k below. No committed `results/rcaeval/summary.md` in tree (only `raw/`).

---

## A. Identification

| Field | Value | Status |
|---|---|---|
| Student | Yashaswini Penumarthi | Verified (CA2, STATUS, titlepage, summary signatures) |
| Student ID | 24262404 | Verified |
| Programme | MSc Cloud Computing, NCI | Verified (CA2; `\mystream` / STATUS) |
| Title | Lightweight Fault Detection and Localisation in AWS Serverless Microservices: Accuracy and Monitoring Overhead against Deep-Learning Baselines | Matches CA2 / STATUS / intro |
| Baseline | Xing et al. (2025), Sensors 25(11), 3396; DOI 10.3390/s25113396 | PDF present; bib uses `doi=` not WhatsApp `note={doi:}` |
| Artefact root | `yashaswini-thesis/serverless-fault-localisation/` | Present |
| Cloud platform | **AWS serverless (required by CA2)** | SAM/template present; **no live AWS campaign** (STATUS) |
| CA2 | `_analysis_extract/yashaswini-thesis__YashaswiniPenumarthi_24262404_proposal.txt` | Present |

### AWS classification

**AWS_CLASS = required**

CA2 states the system under test is “API Gateway endpoint, serverless functions and a managed table,” Leg 3 overhead “on the researcher's own AWS service,” and “Five managed services carry the experiment: Lambda, API Gateway, DynamoDB, CloudWatch and X-Ray.” The research question is explicitly scoped to **AWS serverless microservices**. Offline RCAEval alone cannot satisfy the CA2 overhead objective.

#### Services inventory (evidence-only)

| Service | Class | Evidence |
|---|---|---|
| AWS Lambda | **Required** | CA2; 4× `AWS::Serverless::Function` in `template.yaml` |
| Amazon API Gateway | **Required** | CA2; `AWS::Serverless::Api` (REST; tests assert not HTTP API for X-Ray) |
| Amazon DynamoDB | **Required** | CA2; `AWS::DynamoDB::Table` |
| Amazon CloudWatch (metrics) | **Required** | CA2 rule arm (Errors/Duration/Throttles); collector scripts |
| Amazon CloudWatch Logs | **Required** | CA2 overhead (log volume); 4× `AWS::Logs::LogGroup` |
| AWS X-Ray | **Required** | CA2 localisation + overhead; tracing + `AWS::XRay::SamplingRule` |
| AWS Systems Manager Parameter Store | **Relevant** | Fault switch `AWS::SSM::Parameter`; injector path |
| AWS SAM / CloudFormation | **Relevant** | `template.yaml`; deploy path in config manual |
| Amazon S3 | **Relevant** | Config manual: packaging bucket for `sam deploy` |
| AWS IAM | **Relevant** | Function policies / deploy roles (config manual) |
| AWS Budgets | **Relevant (optional)** | `AWS::Budgets::Budget` in template |
| AWS Lambda Layer | **Relevant** | `AWS::Serverless::LayerVersion` (`faultlab` obs/fault helpers) |
| EC2 / ECS / EKS / Fargate | **Not** | Not in CA2 or template |
| RDS / Aurora | **Not** | Not used |
| SQS / SNS / EventBridge / Step Functions / Kinesis | **Not** | Not in CA2 experiment set |
| HTTP API (API Gateway v2) | **Not** | MD report claims “HTTP API”; template uses **REST** `AWS::Serverless::Api` only |

---

## B. Research Question (RQ /10)

**CA2 RQ:**

> what accuracy-overhead position does rule-based fault detection and localisation occupy relative to learned baselines in serverless microservices?

**Report RQ** (`latex_report/text/introduction.tex`):

> What accuracy-overhead position does rule-based fault detection and localisation occupy relative to learned deep baselines in AWS serverless microservices?

| Check | Result |
|---|---|
| CA2 RQ precise & answerable | Pass — joint accuracy–overhead position vs learned baselines |
| Report mirrors CA2 | Pass — AWS scope made explicit |
| Answered with joint metrics | Partial — RCAEval localisation/detection raw exist; Leg 3 live overhead **absent** |
| Answer honesty | Fail — LaTeX/`yashaswini_final_report.md` assert competitiveness with numbers that **do not match** `results/rcaeval/raw` (see §I) |

**Score: RQ 7/10** — clear, CA2-faithful question; end-state answer is incomplete (no live AWS overhead) and numerically unreliable in the written reports.

---

## C. Objectives (Obj /15)

**CA2 four objectives** (Introduction):

| # | CA2 objective | Delivery | Evidence |
|---|---|---|---|
| 1 | Detection accuracy: precision, recall, F1, detection delay | Partial | Sim: `results/sim/` F1≈0.97 (labeled NOT AWS). RCAEval rule detection via `eval.leg2`: **F1=0.469** (tp=90, fp=204, fn=0) — **not** the ~0.85 / “within 10 pp of Xing 0.938” claimed in LaTeX/MD |
| 2 | Localisation: top-k + mean rank | Partial | Raw 90-case JSONs present; project aggregator → rules AC@3=**0.611**, mean rank **2.98**. LaTeX table claims 0.822 / 1.89 — **contradicted** |
| 3 | Monitoring overhead: volume, latency, cost | Not attained as CA2 specifies | STATUS: no live deploy. LaTeX §overhead presents calculated/sim estimates; MD report presents them as AWS campaign outcomes |
| 4 | Position vs learned baselines on common data | Partial | Leg 1: Xing cited. Leg 2: baro/circa/tracerca/hybrid **90** cases; **causalrca only 4**. Strongest AC@3 baselines ≈0.878; rules gap **26.7 pp** (expectation “>10 pp concession” supported by data, misstated in LaTeX as ~11 pp / inconclusive) |

Intro also adds hybrid Isolation-Forest design + three-leg protocol + decision rule — implemented in code; decision-rule “competitive” claim fails against recomputed detection F1 and localisation gap.

**Score: Obj 9/15** — objectives well specified; Obj1–2 evidence present but misreported; Obj3 live AWS unmet; Obj4 incomplete (CausalRCA) and distorted in write-up.

---

## D. Methodology (Method /15)

Aligned with CA2:
- Two-arm / three-leg protocol (ceiling citation; RCAEval like-for-like; AWS overhead)
- IVs: method, fault type (4), load (steady / 5× peak)
- Rule arm: 3σ + frozen P99; localisation via failed-trace share + depth
- Calibration freeze + SHA-256 (`results/sim/thresholds.json`; STATUS)
- Stats plan coded (`eval/stats.py`: Welch/Mann–Whitney, McNemar, Holm–Bonferroni)
- Ethics: synthetic data; own-account injection (docs/ETHICS.md)

Gaps vs CA2 method:
- CA2 power plan: **60 injections × 4 fault types** per arm; sim campaign uses **48** total (4×2×6)
- 24 h live calibration **not run**
- LaTeX reports Welch t / Cohen’s d on overhead latency without live traces
- RCAEval CausalRCA subset (4) documented by aggregator as fixed-ranking risk when complete

**Score: Method 12/15**

---

## E. Implementation / Artefact (Impl /15)

Verified under `serverless-fault-localisation/`:
- IaC: `template.yaml` (Lambda×4, API, DynamoDB, SSM, LogGroups, X-Ray sampling, Budgets)
- Handlers + layer: `src/{orders_api,inventory,payments,notifications}/`, `src/layer/faultlab/`
- Detector/ranker: `detector/rules.py`, `detector/ranker.py`
- Injector + campaigns: `injector/`, `scripts/campaign.py`, `scripts/collect_telemetry.py`, `scripts/collect_overhead.py`
- RCAEval arms: `baseline_runner/{rule_arm,hybrid_arm,run_baselines}.py`
- Eval: `eval/{rig,leg2,metrics,stats,overhead}.py`
- Tests: **76** `test_*` functions (STATUS claim matches count)
- Config manual: present (docs + root copy)
- Sim harness: `sim/telemetry.py`

Not verified:
- Live stack / `results/live/` (absent; SCHEMA documents intended path)
- Viva / filled weekly reports (only `weekly/WEEK_TEMPLATE.md`)

**Score: Impl 12/15** — strong deployable artefact + tests + manuals; −3 for never-executed live path that CA2 Leg 3 requires.

---

## F. Experiments (Exp /15)

| Arm | Mode | Evidence path | Role vs RQ |
|---|---|---|---|
| Sim rig (rule) | Synthetic CW/X-Ray | `results/sim/*` | Pipeline check only (summary labels **NOT AWS data**) |
| RCAEval rules | Offline RE2-OB | `results/rcaeval/raw/rules/` (90) | Like-for-like detection+localisation |
| RCAEval hybrid | Offline | `raw/hybrid/` (90) | Extra IF arm (intro Obj); **worse** AC@3 than rules |
| BARO / CIRCA / TraceRCA | Offline | 90 each | Baselines |
| CausalRCA | Offline | **4** only | Incomplete vs STATUS “5 baseline methods across 90” |
| Xing ceiling | Citation | Lit / Leg 1 text | Not same-rig |
| Live AWS calibration/campaign/overhead | **Not run** | No `results/live/` | CA2 Leg 3 unmet |

**Score: Exp 8/15** — meaningful offline Leg 2 raw + honest sim leg; incomplete CausalRCA; zero live Leg 3.

---

## G. Metrics (Metrics /10)

CA2-aligned metric families are implemented:
- Detection: P/R/F1, delay median/P95
- Localisation: AC@1/AC@3, mean rank, Avg@5
- Overhead: volume, latency percentiles, cost estimate
- Competitiveness thresholds: ≤10 pp F1; >10 pp Top-3 concession; ≥50% telemetry cut

Recomputed RCAEval detection (rule arm): F1 **0.469**, precision **0.306**, recall **1.0**, delay median **20.5 s**.  
Recomputed localisation gap vs strongest AC@3 baselines (BARO/CIRCA **0.878**): **26.7 pp** concession (expectation of >10 pp **supported** by data).

**Score: Metrics 7/10** — right instruments; written reports substitute unsupported F1≈0.85 and wrong AC@k tables.

---

## H. Evidence (Evidence /10)

| Evidence class | Verdict |
|---|---|
| Sim CSV + summary | Present; numbers match LaTeX sim tables; provenance honest |
| RCAEval raw JSON | Present (454 files under `raw/`); **no committed aggregated summary** |
| `eval.leg2` recompute | Contradicts LaTeX Table `tab:rcaeval_comparison` and MD “~82% Top-3 / ~84.5% F1” |
| Live AWS results | **Absent** (`results/live/` missing; STATUS explicit) |
| WhatsApp DOI `note = {doi: ...}` | **FAIL — 0** in both bibs (`doi=` only) |
| Compiled PDF | **12 pages**; handbook target up to ~20; `refs.bib` only **4** keys while `bibliography{refs}` |
| Config manual | Present and actionable |
| Baseline PDF | PRESENT |
| pytest suite | 76 tests in tree (not re-executed here) |
| Weekly / viva | Template only / not present |

**Score: Evidence 4/10** — strong raw artefacts; weak report packaging; DOI-note fail; Leg 3 missing; Leg 2 write-up diverges from raw.

---

## I. Claims / Honesty (Claims /5)

**Honest (verified):**
- STATUS clearly states no live AWS; sim labeled “NOT AWS data”
- `evaluation.tex` opening sections disclose sim vs RCAEval vs live-needed overhead
- `results/sim/summary.md` Leg 1 “not same-rig”
- Aggregator flags CausalRCA fixed-ranking risk when run

**Problematic (verified):**

1. **LaTeX RCAEval table vs raw (critical):** Claims rules Top-1/Top-3/mean-rank **0.756 / 0.822 / 1.89** and BARO **0.811 / 0.911 / 1.54**. Same-tree `eval.leg2` on same JSON → rules **0.289 / 0.611 / 2.98**, BARO **0.144 / 0.878 / 2.32**, CIRCA **0.589 / 0.878 / 2.08**.
2. **Invented detection F1:** LaTeX/MD use ~0.85 “from Top-3 success” vs Xing 0.938. Aggregator detection table: **F1=0.469**.
3. **`yashaswini_final_report.md` AWS overhead:** Asserts Full→Policy sampling cut traces **95%**, P95 latency **−12%**, as AWS cloud results. STATUS: no live campaigns.
4. **Hybrid superiority claim:** MD says hybrid Top-3 ~82% and outperformed static ranking. Raw: hybrid AC@3 **0.478** < rules **0.611**.
5. **STATUS “90 cases, 5 baseline methods”** vs CausalRCA **4** files; LaTeX still tabulates CausalRCA Top-1 **0.889** as if complete.
6. **HTTP API** claimed in MD; template is REST API only.
7. **Competitiveness conclusion** (“within 10 pp F1 **and** ≥50% volume cut”) fails on recomputed F1; volume cut is estimated, not measured live.

**Score: Claims 1/5** — STATUS/sim provenance discipline undermined by LaTeX tables and MD overclaims (Nemi-class results contradiction on Leg 2).

---

## J. Alignment score + Cloud Computing rubric map

### Research Alignment % 

| Dimension | Max | Score | One-line rationale |
|---|---|---|---|
| RQ | 10 | **7** | Clear CA2 RQ; answer incomplete + numerically unreliable |
| Obj | 15 | **9** | Four objs partially delivered; live overhead + honest Leg2 missing |
| Method | 15 | **12** | Three-leg design + stats code strong; live/power gaps |
| Impl | 15 | **12** | Full SAM artefact, 76 tests, config manual; undeployed |
| Exp | 15 | **8** | Sim + RCAEval raw; CausalRCA incomplete; no live Leg 3 |
| Metrics | 10 | **7** | Right metrics; wrong reported values vs raw |
| Evidence | 10 | **4** | Raw strong; PDF/bib/DOI/live weak; tables diverge |
| Claims | 5 | **1** | Critical Leg2/overhead contradictions |
| Rubric | 5 | **2** | Artefact/spec OK; eval/report/viva packaging fail gate of honesty |
| **Total** | **100** | **62** | |

**Compact line:** `RQ7 Obj9 Method12 Impl12 Exp8 Metrics7 Evidence4 Claims1 Rubric2` → **62/100**

### Cloud Computing portfolio rubric (final 88% components)

| Component | Weight | Alignment read (evidence-based) |
|---|---|---|
| Project Specification | 5% | Strong — CA2 RQ + four objs + three-leg method explicit |
| Literature Review | 8% | `relatedwork.tex` present (~127 lines); PDF only 12 pp; DOI `note=` **FAIL**; `refs.bib` stub (4 entries) |
| Artefact / Product Development | 27% | Strong local/SAM ICT; moto tests; **not** live-exercised |
| Evaluation & Analysis | 25% | **Weak** — sim honest; RCAEval raw usable but **report numbers contradict raw**; live overhead absent yet conclusions treat estimates as decisive |
| Report presentation / refs | 8% | Structure on disk; short PDF; broken/minimal `refs.bib`; MD/LaTeX claim drift |
| Configuration Manual | 5% | Present (`docs/CONFIGURATION_MANUAL.md`) with deploy/campaign/teardown |
| Viva | 10% | Not present in folder |

Weekly progress (12% separate): template only under `weekly/`.

### Critical gaps (priority order)

1. **Leg 2 write-up ≠ `results/rcaeval/raw`:** must regenerate `eval.leg2` summary and rewrite tables/claims (rules AC@3≈0.61, F1≈0.47; hybrid worse than rules).
2. **CA2 Leg 3 live AWS unmet:** no `results/live/`; overhead decision-rule evidence is estimate-only.
3. **WhatsApp DOI rule FAIL:** `0` × `note = {doi: ...}` in both bibliographies.
4. **CausalRCA incomplete (4/90)** while STATUS/report imply full five-method 90-case comparison.
5. **PDF packaging:** 12 pages; `latex_report/refs.bib` has 4 entries vs 24 in artefact bib.
6. Replication undersized vs CA2 (48 sim injections vs 60×4 plan); no filled weekly/viva pack.

### What is solid

- CA2 → artefact mapping for AWS serverless topology is coherent (Lambda/API/DynamoDB/CW/X-Ray).
- End-to-end code path (inject → detect → rank → score) exists and is tested; sim results are explicitly labeled.
- RCAEval raw artefacts are substantial and re-aggregatable; stats code matches the proposed protocol.
- Config manual is concrete enough for a third party with an AWS account to attempt Leg 3.
- STATUS’s live-AWS limitation disclosure is clearer than `yashaswini_final_report.md`.

---

**Final verdict:** Against **CA2**, Yashaswini’s work is an **AWS-required** serverless observability thesis with a **strong undeployed artefact** and **usable RCAEval raw**, but alignment is capped by **no live Leg 3**, **DOI-note failure**, and **critical contradiction between reported RCAEval/overhead claims and in-tree evidence**. Alignment **62%**.

Yashaswini — analysis of `yashaswini-thesis` only. Kasi was not analysed.

**Source agent:** [Analyse yashaswini thesis CA2](https://cursor.com/agents/bc-a96b5798-fe38-54b8-8582-39d4dec89f04)

---

GATE_READY=yes
AWS_CLASS=required
