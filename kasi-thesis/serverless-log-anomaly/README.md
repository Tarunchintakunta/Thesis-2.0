# Source-free log anomaly detection on AWS serverless logs

MSc in Cloud Computing - Research Project artefact, National College of Ireland
**Title:** Source-Free Log Anomaly Detection for AWS Serverless Applications: Measuring the Accuracy Forfeited When No Labelled Source Exists
**Student:** Kasireddy Vadicharla (25104047)

**Research question:** how much F1 does a source-free one-class detector
forfeit, relative to a transfer-based detector supplied with a labelled public
source (ELFA-Log procedure, Zhao et al., 2025), on the same serverless
application's CloudWatch logs under faults from a published serverless fault
distribution - and how do both compare to CloudWatch threshold alarms under
benign elasticity?

## Quick start

```bash
scripts/00_bootstrap.sh     # venv, pinned deps (drain3 0.9.11), Loghub BGL sample (checksum verified)
make test                   # unit + integration tests
make smoke                  # whole chain on a tiny config (seconds)
make run report             # the real study: 3 seeds x (24 h clean + 240 injections + 6 h elasticity)
```

Everything runs locally on a Lambda runtime emulator - no Docker, no AWS
account, no cost. A LocalStack / own-account path exists too
(`docs/config_manual/CONFIG_MANUAL.md` section 6).

## Layout

```text
serverless-log-anomaly/
├── infra/lambda_app/        Orders API Lambda (handler.py) + SAM template
├── infra/localstack/        pinned LocalStack compose file
├── src/logad/
│   ├── collect/             runtime emulator, workload, fake DynamoDB, scrubbing, CloudWatch collector, live runner
│   ├── inject/              4 fault categories, blocked schedule (ground truth), live fault switch
│   ├── parse/               fixed + fingerprinted Drain parser
│   ├── features/            60 s windows: count view (D1), semantic view (D2)
│   ├── source/              Loghub BGL reader
│   ├── detectors/           D1 OC-SVM + Isolation Forest, D2 ELFA-Log style transfer, D3 threshold alarms
│   ├── eval/                metrics, paired statistics, figures, report
│   └── pipeline.py          end-to-end run per seed
├── configs/                 experiment, drain (fixed), detectors, alarms, smoke, live, sensitivity
├── scripts/                 00_bootstrap ... 06_bundle_results, fetch_loghub
├── results/                 main run: window predictions, tables, stats, figures, fingerprint, certificates
├── results_sensitivity/     robustness run with background throttling
├── docs/                    config manual, architecture, demo walkthrough, ethics notes, weekly template, report notes
└── tests/                   unit + integration (smoke pipeline, moto)
```

## Results

> **All numbers below come from logs produced by the local Lambda runtime
> emulator (the real handler code, simulated AWS around it). They are not
> live AWS or LocalStack measurements.** 3 seeds, 720 injected faults, 60
> blocks, ~1.2 million log lines per run.

### Main (pre-registered) run - `results/`

| Detector | Precision | Recall | F1 [95 % CI] | FAR phase C (elasticity) | FAR in bursts |
|----------|-----------|--------|--------------|--------------------------|---------------|
| D1 source-free, OC-SVM (primary) | 0.958 | 0.863 | **0.908** [0.892, 0.924] | 9.1 % | 36.8 % |
| D1 source-free, Isolation Forest | 0.711 | 0.048 | 0.090 [0.070, 0.112] | 10.2 % | 71.5 % |
| D2 transfer (ELFA-Log style) | 0.826 | 0.847 | **0.836** [0.785, 0.887] | 24.7 % | 0 % |
| D3 threshold alarms | 1.000 | 0.880 | **0.936** [0.923, 0.947] | 0 % | 0 % |

* **H1** (F1 source-free = transfer): not rejected - Wilcoxon on 60 block
  pairs, p = 0.132, rank-biserial r = 0.23. The source-free OC-SVM is in fact
  7 F1 points *above* the transfer detector here.
* **H2** (F1 equal across fault categories): rejected for all three approaches
  (Friedman, Holm p < 0.001). Source-free is weakest on permission denial (only
  the write route fails), transfer on configuration errors.
* **H3** (elasticity false-alarm rate equal across approaches): rejected
  (Friedman chi2 = 42.0, Holm p < 0.001, Kendall's W = 0.58). The source-free
  detector's false alarms are concentrated in scale-up bursts - benign
  elasticity looks like an anomaly to it.
* **Decision rule:** within 10 F1 points of transfer - yes; better than the
  threshold alarms - no. **Pre-registered verdict: not a viable substitute**
  (the plain alarms beat both learned detectors).
* Transfer is unstable across seeds: entropy-based pseudo-labelling snowballed
  for seed 2027 (1,005 pseudo-labels by round 3 vs 43-49 for the other seeds),
  giving 69 % false alarms in phase C for that seed and 0-5 % for the others.
* Isolation Forest is nearly blind in this setting: it cannot split on a
  feature that was constant in the clean training period (never-seen
  templates, error lines). This is why the D1 primary model was fixed to the
  OC-SVM after the pilot (see `configs/detectors.yaml`).

### Sensitivity run - `results_sensitivity/background/`

The emulated system never returns a 5xx in normal operation, which makes the
alarms look perfectly precise. With 0.2 % background throttling added
(`configs/sensitivity_background.yaml`): D1 F1 0.960, D2 0.663, D3 0.912, and
the decision rule **flips to "viable substitute"**. The verdict therefore
depends on how noisy the real system is - that is a discussion point, not a
settled answer.

Full tables: `results/tables/summary.md`, `per_category.md`, `hypotheses.md`;
figures in `results/figures/`.

## Status

- [x] Orders API Lambda, SAM template (cfn-lint clean), LocalStack compose
- [x] runtime emulator, fixed parser, three detectors, fault injection, evaluation
- [x] tests (unit + integration) and GitHub Actions CI
- [x] main study (3 seeds) + sensitivity run - **emulated logs**
- [ ] live run on LocalStack / own AWS account (implemented and moto-tested, not executed)
- [ ] research report (NCI template, see `docs/report/README.md`)
- [ ] weekly activity reports (fill in `docs/weekly_activity/WEEK_TEMPLATE.md`)

## Baseline

Zhao, X., Guo, K., Huang, M., Qiu, S. and Lu, L. (2025) 'ELFA-Log: cross-system
log anomaly detection via enhanced pseudo-labeling and feature alignment',
*Computers*, 14(7), 272. https://doi.org/10.3390/computers14070272

Kasireddy Vadicharla
