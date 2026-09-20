# Venkat Thesis Traceability Report (venkat-bora-thesis ONLY)

**Scope:** `venkat-bora-thesis/` + CA2 `_handoff/venkat_ca2.txt` only.  
**Do not mix with other theses.**  
**Alignment (explore):** **63/100**  
**AWS classification:** **required** (matched-vCPU EC2)  
**GATE_READY:** yes (exploration completeness — not 100% CA2 alignment)  
**SOLE_AWS_RESIDUAL:** yes

**CA2 / proposal status:** PRESENT — `_handoff/venkat_ca2.txt` (also `venkat-bora-thesis/venkat_ca1 (1).pdf` / CA1 materials).  
Alignment % below is scored **vs CA2 commitments**, cross-checked against `STATUS.md`, `latex_report/`, `distributed-matrix-scaling/`, and committed `results/data/summary_statistics.json`. Evidence-only; **no invented EC2 metrics**; Terraform **not applied**.

Sources used (verified in-tree):
- CA2 text: `_handoff/venkat_ca2.txt`
- STATUS: `venkat-bora-thesis/STATUS.md` (updated 2026-09-20)
- Artefact: `venkat-bora-thesis/distributed-matrix-scaling/`
- Results: `results/data/{summary_statistics,benchmark_results}.json` (+ CSV); figures under `results/figures/` (5 PNGs)
- LaTeX: `latex_report/projectReport.tex` + `text/*.tex`; compiled `projectReport.pdf` (**45 pages**)
- Bib: `latex_report/references.bib` (DOI fields present; WhatsApp `note = {doi: ...}` **not** applied — STATUS)
- Baseline: `baseline_papers/BASELINE_PAPER.md` (Sabir & Alebrahim 2025; DOI 10.3390/math13020298)
- Config manual: `CONFIGURATION_MANUAL.md` (local)
- Residual note: `_analysis_extract/reports/venkat_AWS_RESIDUAL.md` (`READY_FOR_AWS=yes`)
- Terraform scaffold: `distributed-matrix-scaling/terraform/` (project tags only; **not applied**)
- Cloud Computing rubric (WhatsApp / MScCC): Spec 5%, Lit 8%, Artefact 27%, Eval 25%, Report 8%, Config Manual 5%, Viva 10% (+ weekly 12% outside final 88%)

---

## A. Identification

| Field | Value | Status |
|---|---|---|
| Student | Sri Venkat Bora | Verified (CA2, STATUS, README) |
| Student ID | 25164414 | Verified |
| Programme | MSc Cloud Computing, NCI | Verified |
| Title (CA2) | Analyzing Performance of Multi-Threaded and Distributed Matrix Scaling Workloads on Cloud Infrastructure | Matches STATUS / README / LaTeX |
| Baseline | Sabir & Alebrahim (2025), Mathematics 13(2), 298 | DOI present in bib as `doi=`; baseline note present |
| Artefact root | `venkat-bora-thesis/distributed-matrix-scaling/` | Present |
| Cloud platform | **AWS EC2 matched aggregate vCPUs** (CA2) | **Required**; practice is **local Dask `LocalCluster` only** |
| CA2 | `_handoff/venkat_ca2.txt` | Found |

### AWS classification

**AWS_CLASS = required**

CA2 method (§3) requires: cloud compute instances from one general-purpose family; threaded condition on a **single instance with n vCPUs** vs distributed across instances whose vCPUs **sum to n**; IaC provision/destroy; synthetic matrices; completion time + peak RSS + per-core utilisation. The niche statement is explicit that the comparison must be **on cloud infrastructure**. Local single-host Dask cannot satisfy the matched multi-instance EC2 design.

#### Services / capabilities inventory (evidence-only)

| Service / capability | Class | Evidence |
|---|---|---|
| **Amazon EC2** (matched-vCPU scale-up vs scale-out) | **Required** | CA2 §3; Terraform `aws_instance.scale_up` / `scale_out` (count gated on `ami_id`) |
| **VPC / Security Group** (Dask 8786/8787) | **Relevant** | `terraform/main.tf` SG ingress |
| **AWS IAM** (instance/profile least privilege) | **Relevant** | Residual discipline note; not applied |
| **CloudWatch** (optional host metrics) | **Relevant** | STATUS lists as missing; no live artefacts |
| Dask remote scheduler CLI | Soft blocker for live path | `src/main.py` has **no** `--scheduler-address` |
| Lambda / S3 / DynamoDB / SQS / API Gateway | **Not** | Not in CA2 experiment set |

---

## B. Research Question (RQ /10)

**CA2 framing (paraphrased from proposal):** at what matrix order does distributed execution across multiple cloud instances finish before multi-threaded execution on a single cloud instance with the **same total number of cores**?

**Report RQ** (`latex_report/text/introduction.tex`):

> How do multi-threaded and distributed parallel processing compare in completion time, memory footprint, and core-distribution efficiency for matrix workloads of increasing size when total core count is held constant?

