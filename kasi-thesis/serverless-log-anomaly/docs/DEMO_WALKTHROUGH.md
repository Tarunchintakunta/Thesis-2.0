# Demo walkthrough (artefact demo, 5-10 min)

Command-by-command runbook for showing the artefact. Everything runs locally.

## 0. Set up (before recording)

```bash
scripts/00_bootstrap.sh
source .venv/bin/activate
export PYTHONPATH=src
make test
```

## 1. The target application and its logs (2 min)

Show `infra/lambda_app/handler.py` (one JSON line per request) and generate a
small campaign:

```bash
python -m logad.collect.generate --config configs/smoke.yaml --out data/raw/demo
head -8 data/raw/demo/seed_7/phase_A.log
grep -m3 AccessDenied data/raw/demo/seed_7/phase_B.log
grep -m2 "Task timed out" data/raw/demo/seed_7/phase_B.log
head -5 data/raw/demo/seed_7/ground_truth.csv
```

Point out START / END / REPORT, the Init Duration on cold starts, and that the
ground truth is known because the faults were scheduled.

## 2. Scrubbing and the fixed parser (1 min)

```bash
make smoke          # runs pipeline + report on the smoke config
head results_smoke/tables/templates_seed_7.csv
cat results_smoke/parser_fingerprint.json
cat results_smoke/certification/seed_7.json
```

## 3. The three detectors on the same windows (2 min)

Open `docs/ARCHITECTURE.md` section 4, then:

```bash
python - <<'EOF'
import pandas as pd
B = pd.read_csv("results_smoke/metrics/windows_B_seed_7.csv")
print(B[["start", "label", "category", "pred_d1_primary", "pred_d2_transfer", "pred_d3_thresholds"]].iloc[20:40])
EOF
```

## 4. Results of the main run (2-3 min)

`results/tables/summary.md`, `results/tables/hypotheses.md` (H1-H3 and the
decision rule), then the figures: `f1_by_detector.png`, `f1_by_category.png`,
`elasticity_far.png`, `timeline_phase_B.png`.

## 5. Live path (optional, 1 min)

```bash
make localstack-up && make deploy-local
MODE=live API_URL=... scripts/02_generate_traffic.sh
```

(Show the scripts and `configs/live.yaml`; the live path is slow because it
runs in real time.)

Kasireddy Vadicharla
