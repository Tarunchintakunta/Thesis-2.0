# Rubric strategy: protect 70+, target beyond (MSc Cloud Computing)

**Repo root driver** for every thesis project in this cohort (Kasi excluded).  
**Assessment split (handbook):** **12%** weekly progress monitoring + **88%** final submission.  
**Companion:** `_analysis_extract/reports/RUBRIC_QUALITY_BAR.md` (JPEG weights + per-thesis fold status).

> Right approach: **not** “make the thesis good” in the abstract — engineer the project so **every** rubric category meets the **70%+ descriptor**, while **Artefact (27%) + Evaluation (25%) = 52/88** are pushed **beyond** the minimum.

---

## 1. What “70+” requires (JPEG rubric)

| Component | Weight | 70%+ standard |
|-----------|-------:|---------------|
| Project Specification | 5 | Objectives clearly specified, creative/appropriate, **fully achieved or surpassed** |
| Literature Review | 8 | **Critical** application/critique; breadth **and** depth |
| Artefact / Product Development | **27** | Alternatives **fully considered**; method **fully justified**; application **rigorously** carried out |
| Evaluation & Analysis | **25** | **Rigorous and creative** analysis; synthesise data + theory; insightful conclusions/implications |
| Report Presentation / Referencing | 8 | Excellent presentation/structure; rigorous referencing; correct grammar/spelling |
| Configuration Manual | 5 | Excellent description/structure to **reproduce** environments |
| Viva | 10 | Excellent, well-directed; impeccable Q&A (student-facing) |

**Majority of effort → Artefact + Evaluation.**

---

## 2. Target is NOT “exactly 70%”

### Minimum protection
Every major category must **visibly** satisfy the 70%+ wording.

### High-mark target (beyond the descriptor)
For Artefact and Evaluation especially, produce evidence that goes **above** 70% wording:

- stronger experimental design  
- multiple comparisons / baselines  
- statistical analysis  
- reproducible experiments  
- deeper interpretation  
- **explicit limitations**  
- comparison with literature  
- clear contribution  
- implications for practitioners **and** researchers  

Examiners cannot be forced to award 100 — but the project can **systematically target the highest descriptors**.

---

## 3. Rubric evidence matrix (mandatory before final prose polish)

Fill **one matrix per thesis** (copy template → `THESIS_ROOT/RUBRIC_EVIDENCE_MATRIX.md`).

| Rubric requirement | Where evidence exists | Concrete evidence |
|--------------------|----------------------|-------------------|
| Objectives fully achieved | Evaluation + Conclusion | Objective-to-result mapping |
| Critical literature review | Literature Review | Comparison matrix + critique |
| Alternatives considered | Methodology / Design | Alternatives + rejection rationale |
| Methodology justified | Methodology | Why this design vs RQ/objectives |
| Rigorous implementation | Implementation | Architecture + execution evidence |
| Rigorous evaluation | Evaluation | Stats + repeated experiments |
| Synthesis of data | Evaluation | Cross-factor analysis |
| Relevant theory | Discussion | Results ↔ literature |
| Insightful conclusions | Discussion | **Why** results occurred |
| Academic implications | Discussion | What is added to knowledge |
| Practitioner implications | Discussion | What practitioners can do |
| Validity | Discussion | Internal / external |
| Generalisability | Discussion | Where results apply / do not |
| Limitations | Discussion | Explicit limits + effects |
| Reproducibility | Configuration Manual | Exact setup + procedure |
| Viva evidence | Presentation | Every major decision explainable |

Handbook: report describes research + artefact + evaluation; evaluation must be **critically analysed**, not merely reported.

---

## 4. Project Specification (5%) — measurable objective chain

**Problem → Gap → RQ → Objectives → Variables → Experiments → Metrics → Results**

Handbook: RQ and objectives stated **together with the tests** that show whether they were achieved.

| Weak | Strong |
|------|--------|
| “Evaluate AWS Lambda performance.” | “Evaluate effects of memory, package size, and warming on **Init Duration**, billed duration, and cost using controlled repeated cold invocations; success = Holm-adjusted tests + effect sizes on pre-registered cells.” |

Later, in Evaluation/Conclusion:

> **Objective 1 achieved:** … measured X/Y/Z across predefined configurations; statistical analysis showed …

Auditable **objective → evidence** chain.

---

## 5. Literature Review (8%) — critique, not paper dumps

**search → compare → critique → synthesise → identify gap → justify this study**

Per important paper:

1. What did they do?  
2. How?  
3. Findings?  
4. Strengths?  
5. Weaknesses?  
6. How different from **this** thesis?  
7. What remains unanswered?

**Close with a necessary gap** (not arbitrary):