| Check | Result |
|---|---|
| CA2 RQ precise & answerable | Pass — crossover / matched-vCPU cloud comparison |
| Report mirrors CA2 | Partial — matched-cores kept; **cloud-instance** clause softened to local proxy |
| Answered with experimental metrics | Partial — local JSON answers local proxy only |
| Live EC2 evaluation clause | Fail — STATUS / abstract / eval: no EC2 campaign |

**Score: RQ 7/10** — clear CA2 question; delivery answers a **local Dask proxy**, not the matched-vCPU EC2 RQ as written (−3).

---

## C. Objectives (Obj /15)

CA2 four goals (Introduction):

| # | CA2 objective | Delivery | Evidence |
|---|---|---|---|
| 1 | Compare both parallelism models for growing matrix sizes at constant total cores | Partial | Local matched worker counts; not EC2 instances |
| 2 | Identify crossover order or show none in tested range | Partial (local) | JSON: **no matmul crossover** through 2000×2000; not measured on EC2 |
| 3 | Record peak memory footprint per model | Pass (local) | `mean_memory` in `summary_statistics.json` |
| 4 | Per-core utilisation (capacity billed unused) | Pass (local) | `mean_cpu` in JSON; CloudWatch not used |

**Score: Obj 9/15** — all four measurable locally with committed evidence; cloud-instance and IaC campaign unmet (−6).

---

## D. Methodology (Method /15)

Aligned with CA2:
- IV: parallelism model (threaded vs distributed; artefact also adds multiprocessing)
- Factor: matrix order 200–2000; workers 1/2/4/8
- DVs: completion time, peak RSS, CPU utilisation
- Synthetic seeded matrices; descriptive repeats
- Ethics: no personal data; destroy-after-campaign intent documented for future EC2

Gaps vs CA2 method:
- **Not** multi-instance EC2 with matched aggregate vCPUs
- IaC provision/destroy **not executed** (Terraform present, default `ami_id=""` → instance count 0)
- Inferential plan (Shapiro → t-test / Mann–Whitney, Holm–Bonferroni, 95% CI crossover bracket) described in LaTeX methodology but **not coded**; no p-value artefacts
- Committed campaign uses **`n_iterations: 3`** (CA2 pilot/power narrative discusses five / power-based replication)
- CLI lacks remote `--scheduler-address` for true distributed arm

**Score: Method 10/15** — local controlled design is solid; cloud + inferential execution incomplete.

---

## E. Implementation / Artefact (Impl /15)

Verified under `distributed-matrix-scaling/`:
- Models: threading, multiprocessing, Dask `LocalCluster` (`matrix_operations.py`, `matrix_scaling_evaluator.py`)
- Harness: `benchmark.py`, CLI `main.py` (`--sizes`, `--workers`, `--iterations`, `--quick`/`--full`)
- Tests: **20** `test_*` methods (`test_matrix_operations.py` + `test_benchmark.py`) per STATUS count
- Results + 5 figures committed
- Docs: README, `CONFIGURATION_MANUAL.md`
- Makefile / requirements
- Terraform: `main.tf` / `variables.tf` / `outputs.tf` — project tags (`project=distributed-matrix-scaling`); **not applied**

Not present / contradicted vs CA2 live path:
- No live EC2 run artefacts / CloudWatch exports
- No `--scheduler-address` in `src/main.py`
- Inferential stats modules absent

**Score: Impl 11/15** — substantive local ICT artefact + tests + config manual + unused Terraform; −4 for missing remote-scheduler wiring and never-executed EC2 path.

---

## F. Experiments (Exp /15)

| Arm | Mode | Evidence | Role vs CA2 RQ |
|---|---|---|---|
| Local campaign | Dask `LocalCluster` | `summary_statistics.json` — **90 configs × 3 iterations** | Proxy only |
| Threaded / multiprocess / distributed | Local | JSON + figures | Matched workers on **one host** |
| Matched-vCPU EC2 (scale-up vs scale-out) | **Not run** | STATUS; residual note | **Required by CA2** |
| Inferential / Holm campaign | **Not run** | Methodology text only | Required by CA2 eval plan |

### Verified JSON anchors (matmul) — match STATUS / LaTeX eval

| Config | mean_time | Note |
|---|---|---|
| Threaded 1000×1000, 1 worker | ≈67.2 ms | Baseline |
| Threaded 1000×1000, 4 workers | ≈62.2 ms | Speedup ≈1.08× |
| Distributed 1000×1000, 4 workers | ≈344.6 ms | ≈5.54× slower than threaded-4 |
| Threaded 2000×2000, 4 workers | ≈651.2 ms | Still faster than distributed |
| Distributed 2000×2000, 4 workers | ≈1099.2 ms | Ratio ≈1.69× |

**Matmul crossover count in committed JSON:** **0** (distributed never faster than threaded at same worker count through 2000×2000).

**Do not treat any of these as EC2 results.**

**Score: Exp 7/15** — reproducible local campaign committed and narratively aligned; fails live EC2 / multi-round / inferential CA2 requirements.

---

## G. Metrics (Metrics /10)

