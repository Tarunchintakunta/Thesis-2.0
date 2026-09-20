# Varun Thesis Traceability Report (Varun ONLY)

**Scope:** `Varun/` only. Do **not** mix with kasi or any other thesis.  
**Alignment:** **58/100**  
**AWS classification:** **required**  
**GATE_READY:** yes

**CA2 / proposal status:** PRESENT — `Varun/VarunGampa_RIC_CA2.txt` (also `VarunGampa_RIC_CA2.pdf`).  
Alignment % below is scored **vs CA2 commitments**, cross-checked against `STATUS.md`, `latex_report/`, `s3-predictive-optimization/`, and committed results. Evidence-only; no invented CA2 clauses.

Sources used (verified in-tree):
- CA2 text: `Varun/VarunGampa_RIC_CA2.txt`
- STATUS: `Varun/STATUS.md` (updated 2026-09-19)
- LaTeX: `Varun/latex_report/projectReport.tex` + `text/*.tex`; compiled `projectReport.pdf` (**20 pages**)
- Bib: **`refs.bib` NOT FOUND** under `Varun/` (projectReport.tex has no `\bibliography`)
- Artefact: `Varun/s3-predictive-optimization/`
- Results: `results/data/{pilot,baseline,improved}_results.json` + `results/figures/*.png` (4 PNGs)
- Baseline: `Varun/baseline_papers/BASELINE_PAPER.md` + `Shen_et_al_2025_TierBase_baseline.pdf` (PRESENT)
- Docs: `README.md`, `docs/ARCHITECTURE.md`, `docs/CONFIGURATION_MANUAL.md`
- WhatsApp DOI rule: Moodle “DOI LATEX” — require `note = {doi: ...}` in bib fields
- Cloud Computing rubric (WhatsApp / MScCC-Marking Rubric): Spec 5%, Lit 8%, Artefact 27%, Eval 25%, Report 8%, Config Manual 5%, Viva 10% (+ weekly 12% outside final 88%)

---

## A. Identification

| Field | Value | Status |
|---|---|---|
| Student | Varun Gampa | Verified (CA2 cover, STATUS, README) |
| Student ID | 23398639 | Verified (CA2; email `X23398639@student.ncirl.ie`) |
| Programme | MSc Cloud Computing, NCI | Verified |
| Supervisor / Lecturer | Sean Heeney | Verified (CA2; STATUS) |
| Title (CA2) | Predictive Storage Cost Optimization Framework for Amazon S3: Intelligent Storage-Class Recommendation, Forecasting and Savings Estimation | Matches artefact README / STATUS |
| Title (LaTeX PDF) | …based on Intelligent Storage-Class Management | Wording drift vs CA2 |
| Baseline | Shen et al. (2025) TierBase (ICDE); also cites Yang/Liu/Beck in CA2 | PDF present; DOI in `BASELINE_PAPER.md` as `10.1109/ICDE65448.2025.00049` — **no** WhatsApp `note={doi:...}` bib |
| Artefact root | `Varun/s3-predictive-optimization/` | Present |
| Cloud platform | Live AWS S3 pipeline (CA2); local simulator in delivery | **AWS-required**; delivery is `DRY_RUN` / synthetic only |
| CA2 / proposal | `VarunGampa_RIC_CA2.txt` | Found |

### AWS services named in CA2 (inventory)

| Service / capability | Role in CA2 | In artefact evidence |
|---|---|---|
| **Amazon S3** | Target store; live bucket under test | Simulated only (`WorkloadGenerator` / `S3Simulator`) |
| **AWS SDK (Boto3)** | Metadata collection module | Listed in `requirements.txt`; **no `import boto3` in `src/`**; README claims `src/metadata/collector.py` — **file absent** |
| **S3 Inventory** | Metadata source (Table 1) | Not implemented |
| **CloudWatch** | Near-real-time cost/utilisation proxy for forecast validation | Not implemented / not measured |
| **S3 Lifecycle Policies** | Native baseline for realised savings | **Simulated** age rules in `SavingsEstimator` |
| **S3 Intelligent-Tiering** | Native baseline | **Simulated** monitoring/tier logic in `SavingsEstimator` |
| **AWS Cost Explorer** | Settled-cost confirmation for forecasts | Not called |
| **AWS Pricing API** | Savings delta pricing (Table 1) | **Static** `configs/pricing.json` only; metadata string claims “AWS Pricing API” |
| **Budget alerts** | Ethics / cost control | Not evidenced |

**AWS_CLASS = required** — CA2 RQ requires evaluation “in a live AWS environment”; contribution explicitly rejects simulation-only validation (“instead of through simulation”); solution is “implemented entirely on AWS.”

---

## B. Research Question (RQ /10)

**Source:** CA2 §1 Research Question