> Existing studies investigated A and B; C under X conditions remains weakly systematic. Prior work uses inconsistent workloads/configs/metrics. Therefore this study investigates…

---

## 6. Artefact Development (27%) — biggest scoring opportunity

70+ wording: **alternatives considered → method fully justified → rigorous execution**.

Include an explicit **design-decision table**:

| Decision | Alternative 1 | Alternative 2 | Selected | Reason |
|----------|---------------|---------------|----------|--------|
| … | … | … | … | tied to RQ/objectives |

Do **not** only write “we selected factorial design” — show **why**.  
Methodology discusses and justifies choices against RQ/objectives (handbook).

---

## 7. Evaluation & Analysis (25%) — central scoring engine

Handbook: comprehensive analysis + main findings + implications; use statistical tools for significance.

### Recommended structure

**A. Descriptive** — latency / throughput / cost / Init / cold fraction / etc. (thesis-specific)  
**B. Factor effects** — each IV  
**C. Interaction effects** — where design allows (memory × package, QoS × disconnect, …)  
**D. Statistical significance** — ANOVA / KW / MWU / Holm / effect sizes / CIs as appropriate  
**E. Repeated runs** — final-3 / multi-seed; do not hang claims on one shot  
**F. Negative / unexpected results** — **required** (handbook: how they are handled strengthens discussion)

### Weak vs strong claims

| Weak | Strong |
|------|--------|
| “Config A was fastest.” | “A had lowest median latency, but higher compute cost. Factor F was significant; interaction F×G modified the gain. Raising F alone is insufficient for this workload.” |

Pattern for Discussion:

**Our result → prior literature → agree/disagree → explanation → implication**

---

## 8. Discussion — answer “So what?”

Beyond “F was significant”:

- Why?  
- Why it matters?  
- Practitioner implication?  
- Academic implication?  
- Under what conditions?

Handbook: confidence, validity, scope, generalisability, implications, strengths, limitations; compare with previous research; new finding vs method artefact.

### Limitations as strength

> Single region + synthetic/controlled workload → limited external validity for heterogeneous production traffic; controlled setting improves **internal** validity by reducing environmental noise.

---

## 9. Configuration Manual (5%) — easy marks, do not lose

Separate from ≤20-page report. Another person reproduces **without asking**:

Prerequisites → AWS/IAM → deploy → config → run experiment → collect → analyse → **cleanup/destroy**

Exact: versions, region, env vars, commands, IaC, sequence, data paths.

---

## 10. Report presentation (8%)

Dedicated QA: grammar, terminology, figure/table numbering, citations, headings, formatting.  
Every important figure/table has an **analytical** purpose (not “Figure 5 shows…” with no so-what).

---

## 11. Viva (10%) — defend every “why?”

Prepare one-paragraph answers for: design choice, factors, metrics, stats, baselines, limitations, contribution, what you would change.  
**Nothing in the thesis should be a decision you cannot defend.**

---

## 12. Traceability architecture (100-mark target shape)

```text
RESEARCH QUESTION
       │
       ▼
RESEARCH OBJECTIVES
       │
 ┌─────┴─────┐
 ▼           ▼
LIT GAP   VARIABLES
 │           │
 ▼           ▼
METHODOLOGY ──► EXPERIMENT DESIGN
 │                    │
 ▼                    ▼
ALTERNATIVES     EXECUTION
+ JUSTIFICATION       │
                      ▼
               RAW / PROCESSED DATA
                      │
                      ▼
               STATISTICAL ANALYSIS
                      │
                      ▼
                 KEY FINDINGS
                      │
         ┌────────────┴────────────┐
         ▼                         ▼
  LIT COMPARISON              IMPLICATIONS
         │                         │
         └────────────┬────────────┘
                      ▼
              RESEARCH CONTRIBUTION
                      │
                      ▼
           CONCLUSION + FUTURE WORK
```

Every arrow must be traceable in the dissertation.

---

## 13. 70+ protection rule

**No rubric category is “done” until there is explicit evidence for its 70%+ wording.**

| Category | ❌ Describing work | ✅ Demonstrating research quality |
|----------|-------------------|-----------------------------------|
| Lit | “Reviewed 20 papers.” | Compare, critique, reconcile, gap → RQ |
| Artefact | “Implemented the experiment.” | Alternatives + justification + rigorous execution |
| Eval | “Best config was X.” | Stats, interactions, interpretation, lit compare, implications, limitations |

---

## 14. Pre-submission 100-mark audit (per thesis)

### Specification — 5
- [ ] Every objective measurable  
- [ ] Every objective tested  
- [ ] Objective→evidence map exists  
- [ ] Project justified  

