# Rubric evidence matrix — Chaitanya (lambda cold-start isolation)

**Driver:** `/RUBRIC_70_TO_100_STRATEGY.md`  
**Artefact:** `chaitanya-thesis/lambda-coldstart-isolation/`  
**CA2:** 100% | **INITIAL_EVAL_PASS:** yes | **Final-3:** done (`results/live/final_{1,2,3}/`)  
**Rubric:** raised→yes path — protect 70+; push Eval/Artefact beyond minimum  

| Rubric requirement | Where evidence exists | Concrete evidence | Gap to 80+/90+ |
|--------------------|----------------------|-------------------|----------------|
| Objectives fully achieved | STATUS Rubric notes; Eval tables | Init H1 rejects on final-3; H2/H3/H4 lite in `data/processed/live/` | Explicit O1–On ↔ result table in LaTeX Conclusion |
| Critical literature review | `docs/` + report lit; bib 26 DOI | Cold-start taxonomy vs Bluemke Duration/cost | Stronger per-paper critique matrix in report |
| Alternatives considered | STATUS; ASSUMPTIONS; DESIGN_RATIONALE | Free controls vs provisioned concurrency; bytecode dropped | Expand decision table in Method chapter |
| Methodology justified | ANALYSIS_PLAN; experiment.yaml | Pre-registered H1–H4; Holm; force_cold=update_env | Tie each phase to RQ sentence in Method |
| Rigorous implementation | terraform/SAM; deploy/teardown; live_r* | Destroy-after finals; REPORT Init parser | Confirmatory n≥30 still soft beyond-CA2 |
| Rigorous evaluation | FINAL3_BASELINE; live_lite Holm | H1 reject ×3; java≫nodejs≳python Init p50 | Deeper interaction/cost narrative in Eval |
| Synthesis of data | init_summary; roi_lite; adopt_lite | Package prune ADOPT-lite; memory HOLD-lite | Cross-factor Init×cost paragraph |
| Relevant theory | Eval vs Bluemke | Isolates Init vs aggregate Duration | Explicit agree/disagree sentences in Discussion |
| Insightful conclusions | FINAL3_BASELINE verdict | Ordering stable; lite n limits Holm on H3 | “Why java Init higher” mechanism note |
| Academic implications | DESIGN_RATIONALE; STATUS | Free-control Init evidence at lite depth | Contribution bullet in Conclusion |
| Practitioner implications | adopt_lite_matrix | Prune package + warming candidates; memory raise HOLD | Config Manual “operator takeaway” box |
| Validity | STATUS; ASSUMPTIONS | Intended-cold discard; data_mode segregation | External validity: single region eu-west-1 |
| Generalisability | STATUS limitations | Lite n; arm64 fixed | Multi-region beyond-CA2 |
| Limitations | STATUS §7; FINAL3_BASELINE | n=5 finals; H3 underpowered; proxy≠Init | Keep honest; do not inflate |
| Reproducibility | configuration_manual.md; Makefile | package→deploy→campaign→teardown | Verify destroy commands current |
| Viva evidence | STATUS Rubric notes | Why drop bytecode; why lite n; why Bluemke gap | One-pager Q&A for student |

## Objective → test → result (draft)

| Objective | Test / metric | Result location | Achieved? |
|-----------|---------------|-----------------|-----------|
| Isolate Init by runtime (H1) | runtime_compare cold Init | final_1–3 H1 reject | **yes** (lite) |
| Package size effect (H2) | package_size / live_*_init | `data/processed/live/init_summary_by_cell.csv` | **yes** (lite) |
| Warming cold fraction (H3) | H3-lite on vs off | h3_warming_summary | **directional** (underpowered) |
| Memory exploratory (H4) | Python memory sweep | h4_python_memory_summary | **yes** (lite exploratory) |

## Design decisions (Artefact)

| Decision | Alt 1 | Alt 2 | Selected | Reason |
|----------|-------|-------|----------|--------|
| Init vs Duration | Aggregate Duration only | REPORT Init | Init | RQ isolates cold-start init |
| Paid warming | Provisioned concurrency | EventBridge sparse | EventBridge | Free control; CA2 scope |
| Bytecode cell | Keep broken cell | Drop | Drop | Unhandled on live; ASSUMPTIONS W7 |
| Final depth | n≥30 confirmatory | lite smoke ×3 | lite ×3 | Free-Tier / shared account; soft beyond-CA2 |

## Eval checklist

- [x] Descriptive Init tables  
- [x] Factor H1 on finals; H2–H4 on initial_eval  
- [ ] Richer Init×cost synthesis in LaTeX Eval  
- [x] Stats (H1; lite Holm family)  
- [x] Repeated finals ×3  
- [x] Negative: lite n; H3 fail; posthoc miss on f2  
- [x] vs Bluemke framed  
- [ ] Practitioner box in Config Manual  
- [x] Limitations disclosed  
- [x] RQ answered at lite depth  

**Scoreboard Rubric70:** raised→yes path  
**Last updated:** 2026-09-22