| CA2 metric | Implemented? | Notes |
|---|---|---|
| Completion time | Yes | `mean_time` / `std_time` / `all_times` |
| Peak resident memory | Yes | `mean_memory` |
| Per-core / CPU utilisation | Yes | `mean_cpu` (local OS sampling, not CloudWatch) |
| Crossover order + 95% CI | Partial | Crossover **absence** reported descriptively; no CI/p-values |
| Shapiro / t-test / Mann–Whitney / Holm | No | Narrative only |
| Instance-hours / spend reporting | No | N/A until EC2 campaign |

**Score: Metrics 8/10** — core DV set present in JSON; −2 for missing inferential artefacts and cloud cost/utilisation path.

---

## H. Evidence (Evidence /10)

| Evidence class | Verdict |
|---|---|
| Committed experiment JSON | Present; STATUS / LaTeX numbers match verified anchors |
| Figures (5 PNG) | Present under `results/figures/` |
| Baseline note / DOI | Baseline MD present; bib uses `doi=` |
| WhatsApp DOI `note = {doi: ...}` | **FAIL — 0 entries** (STATUS agrees) |
| pytest suite | 20 tests claimed; methods present in tree |
| Compiled report PDF | 45 pages; claim hygiene documents local-only |
| Configuration manual | Present (local setup) |
| Live EC2 / CloudWatch artefacts | **Absent** |
| Terraform | Present, project tags only, **not applied** |
| Viva / weekly reports | Not evidenced under folder for this audit |

**Score: Evidence 5/10** — local JSON/figures/report honesty strong; DOI-note format + live-cloud evidence weak.

---

## I. Claims / Honesty (Claims /5)

**Honest (verified):**
- STATUS / README / abstract / intro / eval / conclusion: **LOCAL ONLY**; Local Dask ≠ CA2 matched-vCPU EC2
- Eval numbers tied to `summary_statistics.json`; older speedup cells withdrawn
- No crossover claimed through 2000×2000 in local suite
- Inferential stats explicitly **not implemented**
- Residual: `READY_FOR_AWS_ALIGNMENT_PATH=yes`; sole hard residual = live EC2

**Soft / packaging:**
1. README still lists “default: 5” iterations / “statistical significance testing” while committed JSON is `n_iterations: 3` and inferential code absent.
2. WhatsApp DOI `note={doi:}` still not on bib entries despite `doi=` fields.
3. Soft blocker: remote scheduler CLI not wired (needed before live distributed arm).

**Score: Claims 4/5** — post-hygiene disclosure is strong; minor README/iteration packaging drift (−1).

---

## J. Alignment score + residual

### Research Alignment % (explore)

| Dimension | Max | Score | One-line rationale |
|---|---|---|---|
| RQ | 10 | **7** | Precise CA2 cloud RQ; answered on local proxy |
| Obj | 15 | **9** | Four objectives measurable locally; EC2 unmet |
| Method | 15 | **10** | Controlled local design; no live IaC/EC2; no inferential code |
| Impl | 15 | **11** | Real harness + 20 tests + Terraform scaffold unused |
| Exp | 15 | **7** | 90×3 local campaign; zero EC2 rounds |
| Metrics | 10 | **8** | Time/memory/CPU present; no Holm/p-values |
| Evidence | 10 | **5** | JSON/PDF solid; DOI-note 0; no live cloud |
| Claims | 5 | **4** | Local-only honesty strong |
| Rubric | 5 | **2** | Config manual strong; live eval / viva weak |
| **Total** | **100** | **63** | |

**Compact line:** `RQ7 Obj9 Method10 Impl11 Exp7 Metrics8 Evidence5 Claims4 Rubric2` → **63/100**

### Critical gaps (priority)

1. **Live matched-vCPU AWS EC2 campaign missing** (CA2 hard requirement) → **AWS_CLASS=required**, **SOLE_AWS_RESIDUAL=yes**.
2. Soft: wire `--scheduler-address` (or equivalent) before remote Dask workers.
3. Soft: WhatsApp DOI `note = {doi: ...}` on bibliography DOI entries.
4. Soft: implement or drop claimed Shapiro/t-test/Holm artefacts.

### What is solid

- CA2 present and AWS-EC2-scoped.
- Honest STATUS / LaTeX after claim hygiene (local proxy ≠ EC2).
- Committed local campaign (90 configs × 3) with numbers matching STATUS/eval.
- No fabricated EC2 metrics in tree.
- Terraform scaffold with project-only tags ready for future apply (not applied here).
- `venkat_AWS_RESIDUAL.md`: **READY_FOR_AWS=yes**.

---

**Final verdict:** Against **CA2**, Venkat’s work is a **complete local Dask proxy** of a **required AWS EC2 matched-vCPU crossover study**. Local evidence is real and internally consistent (no crossover through 2000×2000). The **sole hard residual** to CA2 alignment is the live multi-instance EC2 campaign (plus multi-round evidence). Exploration alignment **63%**. Gate-ready for exploration completeness only — **do not start `terraform apply` from this report.**

Venkat — analysis of `venkat-bora-thesis/` only.

```
GATE_READY=yes
AWS_CLASS=required
SOLE_AWS_RESIDUAL=yes
ALIGNMENT_EXPLORE=63
```
