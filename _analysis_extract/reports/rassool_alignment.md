# Rassool Thesis Traceability Report (rassool-thesis ONLY)

**Scope:** `rassool-thesis/` only. Do **not** mix with kasi-thesis or any other thesis.  
**Alignment:** **62/100**

**CA2 / proposal (STRICT):** `_analysis_extract/rassool-thesis__RasoolBashaDurbesula_24205478_proposal.txt`  
Alignment % below is scored **vs CA2 commitments**, cross-checked against STATUS, LaTeX, artefact, results, and bib. No invented CA2 text.

Sources used (verified in-tree):
- CA2: `_analysis_extract/rassool-thesis__RasoolBashaDurbesula_24205478_proposal.txt`
- STATUS: `rassool-thesis/dynamodb-pk-capacity-eval/STATUS.md`
- Final summary (side doc): `rassool-thesis/rassool_final_report.md` / `final_report.md`
- LaTeX: `rassool-thesis/latex_report/text/{abstract,introduction,methodology,design,implementation,evaluation,conclusion,relatedwork}.tex`
- Compiled PDF: `rassool-thesis/latex_report/projectReport.pdf` (**33 pages**)
- Bib wired by report: `rassool-thesis/dynamodb-pk-capacity-eval/bib/references.bib` (24 entries; **18** `DOI=` / `doi=`; **0** `note = {doi: ...}`)
- Stub unused by `\bibliography`: `rassool-thesis/latex_report/refs.bib` (4 template entries; **0** `note={doi:}`)
- Artefact: `rassool-thesis/dynamodb-pk-capacity-eval/`
- Results: `results/SCHEMA.md` only — **no** `batches.csv` / `cloudwatch.csv` / `raw/`
- Generated tables: `report/generated/cell_summary.md` — all `[TO BE FILLED FROM EXPERIMENT]`
- Config manual: `configuration_manual/CONFIGURATION_MANUAL.md` (PRESENT)
- Baseline: `baseline_papers/Pantelic_et_al_2026_SQL_NoSQL_baseline.pdf` + `BASELINE_PAPER.md` (PRESENT)
- Cohort overview: `Thesis2_Student_Cloud_Overview.pdf` §8 Rasool
- WhatsApp DOI rule: Moodle “DOI LATEX” — require `note = {doi: ...}` in bib fields
- Cloud Computing rubric (WhatsApp / MScCC-Marking Rubric): Spec 5%, Lit 8%, Artefact 27%, Eval 25%, Report 8%, Config Manual 5%, Viva 10% (+ weekly 12% outside final 88%)

---

## A. Identification

| Field | Value | Status |
|---|---|---|
| Student | Rasool Basha Durbesula | Verified (CA2, STATUS, PDF author) |
| Student ID | 24205478 | Verified |
| Programme | MSc Cloud Computing, NCI | Verified (CA2; PDF Keywords: Cloud Computing) |
| Supervisor | Not stated in sampled title/STATUS | Unset in STATUS |
| Title | Partition-Key Design and Capacity Mode in Amazon DynamoDB: An Empirical Performance-Cost Evaluation under Serverless Workloads | Matches CA2 / STATUS / PDF |
| Baseline | Pantelić et al. (2026), Future Internet, DOI 10.3390/fi18010053 | PDF present under `baseline_papers/` |
| Artefact root | `rassool-thesis/dynamodb-pk-capacity-eval/` | Present |
| Cloud platform | AWS DynamoDB + Lambda + CloudWatch (+ IAM, S3, App Auto Scaling, Budgets) | IaC present; **no live campaign evidence** |
| CA2 / proposal | Extracted proposal text | Present |

---

## B. Research Question (RQ /10)

**CA2 RQ** (Introduction):

> how does Amazon DynamoDB table configuration determine the performance-cost trade-off under serverless workloads?

**Report RQ** (`latex_report/text/introduction.tex`):

> How does Amazon DynamoDB table configuration—specifically the interaction between partition-key design and capacity mode—determine the performance–cost trade-off under serverless workloads?

| Check | Result |
|---|---|
| CA2 RQ stated precisely | Pass |
| Report retains CA2 RQ | Pass — interaction clause is a clarification, not a rewrite |
| Scoped to metered DynamoDB (RCU/WCU, throttle, price) | Pass in wording |
| Answered with live metered measurements | **Fail** — STATUS + evaluation: moto / placeholders only; `results/` has schema only |
| Comparability to Pantelić latency/throughput retained | Pass in design narrative |

