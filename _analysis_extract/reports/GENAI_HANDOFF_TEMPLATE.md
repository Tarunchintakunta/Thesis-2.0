# GENAI_HANDOFF.md — required self-contained structure

Every thesis `GENAI_HANDOFF.md` must be readable alone by another GenAI tool.
**Evidence-only.** Mark unknown/incomplete explicitly. Never invent metrics or runs.
**Kasi excluded.** Artefact-only paths (no whole-monorepo dump).

## Required sections (use these headings)

0. Document meta (student, ID, programme, artefact root, CA2 %, eval completeness, date)
1. Research problem, motivation, research question, and objectives
2. Identified literature gap and how this research addresses it
3. CA2 proposal alignment and any extensions beyond the proposal
4. Research methodology and experimental design
5. Artefact purpose and artefact-only project structure (tree + role of each top folder/file)
6. AWS architecture, services, configurations, and experimental setup (or **N/A — AWS not required / not applied** with reason)
7. Evaluation metrics and why they were selected
8. Baseline definition and baseline comparison
9. Complete evaluation process and number of runs (list each run; lite vs full; destroyed?)
10. Final results and key findings (tables/numbers from committed evidence only)
11. How results satisfy or address **each** research objective (objective-by-objective)
12. How results answer the research question
13. How findings relate to the literature gap and previous research
14. Statistical analysis and significance (or state none / exploratory only)
15. Important observations, trends, positive/negative findings, and anomalies
16. Limitations, validity, reproducibility, and generalisability
17. Final conclusions and research contribution
18. What changed or improved during the evaluation process
19. Remaining issues or recommended future work
20. Important files, scripts, configurations, datasets, and artefacts to reproduce/continue

## Completeness honesty
If 3–5 full-scale final AWS evaluations are not done, say so in §0 and §9–§12.
Still fill every section with the best evidence-bound account so a successor GenAI understands the whole research without reading the original thesis.
