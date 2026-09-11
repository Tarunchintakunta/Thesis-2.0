# docs/report/

The research paper style report (max 20 pages, NCI template) is written by the
student. Mandatory sections: Abstract, Introduction, Literature Survey, Research
Methodology, Design and Implementation Specifications, Evaluation, Conclusions
and Discussion, References.

## Where the evidence for each section lives

| Section | Artefact source |
|---------|-----------------|
| Design and Implementation | `docs/ARCHITECTURE.md`, `infra/lambda_app/`, `src/logad/` |
| Methodology | `configs/experiment.yaml` (phases, 240 injections, seeds), `configs/detectors.yaml`, `configs/alarms.yaml`, `configs/drain.yaml` |
| Evaluation - tables | `results/tables/summary.md`, `per_category.md`, `hypotheses.md` |
| Evaluation - figures | `results/figures/*.png` |
| Reproducibility | `results/parser_fingerprint.json`, `results/certification/`, `results/run_info.json` |

The committed results come from the local Lambda runtime emulator. The report
has to say so; they must not be described as live AWS or LocalStack
measurements.

Baseline: Zhao, X., Guo, K., Huang, M., Qiu, S. and Lu, L. (2025) 'ELFA-Log:
cross-system log anomaly detection via enhanced pseudo-labeling and feature
alignment', *Computers*, 14(7), 272. https://doi.org/10.3390/computers14070272

Kasireddy Vadicharla