**Score: RQ 8/10** — RQ is clear, CA2-faithful, and programme-appropriate; −2 because the metered quantities the RQ is *about* have not been measured on the live service the CA2 commits to.

---

## C. Objectives (Obj /15)

**CA2 four objectives** (Introduction):

| # | CA2 objective | Artefact / report coverage | Evidence |
|---|---|---|---|
| 1 | Quantify how partition-key design affects latency and throttling under each workload profile | K1/K2/K3 in `config/experiment.yaml`, generator, handler, methodology | No filled latency/throttle cells; eval tables `[MOTO SIM]` |
| 2 | Quantify how capacity mode affects throttling and cost at equivalent load | On-demand + provisioned tables + auto-scaling in Terraform | No live cost/throttle campaign; cost model code present |
| 3 | Determine whether latency-minimising configuration also minimises cost | Analysis plan / hypotheses in methodology + `ANALYSIS_PLAN.md` | Cannot be decided — no campaign numbers |
| 4 | Express each of six configurations on latency × throttle × cost surface | 3×2×4 matrix wiring; `cell_summary.md` template | All 24 cells `[TO BE FILLED FROM EXPERIMENT]` |

CA2 factorial is **three** key designs. Code also implements **K4** adaptive tiered sharding (`keys.py`, `handler.py`, `seed.py`, `terraform.tfvars.json` has a K4 capacity block) but `experiment.yaml` factorial remains `[K1, K2, K3]` only. K4 is **off-CA2** relative to the committed 3×2 design; `rassool_final_report.md` claims empirical K4 wins that neither CA2 nor filled results support.

**Score: Obj 8/15** — objectives are correctly specified and instrumented; none are attained with live (or even numeric moto) campaign evidence answering them.

---

## D. Methodology (Method /15)

Aligned with CA2 on paper:
- Full factorial: 3 key designs × 2 capacity modes × 4 workloads (W1–W4), 30 replicates → 720 trials
- DVs: mean / p95 / p99 latency, success rate, throttles, consumed RCU/WCU, cost per 10k ops
- Zipfian skew (`s = 1.070916`), synthetic 1M orders / 10k customers, eu-west-1
- Settling interval, Lambda warm-up, randomised block order
- Two-way ANOVA + interaction, Tukey HSD, Holm–Bonferroni; ART if non-normal
- Ethics: no humans, synthetic data, own-account load within AUP; analysis plan pre-committed
- Item-size sensitivity (1/8/32 KB) as separate run — matches CA2

Gaps vs CA2 execution:
- CA2: “measures … on the **live** metered service”
- Practice: STATUS + `evaluation.tex` — **moto only**; scaled smoke (2k items, 2 reps, W3/W4 only, 10 ops/s) in eval text
- Eval cost-model claim “validated against AWS Cost Explorer in pilot study” has **no** Cost Explorer artefact / CSV in `results/`
- Weekly folder contains only `WEEK_TEMPLATE.md` (no filled weekly reports)

**Score: Method 13/15** — design fidelity to CA2 is high; −2 for live-service execution replaced by emulator smoke and for unreproducible “Cost Explorer pilot” claim.

---

## E. Implementation / Artefact (Impl /15)

Verified under `dynamodb-pk-capacity-eval/`:
- IaC: DynamoDB tables, Lambda driver, IAM, CloudWatch dashboard/alarms/log group, S3 results bucket, Application Auto Scaling, AWS Budgets (`iac/**/*.tf`)
- Workloads: Zipfian generator, profiles W1–W4, Lambda handler, seed
- Analysis: cost model, ANOVA pipeline (`analysis/analyse.py`), design checks CSVs
- Tests: **60** `test_*` functions across 9 files (moto / unit / terraform fmt-validate style)
- Ops docs: `CONFIGURATION_MANUAL.md`, `RUNBOOK.md`, `README.md`, `Makefile` targets
- Config externalised: `config/experiment.yaml`, `config/prices.yaml`

Not verified / missing for CA2 completion:
- Live `terraform apply` / campaign outputs
- Committed `results/batches.csv` (folder explicitly schema-only)
- WhatsApp DOI `note={doi:}` compliance in the bib the PDF uses
- Viva / weekly progress artefacts

**Score: Impl 13/15** — strong ICT artefact + config manual; −2 for no deployed live stack evidence and off-CA2 K4 surface area without factorial inclusion.

---

## F. Experiments (Exp /15)