> To what extent does an integrated predictive storage-class optimisation framework – combining machine-learning-based storage-class recommendation, time-series-based cost forecasting, and savings estimation – reduce Amazon S3 storage cost and improve storage-class allocation accuracy, relative to AWS-native Lifecycle Policies and Intelligent-Tiering, when evaluated in a live AWS environment?

| Check | Result |
|---|---|
| RQ stated precisely in CA2 | Pass |
| Echoed in artefact README | Partial — live-AWS clause dropped |
| Stated in LaTeX intro | Fail — filler text; no formal RQ |
| Answered with experimental metrics | Partial — synthetic allocation / MAPE / simulated savings only |
| Live AWS evaluation clause | Fail — STATUS: “No live AWS infrastructure was used” |

**Score: RQ 7/10** — CA2 RQ is clear and answerable; delivery answers a **simulator proxy**, not the live-AWS RQ as written (−3).

---

## C. Objectives (Obj /15)

CA2 has no numbered “Objectives” list; objectives are inferred from Proposed Solution (5 components) + Evaluation Plan success criteria.

| # | CA2 commitment | Artefact / report coverage | Evidence |
|---|---|---|---|
| 1 | Boto3 metadata collection on real S3 (+ Inventory/CloudWatch) | Simulator objects only; **no** `metadata/collector.py` | FAIL |
| 2 | Hybrid rule + supervised ML recommender (RF/XGBoost) | `baseline.py` + `ml_recommender.py` (XGBoost) | PASS (synthetic) |
| 3 | Cost forecasting (Prophet/ARIMA) vs naive persistence | `time_series.py` + `naive_baseline.py`; results report `beats_naive: false` | PASS (honest fail vs success bar) |
| 4 | Savings estimation before apply (Pricing) | `savings/estimator.py` + static pricing JSON | PARTIAL (not Pricing API) |
| 5 | Eval harness vs Lifecycle + Intelligent-Tiering on same bucket | Simulated baselines in savings comparison | PARTIAL |
| 6 | Live AWS + Cost Explorer / CloudWatch validation | Explicitly not run (`DRY_RUN=1`) | FAIL |
| 7 | Three workloads + Wilcoxon (α=0.05); forecast beats naive | Single synthetic mix; Wilcoxon **code** in `metrics.py` but **not executed** in `experiment.py` / no `p_value` in results | FAIL |

**Score: Obj 8/15** — local recommender/forecast/savings stack exists; live metadata, live baselines, multi-workload Wilcoxon, and forecast-beats-naive success criteria unmet.

---

## D. Methodology (Method /15)

CA2 method (evidence):
- Five-module AWS-native pipeline (Table 1)
- Python 3.11 + XGBoost + Prophet + Boto3
- Controlled S3 bucket + historical pricing / billing validation
- Metrics: allocation accuracy, MAPE/RMSE vs naive, realised USD/% vs Lifecycle & Intelligent-Tiering, operational overhead
- Wilcoxon signed-rank across repeated trial buckets; success = significant cost cut vs both natives on ≥2/3 workloads **and** forecast better than naive

Artefact method (evidence):
- `ExperimentRunner` generates synthetic workloads; `mode: dry_run` in all three result JSONs
- Configs `pilot.yaml` / `baseline.yaml` / `improved.yaml` encode recommendation + forecast + savings
- `docs/ARCHITECTURE.md` + `CONFIGURATION_MANUAL.md` describe DRY_RUN vs live (`DRY_RUN=0`) but live path is undocumented as executed
- LaTeX `methodology.tex` / `design.tex` are **repeated boilerplate** (asynchronous event-driven filler); do not document CA2 protocol

Gaps vs CA2:
- Simulation instead of live S3 (STATUS §Data Mode)
- No three workload types as separate campaigns
- Wilcoxon configured in YAML (`statistical_test: "wilcoxon"`) but evaluation path never calls `wilcoxon_test`
- Operational overhead metric absent
- Cost Explorer / CloudWatch validation absent

**Score: Method 9/15** — architecture/docs track CA2 design; execution protocol is simulator-only and incomplete vs stated significance plan.

---

## E. Implementation / Artefact (Impl /15)

Verified present under `s3-predictive-optimization/`:
- Recommendation: `src/recommendation/baseline.py`, `ml_recommender.py` (features include `access_recency`)
- Forecasting: `naive_baseline.py`, `time_series.py` (Prophet)
- Savings: `estimator.py` (Lifecycle / Intelligent-Tiering simulators)
- Pricing: `s3_pricing.py` + `configs/pricing.json`
- Simulator: `s3_simulator.py`, `workload_generator.py`
- Runner + metrics: `runner/experiment.py`, `evaluation/metrics.py`
- Tests: **20** `def test_*` across 5 files (pricing 5, recommendation 4, forecasting 3, savings 4, integration 4)
- Docs: README, ARCHITECTURE, **CONFIGURATION_MANUAL** (rubric item present)
- Results + 4 figures committed
- Makefile / requirements / `.env.example`

