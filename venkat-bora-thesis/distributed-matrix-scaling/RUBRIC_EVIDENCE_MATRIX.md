# Rubric evidence matrix — Venkat (matrix scaling)

**Driver:** `/RUBRIC_70_TO_100_STRATEGY.md`  
**Artefact:** `venkat-bora-thesis/distributed-matrix-scaling/`  
**CA2:** 100% | **INITIAL_EVAL_PASS:** yes | **Final-3:** done  

| Rubric requirement | Where evidence exists | Concrete evidence | Gap to 80+/90+ |
|--------------------|----------------------|-------------------|----------------|
| Objectives fully achieved | STATUS; FINAL3_BASELINE | 1×t3.small vs 2×t3.micro matmul | Obj→elapsed map |
| Critical literature review | report / CA2 | Scale-up vs scale-out | Critique matrix |
| Alternatives considered | terraform vars; STATUS | Equal vCPU matched Free-Tier | Decision table |
| Methodology justified | run_ec2_final_*.sh | destroy-after; n=250 | Why n=250 not 500 (timeout history) |
| Rigorous implementation | results/live/final_* | matmul ok ×3 | — |
| Rigorous evaluation | FINAL3_BASELINE | elapsed ≈0.248–0.252 s | Multi-order soft |
| Synthesis of data | round-1 timeout vs f1–3 ok | Larger n not free | Orchestration overhead vs numpy |
| Relevant theory | STATUS | Scale-out ≠ automatically faster | Lit compare |
| Insightful conclusions | FINAL3 neg | Single-shot; RSS not instrumented | So-what for cloud sizing |
| Academic implications | STATUS | Equal-vCPU crossover evidence | Contribution |
| Practitioner implications | STATUS | Prefer scale-up for small dense matmul | Manual note |
| Validity | destroy_confirmed | eu-west-1 | Single region |
| Generalisability | DESIGN soft | Multi-order beyond-CA2 | Soft |
| Limitations | FINAL3 | n=250; no Holm across orders | Keep |
| Reproducibility | scripts + terraform | matched Free-Tier topology | — |
| Viva evidence | STATUS Rubric | Defend n=500 timeout | — |

**Scoreboard:** raised→yes path · **Updated:** 2026-09-22