### Literature — 8
- [ ] Critical, not descriptive  
- [ ] Strengths/weaknesses  
- [ ] Papers compared  
- [ ] Contradictions explained  
- [ ] Clear gap → RQ  

### Artefact — 27
- [ ] Alternatives table  
- [ ] Selection justified vs RQ  
- [ ] Reproducible method  
- [ ] Rigorous execution evidence  
- [ ] Design decisions evidence-based  

### Evaluation — 25
- [ ] Right metrics  
- [ ] Repeated experiments (final-3 / seeds)  
- [ ] Appropriate stats  
- [ ] Interactions where designed  
- [ ] **Negative results** disclosed  
- [ ] Compared with literature  
- [ ] Implications  
- [ ] Validity / generalisability  
- [ ] Directly answers RQ  

### Report — 8
- [ ] Structure, grammar, refs, numbered figs/tables, no fluff  

### Configuration — 5
- [ ] Another researcher can reproduce; versions + destroy path  

### Viva — 10
- [ ] Defend decisions, results, limits, contribution  

---

## 15. What “aiming for 100” is **not**

**Do not** add random features to look impressive.  
Handbook ties work to **RQ, methodology, evaluation, contribution**.

Push to the top end with:

**more rigorous evidence + stronger justification + deeper analysis + statistical validation + better prior-research comparison + clearer contribution + better reproducibility**

— not “more stuff.”

For each thesis: **Evaluation is the central scoring engine**; lit + methodology exist to support it.

---

## 16. Cohort operating procedure (this repo)

**Priority now: artefact design + execution evidence — NOT report writing.**

Reports/LaTeX/prose can wait. Marks are engineered by **what the artefact measures and how it is run**, so examiners later have unavoidable evidence for Artefact (27%) + Evaluation (25%).

### Artefact-first rule (binding)

Design and run so that each thesis **already contains**:

| Rubric need | Artefact property (build this, don't "write" it yet) |
|-------------|------------------------------------------------------|
| Alternatives considered | Explicit rejected paths in code/config/DESIGN (quarantined modules, ASSUMPTIONS, disabled scales) |
| Method justified | Pre-registered `experiment.yaml` / ANALYSIS_PLAN tied to RQ factors |
| Rigorous execution | IaC + deploy→measure→**destroy**; pinned versions; reproducible scripts |
| Rigorous evaluation | Repeated packs (final-3 / seeds); stats scripts that refuse mixed data_modes |
| Factor + interaction evidence | Factorial or multi-cell campaigns on disk |
| Negative results | Cells that show non-improvement kept in results (not deleted) |
| Baseline comparison | **Baseline** and **proposed** in the same run matrix (not a later essay) |
| Reproducibility | Config manual + one-command runners (`run_final_*.sh`) |
| Objective→test link | Named phases/metrics in configs matching objectives |

**Do not** spend cycles on report chapters until the artefact pack for that thesis saturates the rows above.

### Regression + credits (binding)

- Any artefact change ⇒ **full regression** (unit/integration tests + smoke) then **full-scale evaluation again** (AWS destroy-after, or local full pack for local-only thesis).  
- Do not keep stale `final_*` claims after a breaking artefact change — re-run packs.  
- Budget: use available credits **aggressively and usefully** (deeper n, more cells, confirmatory depth) — still **one AWS stack at a time** and **destroy-after** every round.  
- Wording in all docs/results: **baseline** and **proposed** only (never “arm/arms”).

### Sequence

1. CA2 floor **100%** + `INITIAL_EVAL_PASS` + final-3 (or campaign-as-pack).  
2. For **each thesis**: keep `RUBRIC_EVIDENCE_MATRIX.md` as a **pointer to artefact paths** (results, configs, scripts) — not a writing task.  
3. Close remaining AWS/local final packs; strengthen weak artefact gaps (missing **baseline** or **proposed**, missing destroy, missing repeats, missing neg cell).  
4. Scoreboard Rubric column tracks **artefact evidence completeness**, not prose quality.  
5. Report/Discussion prose is a **later** fold from the matrix — deferred.  
6. `GENAI_HANDOFF.md` only when operator requests, after finals + artefact matrix saturated.

### Template location

Copy §3 table into:

`{thesis-root}/RUBRIC_EVIDENCE_MATRIX.md`

Update `_analysis_extract/reports/CA2_ALIGNMENT_SCOREBOARD.md` when a thesis clears the matrix.

---

## 17. Next useful step

**Artefact gap hunt (no report):** for each thesis, list missing **on-disk** evidence that would fail a 70+ Artefact/Eval audit (e.g. no **baseline**/**proposed** pair, single run only, no destroy, no neg cell, stats not runnable). Fix by **design/run**, not by prose.

Report checklist / 80+/90+ narrative mapping stays deferred until artefact packs are saturated.