| Arm | Mode | Evidence path | Role vs CA2 |
|---|---|---|---|
| 3×2×4 live DynamoDB campaign (n=30) | **Not run** | `results/` = SCHEMA only | Core CA2 evaluation |
| Item-size sensitivity 1/8/32 KB | **Not run** | No sensitivity CSVs | CA2 sensitivity run |
| Moto smoke / scaled sim | Narrative only | Eval `[MOTO SIM]` placeholders; STATUS | Pipeline validation, not science |
| Design-check arithmetic | Present | `analysis/design_checks/*.csv` | Predictions, not measurements |
| K4 “beats baseline” claims | Side markdown only | `rassool_final_report.md` | **Not** in CA2 factorial; no result files |

`report/generated/cell_summary.md` states explicitly: “No results/batches.csv yet”.

**Score: Exp 3/15** — experimental *machinery* exists; the CA2 measurement campaign has essentially zero committed empirical cells.

---

## G. Metrics (Metrics /10)

Metrics match CA2 / methodology:
- Latency mean, p50, p95, p99 (+ response_p99 including backlog)
- Throttle rate (throttles never silently dropped per SCHEMA)
- Consumed RCU/WCU; provisioned capacity averages
- Cost and cost per 10k from `config/prices.yaml` (eu-west-1)
- Hot-rank share (~0.90 target), cold-start contamination flag

No formal live significance outputs exist to score beyond pipeline presence (`test_analyse.py` exercises ANOVA on synthetic fixtures).

**Score: Metrics 8/10** — metric set is CA2-correct; −2 because unused on live data (constructs exist only as schema/code).

---

## H. Evidence (Evidence /10)

| Evidence class | Verdict |
|---|---|
| CA2 proposal extract | Present |
| Baseline PDF | PRESENT (`Pantelic_et_al_2026_SQL_NoSQL_baseline.pdf`) |
| Compiled report PDF | **33 pages** |
| Bibliography used by PDF | `bib/references.bib` (24 entries) via `\bibliography{../dynamodb-pk-capacity-eval/bib/references}` |
| WhatsApp DOI `note = {doi: ...}` | **FAIL — 0 / 24** (entries use `DOI=` / `doi=` / `url=`; vendor `note=` texts are *not* doi notes) |
| `latex_report/refs.bib` | 4 unrelated Buyya-template stubs; **not** the wired bibliography |
| Configuration manual | Present |
| Results campaign CSVs | **Missing** (SCHEMA only) |
| Eval tables | Placeholders `[MOTO SIM]` |
| pytest suite | 60 tests in tree (STATUS claims pass on moto — not re-executed here) |
| Design checks | Present |
| Weekly reports | Template only |
| Viva pack | Not present |
| Live AWS / CloudWatch campaign | Not present |

**Score: Evidence 4/10** — documentation/artefact/baseline strong; campaign data + DOI-note rule fail hard.

---

## I. Claims / Honesty (Claims /5)

**Honest (verified):**
- `STATUS.md` and `evaluation.tex` / `conclusion.tex` repeatedly label moto simulation and state live AWS is **not** executed
- `results/SCHEMA.md` refuses pre-filled numbers
- `cell_summary.md` is explicitly unfilled
- Cohort overview §8: “evaluation evidence largely local/moto unless live campaign is run”

**Problematic (verified in files):**
1. Intro contribution claims “first … controlled experiment … on a **production** cloud-metered database service” while evaluation is moto placeholders — overclaim vs evidence.
2. Abstract says simulation results “demonstrate the performance and cost implications” while tables contain no numbers.
3. `STATUS.md` “SUBMIT-READY” / “scientific contribution … stands independently of production data” sits in tension with CA2’s live-measurement niche.
4. `rassool_final_report.md` asserts K4 ~90% RCU cuts, throttle avoidance, etc., with **no** supporting CSV and outside CA2’s three-key design.
5. Eval bullet “validated against AWS Cost Explorer in pilot study” — no Cost Explorer artefact in-tree.
6. DOI WhatsApp format not followed despite “21 verified … DOIs” style claims in STATUS.

**Score: Claims 2/5** — core STATUS/eval disclaimers are honest; contribution language + `rassool_final_report.md` K4 narrative undermine claim discipline.

---

## J. Alignment score + Cloud Computing rubric map

### Research Alignment % (weights as specified)

