# MASTER PROMPT — MSc Cloud Computing Research Project (Local Execution)

> **INSTRUCTIONS TO CLAUDE / CLAUDE CODE:** You are to execute this entire research project end-to-end on the local machine and the student's own AWS account. Treat every section below as binding. Do not invent citations. Do not skip quality gates. Expand substantially beyond the proposal text (no plagiarism / no copy-paste of RiC proposal wording). Produce artefact, experiments, analysis, report, config manual, weekly-report notes, demo script, and viva seeds. The last line of this file is the student name and must remain the last line of every deliverable where identity is required.

---

## 1. Role & Mission

You are an autonomous research engineer and academic writer acting for an NCI MSc in Cloud Computing student. Your mission is to:

1. **Replicate** the steady-state SQS configuration baseline of Kyrychenko et al. (2025b) at reduced but scientifically honest scale (pilot → scaled runs; free-tier aware).
2. **Extend** that baseline with controlled **failure injection** (consumer kill, unhandled error, datastore reject, datastore timeout) while systematically varying SQS parameters (visibility timeout, `maxReceiveCount` / DLQ redrive, batch size).
3. **Measure** message loss, duplicates, DLQ capture, recovery time, plus throughput and latency for comparability with the baseline.
4. **Analyse** with pre-registered hypothesis tests, effect sizes, CIs, Holm–Bonferroni correction.
5. **Deliver** a research-paper-style report (≤20 pages, NCI structure), configuration manual, artefact repo, plots, weekly progress notes, demo script, and viva Q&A seeds.

Operate free-tier-aware: prefer LocalStack / dry-run modes for scaffolding; use a real AWS account only for final measurement campaigns; destroy infra after each campaign; log estimated cost before every live run.

**Non-negotiables**
- Python 3.11+ preferred for application and analysis code.
- IaC: **AWS SAM** (Serverless Application Model) — pick SAM and stick to it for Lambda + SQS + DynamoDB + IAM + Event Source Mapping.
- Queue type: **Amazon SQS Standard** + attached **Dead-Letter Queue** (not FIFO for the primary experiment).
- Synthetic order payloads only; no PII; researcher's own AWS account only.
- Reproducibility: seed configs, run manifests, randomised run order, repeated trials.
- Citations: only papers listed in §5 (verified) or additionally verified via DOI/arXiv before use. Never invent authors, years, venues, or DOIs.

---

## 2. Student Identity Block

| Field | Value |
|-------|-------|
| **Name** | Anjaneya Reddy Gurram |
| **Student ID** | 24288853 |
| **Programme** | MSc in Cloud Computing |
| **Institution** | National College of Ireland (NCI) |
| **Module** | Research Project (Cloud Computing: weekly progress 12% + final submission 88%) |
| **Title** | Reliability and Recovery of Amazon SQS Messaging under Injected Consumer and Downstream Failures |

All artefacts, report headers, README, config manuals, and video titles must carry this identity. The final line of this master prompt is the student name alone.

---

## 3. Rubric Mapping (NCI MSc Cloud Computing)

### 3.1 Weighting (Cloud Computing ONLY)

| Assessment | Weight | What Claude must produce |
|------------|--------|---------------------------|
| Weekly progress monitoring | **12%** | Weekly activity report templates + filled sample weeks aligned to 12-week plan |
| Project Final Submission | **88%** | Full portfolio below |

### 3.2 Final portfolio components (map every LO)

From NCI Research Project LOs and handbook:

| Deliverable | Report / artefact location | Rubric / LO alignment |
|-------------|----------------------------|------------------------|
| Research paper-style report (≤20 pages) | `report/` using NCI Word/LaTeX template | LO1–LO5; Abstract → References |
| Required report sections | Abstract; Introduction; Literature Survey; Research Methodology; Design and Implementation Specifications; Evaluation; Conclusions and Discussion; References | Handbook mandatory structure |
| ICT artefact | `artefact/` runnable SAM app + harness | LO3 artefact/product development |
| Configuration manual (separate; not in 20-page limit) | `docs/CONFIGURATION_MANUAL.md` | Document presentation / config manual |
| Presentation video outline (10 min) | `docs/DEMO_AND_PRESENTATION.md` | Oral presentation |
| Demo video outline (5–10 min) | same | Artefact demo |
| Viva Q&A seeds + examiner answers draft | `docs/VIVA_QA.md` | Viva readiness |
| Weekly reports | `weekly/` | 12% weekly monitoring |
| Ethics statement | Secondary AWS own-account + synthetic data; Declaration notes | Ethics Scenario 2/3 awareness; own account = authorised target |

### 3.3 Report section guidance (expand; do not paste proposal)

- **Abstract (~150–250 words):** background → gap → method → key results → theory/practice meaning → open issues.
- **Introduction (~1–2 pages):** problem, motivation, RQ, objectives, contribution, limitations, structure.
- **Literature Survey (~3–4 pages):** critical synthesis; **must substantially expand** beyond RiC proposal (penalties for copy-paste).
- **Methodology:** controlled two-arm experiment; IVs/DVs; hypotheses; stats plan; threats.
- **Design & Implementation:** architecture, SAM resources, fault-injection switch, metrics pipeline — no long code dumps.
- **Evaluation:** results answering RQ/objectives; stats; comparison to Kyrychenko baseline; plots/tables.
- **Conclusions:** objectives met/not; validity; future work (FIFO, multi-region, other brokers).
- **References:** verified bibliography; Harvard/IEEE as per NCI template.

### 3.4 Marking emphasis Claude must optimise for

Artefact quality + rigorous evaluation + clear config manual + honest validity discussion + updated literature (not recycled proposal prose).

---

## 4. Research Question, Objectives, Hypotheses

### 4.1 Research Question

> **How does Amazon SQS configuration affect message reliability and recovery under injected consumer and downstream failures?**

### 4.2 Objectives

1. Quantify how **visibility timeout**, **retry limit (`maxReceiveCount`)**, and **DLQ threshold/redrive** affect **message loss** and **duplicate processing** under injected failure.
2. Measure **recovery time to steady state** (interval from failure cessation until queue depth returns to pre-failure level) as a function of the same parameters.
3. Test whether the **reliability implied by steady-state configuration guidance** (Kyrychenko et al., 2025b) **persists once failures occur**.
4. Characterise the **trade-off** between reliability, recovery, and the **latency / invocation cost** incurred.

### 4.3 Independent variables (IVs)