Not present / contradicted:
- `src/metadata/collector.py` (README tree) — **missing**
- `analysis/statistics.py` (README) — **missing** (only `plotting.py`)
- Any live Boto3 client usage
- Separate `refs.bib`
- Meaningful LaTeX implementation narrative (`implementation.tex` = “AWS Services are used” + filler)
- GitHub workflow is a stub (`echo "Setting up..."`)

**Score: Impl 11/15** — substantive local ICT artefact + config manual + tests; −4 for missing live collector path and README phantom modules.

---

## F. Experiments (Exp /15)

| Arm | Mode | Evidence | Role vs CA2 RQ |
|---|---|---|---|
| Pilot (100 obj, 30d) | `dry_run` | `pilot_results.json` | Smoke; not a live bucket |
| Baseline TierBase-inspired (1000, 90d) | `dry_run` | `baseline_results.json` | Rule recommender |
| Improved ML+Prophet (1000, 90d) | `dry_run` | `improved_results.json` | Full stack proxy |
| Three CA2 workloads (static/mixed/high-churn) × Wilcoxon | **Not run** | — | Required for success criterion |
| Live S3 + Cost Explorer confirmation | **Not run** | STATUS | Required by RQ |

Verified numbers (JSON ↔ STATUS):

| Experiment | Alloc. acc. | Forecast MAPE | Beats naive | Savings % (vs unopt.) |
|---|---|---|---|---|
| Pilot | 32.0% | 21.04% | No (equal) | 42.4% ($0.01/mo) |
| Baseline | 50.4% (P 89.9%, F1 54.4%) | 21.73% | No | 21.0% ($0.12/mo) |
| Improved | 17.8% (P 33.5%, F1 20.2%) | 21.73% | No | 57.4% ($0.34/mo) |

Improved ML reports `train_accuracy: 1.0`, `test_accuracy: ≈0.973` on its training labels, while allocation accuracy vs runner’s heuristic “optimal” labels is **17.8%** — different label regimes; not a results-file contradiction of STATUS, but weak RQ support for “improve allocation accuracy.”

CA2 success bar (forecast statistically better than naive) is **not met** on any committed run (`beats_naive: false`).

**Score: Exp 7/15** — reproducible synthetic campaign committed; fails live, multi-workload, Wilcoxon-output, and forecast-beats-naive requirements.

---

## G. Metrics (Metrics /10)

| CA2 metric | Implemented? | Notes |
|---|---|---|
| Storage-class allocation accuracy | Yes | vs synthetic “optimal” heuristic in `run_evaluation` |
| Forecast MAPE / RMSE vs naive | Yes | Prophet does not beat naive |
| Realised cost savings vs Lifecycle & Intelligent-Tiering | Partial | Simulated cost deltas, not billed AWS |
| Operational overhead | No | Not in results |
| Wilcoxon α=0.05 | Code only | Not applied to committed experiments |

**Score: Metrics 8/10** — core CA2 metric set present in code/results; −2 for unused Wilcoxon + missing overhead + non-billed “realised” savings.

---

## H. Evidence (Evidence /10)

| Evidence class | Verdict |
|---|---|
| Committed experiment JSON | Present; STATUS numbers match |
| Figures (4 PNG) | Present under `results/figures/` |
| Baseline PDF | PRESENT (`Shen_et_al_2025_TierBase_baseline.pdf`) |
| pytest suite | 20 tests in tree (STATUS says both “16/16” and “20/20” — inconsistent) |
| Compiled report PDF | 20 pages of **repetitive filler**; image placeholders; fake-looking citations (Jackson/Wilson/Lopez/Garcia 2025–26) not in CA2 refs |
| Bibliography / `refs.bib` | **MISSING** — no `\bibliography`, no `.bbl` |
| WhatsApp DOI `note = {doi: ...}` | **FAIL — 0 entries** (no bib file) |
| Configuration manual | Present and substantive |
| Live AWS / CloudWatch / Cost Explorer artefacts | Absent |
| README file tree vs disk | Overclaims missing `metadata/`, `statistics.py`, several scripts |
| Viva / weekly reports | Not present under `Varun/` |

**Score: Evidence 4/10** — experimental JSON/figures/config-manual strong; report packaging, bib, DOI-note, and live-cloud evidence weak.

---

## I. Claims / Honesty (Claims /5)

**Honest (verified):**
- STATUS clearly labels **SYNTHETIC (Local Simulator)** and lists what is simulated vs not live
- Forecast honesty: Prophet does not beat naive (aligns with Beck et al. caution in CA2)
- Savings JSON includes simulated AWS baseline comparisons with explicit descriptions

