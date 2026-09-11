# Research report - section map (to be written by the student)

Rasool Basha Durbesula - 24205478

The <= 20-page report is the student's own work and is not in this repository.
This page maps each handbook section to the artefact outputs it draws on, and
gives the result-table layout that `analysis/analyse.py` fills in.

| Section | Inputs |
|---|---|
| Abstract | `report/generated/hypotheses.json`, `pareto.csv` after the live campaign |
| Introduction | RQ + objectives (master prompt 1); limitations in `docs/ASSUMPTIONS.md` |
| Literature survey | `bib/references.bib` (21 papers + 3 AWS docs) - themes in master prompt 4 |
| Outputs summary | `configuration_manual/CONFIGURATION_MANUAL.md` section 1 |
| Research methodology | `docs/ANALYSIS_PLAN.md`, `config/experiment.yaml`, `docs/ETHICS.md` |
| Design and implementation | `iac/`, `workloads/`, `docs/ASSUMPTIONS.md`, design checks |
| Evaluation | `report/generated/*` (cell summary, tests, Pareto front, figures) |
| Conclusions | trade-off surface, validity (single account / region / table class), future work (GSI, multi-region, DAX, longer adaptive-capacity horizons) |
| References | `bib/references.bib` |

## Result tables (placeholders until the live campaign)

`python analysis/analyse.py` without results writes `report/generated/cell_summary.md`
with every value set to `[TO BE FILLED FROM EXPERIMENT]`, in this layout:

| workload | configuration | mean latency (ms) | p95 | p99 | throughput (ops/s) | throttle rate | cost / 10k ops |
|---|---|---|---|---|---|---|---|
| W1 | K1-on_demand | [TO BE FILLED FROM EXPERIMENT] | ... | ... | ... | ... | ... |
| ... 24 rows (6 configurations x 4 workloads) | | | | | | | |

Hypothesis table: 12 rows (H_key, H_cap, H_joint x W1-W4) with method (ANOVA or
ART), statistic, p, Holm-adjusted p, effect size (partial eta^2 or epsilon^2),
practical-significance flag - all from `hypotheses.json`.
