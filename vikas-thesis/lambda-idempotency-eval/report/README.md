# Report checklist (NCI research-paper format, max 20 pages)

The report is the student's own writing. This file only lists what each
section needs (master prompt section 7) and which generated file feeds it.
Numbers go in only from `results/live/` - never from `results/moto/`.

| section | must contain | from the artefact |
|---|---|---|
| Abstract | background, gap, method, key measured numbers, meaning, what is still open | `results/live/summary.md` |
| Introduction (max 2 pages) | at-least-once Lambda, the three DynamoDB controls, research question, objectives, who benefits, limits (one region / account), outline | master prompt section 3 |
| Literature survey (3-4 pages) | runtime solutions (Halfmoon, Boki, CausalMesh, LambdaStore, Styx, Netherite, µ2sls) vs managed primitives; comparison table: level of control, platform modifiable?, retries known?, duplicates counted?, cost reported?; niche statement - do **not** paste the proposal | `bib/references.bib` (only these sources) |
| Research methodology | controlled experiment, IVs/DVs, injection mechanism, pilot rule, statistics, ethics | `docs/ANALYSIS_PLAN.md`, `docs/ASSUMPTIONS.md`, `docs/ETHICS.md`, `results/live/pilot_report.md` |
| Design and implementation | architecture, the three paths, driver, pinned versions, outputs | `src/`, `infra/`, `config/versions.yaml`, `results/SCHEMA.md` |
| Evaluation | duplicate rate, latency, capacity tables and figures with 95 % CIs; hypothesis decisions (Holm); E1-E3; correctness-cost surface; comparison to the Halfmoon **criterion**, not its overhead numbers; sensitivity case | `results/live/*.csv`, `figures/live/*.png` |
| Conclusions and discussion | objectives met?, practitioner guidance, future work (multi-item transactions, other stores, provisioned mode, multi-region) | |
| References | Harvard or the template style, DOI / URL for every entry | `bib/references.bib` |

## Rules from the master prompt to check before submitting

- [ ] never claim exactly-once for P1
- [ ] never claim P2 / P3 match Halfmoon's formal runtime guarantees - only measured reduction and cost on stock AWS
- [ ] every comparison has a 95 % CI; tests are Holm-corrected
- [ ] failed conditional checks are reported as cost
- [ ] threats to validity: internal (clean post-commit timeouts only), external (one region / account / store / function service), construct (billed units, not a model), conclusion (one campaign; pilot + replication)
- [ ] the configuration manual is a separate document
- [ ] at least 20 of the 2022-2026 sources are cited in the text where relevant

## Figures and tables to regenerate after the live campaign

```bash
make analyse
```

Vikas Reddy Amanagantti