**Problematic (verified in files):**
1. STATUS “Overall Completion: **100%**” / “Deployment” narrative vs CA2 live-AWS RQ unmet.
2. LaTeX abstract/conclusion: “significant improvements” / “successfully validated the hypothesis” without tying to MAPE-fail / low ML allocation accuracy; filler “cloud-native” paragraphs unrelated to S3 FinOps.
3. LaTeX research gap reframed as “temporal recency buffer” — only weakly reflected as feature `access_recency`; diverges from CA2 integrated recommendation+forecast+savings niche.
4. README documents modules/scripts that do not exist; implies live Boto3 collector.
5. Savings metadata claims “Cost delta calculation using AWS Pricing API” while implementation reads local `pricing.json`.
6. STATUS test-count inconsistency (16 vs 20).

**Score: Claims 2/5** — STATUS simulation disclosure is a real credit; packaging/completion/report overclaims dominate.

---

## J. Alignment score + Cloud Computing rubric map

### Research Alignment % (weights as specified)

| Dimension | Max | Score | One-line rationale |
|---|---|---|---|
| RQ | 10 | **7** | Precise CA2 RQ; answered only on simulator |
| Obj | 15 | **8** | Local 3-function stack; live metadata/eval/Wilcoxon/3-workloads missing |
| Method | 15 | **9** | Architecture matches CA2; execution protocol incomplete |
| Impl | 15 | **11** | Real code, 20 tests, config manual; no live Boto3; README phantoms |
| Exp | 15 | **7** | Three dry-run runs committed; not live / not CA2 success bar |
| Metrics | 10 | **8** | Allocation/MAPE/savings present; Wilcoxon unused; overhead missing |
| Evidence | 10 | **4** | JSON/figures solid; LaTeX filler; no refs.bib; DOI-note 0 |
| Claims | 5 | **2** | Simulation honesty vs 100%/LaTeX/README overclaims |
| Rubric | 5 | **2** | Config manual strong; report/lit/viva/live-eval weak |
| **Total** | **100** | **58** | |

**Compact line:** `RQ7 Obj8 Method9 Impl11 Exp7 Metrics8 Evidence4 Claims2 Rubric2` → **58/100**

### Cloud Computing portfolio rubric (final 88% components)

| Component | Weight | Alignment read (evidence-based) |
|---|---|---|
| Project Specification | 5% | Strong in CA2 (RQ + 5-module solution + eval plan); weak carry-through into LaTeX |
| Literature Review | 8% | CA2 lit is real; LaTeX related-work is filler; **no bib / DOI `note=` FAIL** |
| Artefact / Product Development | 27% | Strong local simulator pipeline; **AWS-required path not executed** |
| Evaluation & Analysis | 25% | Synthetic tables exist; forecast fails naive bar; no live/Wilcoxon campaign |
| Report presentation / refs | 8% | 20-page PDF is non-substantive repetition; no references section |
| Configuration Manual | 5% | **Strong** — `docs/CONFIGURATION_MANUAL.md` |
| Viva | 10% | Not present in folder |

Weekly progress (12% separate): not found under `Varun/`.

### Critical gaps (priority order for AWS phase)

1. **Live AWS evaluation missing** while CA2 RQ/contribution require it → **AWS_CLASS=required**.
2. **No Boto3 metadata collector** (claimed in README/CA2 Table 1; absent on disk).
3. **WhatsApp DOI rule FAIL:** `refs.bib` missing → **0** `note = {doi: ...}`.
4. **LaTeX report unusable** as research evidence (filler / placeholders / no bibliography).
5. Wilcoxon / three-workload / Cost Explorer+CloudWatch validation not evidenced.
6. Forecast never beats naive — CA2 success criterion unmet even on synthetic data.
7. README phantom files (`metadata/`, `statistics.py`, scripts) undermine reproducibility claims.

### What is solid

- CA2 is present, coherent, and AWS-native FinOps-scoped.
- Working local artefact with recommendation + Prophet + naive baseline + savings estimator.
- Committed JSON/figures match STATUS numerical summaries.
- STATUS is explicit that experiments are synthetic.
- Configuration Manual exists (rubric 5% item).
- TierBase baseline PDF present.

---

**Final verdict:** Against **CA2**, Varun’s work is a **partial local simulator of an AWS-required S3 FinOps study**. The code/results chain for synthetic recommendation/forecast/savings is real, but the **live AWS RQ**, **Boto3/Inventory/CloudWatch/Cost Explorer** path, **Wilcoxon multi-workload success protocol**, and **report/bib/DOI packaging** are not aligned. Alignment **58%**.

Varun — analysis of `Varun/` only. Kasi not analysed.

```
GATE_READY=yes
AWS_CLASS=required
```