| Dimension | Max | Score | One-line rationale |
|---|---|---|---|
| RQ | 10 | **8** | CA2 RQ retained; unanswered on live meter |
| Obj | 15 | **8** | Four objs instrumented; none filled with campaign data |
| Method | 15 | **13** | Factorial/stats/ethics match CA2; live→moto gap |
| Impl | 15 | **13** | Terraform/Lambda/tests/config manual solid |
| Exp | 15 | **3** | No batches.csv; placeholders only |
| Metrics | 10 | **8** | CA2-aligned metric set; unused live |
| Evidence | 10 | **4** | Docs/PDF/baseline yes; data + DOI-note no |
| Claims | 5 | **2** | Moto honesty vs production/K4 overclaims |
| Rubric | 5 | **3** | Artefact/spec/config strong; eval empty; viva absent |
| **Total** | **100** | **62** | |

**Compact line:** `RQ8 Obj8 Method13 Impl13 Exp3 Metrics8 Evidence4 Claims2 Rubric3` → **62/100**

### Cloud Computing portfolio rubric (final 88% components)

| Component | Weight | Alignment read (evidence-based) |
|---|---|---|
| Project Specification | 5% | Strong — CA2 RQ + 4 objectives echoed in intro/methodology |
| Literature Review | 8% | Related-work chapter + 24-entry bib + baseline PDF; WhatsApp `note={doi:}` **FAIL** |
| Artefact / Product Development | 27% | Strong local ICT (IaC, Lambda, Zipf, ANOVA, 60 tests, RUNBOOK); **not** live-deployed |
| Evaluation & Analysis | 25% | **Weak** — placeholders / schema-only; cannot answer CA2 trade-off surface |
| Report presentation / refs | 8% | 33-page PDF structured; DOI-note format fail; stub `refs.bib` misleading if mistaken for live bib |
| Configuration Manual | 5% | **Present** (`CONFIGURATION_MANUAL.md`) |
| Viva | 10% | Not present in folder |

Weekly progress (12% separate): template only under `weekly/`.

### AWS classification (required / relevant / not)

**AWS_CLASS = required**

CA2 Research Resources: “Three managed services carry the experiment: DynamoDB itself, AWS Lambda … and Amazon CloudWatch.” Cohort overview §8: “Yes for real latency/capacity numbers… Moto alone is not live AWS.”

| Class | Services | Evidence |
|---|---|---|
| **Required** (CA2 live study) | Amazon DynamoDB; AWS Lambda; Amazon CloudWatch; IAM (execution roles) | CA2 §Research Resources; `iac/tables`, `iac/lambda`, `iac/monitoring`, `iac/iam` |
| **Relevant** (artefact support) | Amazon S3 (results bucket); Application Auto Scaling (provisioned tables); AWS Budgets (spend cap) | `iac/main.tf`, `iac/tables/main.tf`, `iac/monitoring/main.tf` |
| **Not required** for answering CA2 RQ | Cost Explorer (optional bill cross-check); SNS/SQS/API Gateway/ECS/EKS/EC2; non-AWS clouds | Mentioned narratively or absent |

Local **moto** validates code only; it does **not** replace required AWS measurement for CA2 alignment.

### Critical gaps (priority order)

1. **No live AWS campaign** — empty `results/` beyond SCHEMA; CA2 niche unmet.
2. **Evaluation tables unfilled** (`[MOTO SIM]` / `[TO BE FILLED FROM EXPERIMENT]`).
3. **WhatsApp DOI rule FAIL:** `0` entries with `note = {doi: ...}` in wired `references.bib`.
4. **`rassool_final_report.md` K4 win claims** unsupported and off the CA2 3-key factorial.
5. Intro “production … empirical” contribution language vs moto-only evidence.
6. Weekly / viva artefacts absent.

### What is solid

- CA2 ↔ intro RQ/objectives ↔ methodology factorial ↔ Terraform/Lambda artefact form a coherent *design* chain on Pantelić’s metering gap.
- Baseline PDF present; config manual + runbook + 60 tests are substantive.
- STATUS/eval mostly refuse to invent DynamoDB numbers (unlike the K4 side report).

---

**Final verdict:** Against **CA2**, Rassool’s work is **well aligned on specification, methodology narrative, and artefact engineering**, but **not aligned on the empirical core** (live DynamoDB latency/throttle/cost surface). Alignment **62%**. AWS is **required**.

Rassool — analysis of `rassool-thesis` only. Kasi was not analysed.

```
GATE_READY=yes AWS_CLASS=required
```
