# MHSA-TDL: Cross-Head Fusion for Multi-Head Attention Cluster Telemetry Monitoring

Mehak's MSc Cloud Computing thesis codebase. Reproduces the baseline architecture from
Thapliyal (2026), *"A Multi-Head Attention Approach for SLA Compliance Monitoring in
Data Centers"* (arXiv:2605.05354, IEEE ICDCS 2026), adapted from data-center SLA rules
to cluster telemetry (CPU, memory, disk, network), and evaluates a fix for a gap that
paper reports in its own results.

## The baseline paper's gap
Thapliyal's model gives each attention head strict, exclusive ownership of one metric
(power/temperature/humidity). Their results show the most volatile head (power)
systematically **underpredicts** severity during high-load transients — the authors
attribute this to heads never sharing information, even though the underlying metrics
are correlated.

## What this project does
1. **Reproduces** the strict one-head-per-metric architecture (`MHSAPerHead`) as a baseline, applied to cluster telemetry.
2. **Confirms the gap** on synthetic telemetry with injected cross-metric burst precursors, where predicting one metric's future violation sometimes requires reading a *different* metric's early signal.
3. **Fixes it** with a cross-head fusion layer (`MHSAFused`) that lets the per-metric head vectors attend to each other before classification.
4. Evaluates both, across 5 seeded training runs, against a reactive threshold-monitoring baseline.

**Result:** fusion gives a real but modest improvement on the targeted gap (transient
recall 86.4%→88.4%, underprediction bias 0.29→0.27) at a small accuracy cost — see
`../final_report.md` for full numbers and an honest discussion of an earlier, unseeded
run that overstated the effect.

## Project Structure
- `src/data/telemetry_simulator.py` — synthetic telemetry generator (history window in, future window labelled).
- `src/models/mhsa_model.py` — shared backbone, `MHSAPerHead` (baseline), `MHSAFused` (improved), `CrossHeadFusion` layer.
- `src/models/baseline.py` — reactive threshold monitor.
- `scripts/train_and_evaluate.py` — trains/evaluates all 3 approaches over 5 seeds, saves results + exports the deployable model.
- `src/lambda_handler/app.py` — real (not mocked) inference over a Kinesis telemetry stream, using the exported model.
- `template.yaml` — AWS SAM template (Kinesis stream + Lambda).
- `.github/workflows/deploy.yml` — CI: runs training/eval on every push, deploys the SAM stack to `main`.

## Usage
```bash
pip install -r requirements.txt
python scripts/train_and_evaluate.py
```
Results land in `results/results_per_seed.csv` and `results/results_summary.csv`. The
trained model used for deployment is saved to `src/lambda_handler/model/`.

## Known simplification
`torch` is a heavy dependency for a Lambda zip package. This repo keeps the code simple
and correct locally; for a real deployment you would package the Lambda as a container
image or put `torch` in a Lambda layer. The GitHub Actions workflow assumes you've set
`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION` as repository secrets.
