# Lite Leg 3 — AWS overhead (Free-Tier–safe prep)

Sole CA2 AWS residual for Yashaswini: measured overhead under
`results/live/overhead.json` from three telemetry conditions on the live
faultlab stack (Lambda + API Gateway + DynamoDB + CloudWatch + X-Ray).

## Stack naming (collision-safe)

| Item | Value |
|------|-------|
| Terraform `name_prefix` | `faultlab` |
| Region | `eu-west-1` |
| Tags | `project=faultlab`, `managed_by=terraform`, `purpose=research-eval`, `data=synthetic` |
| Do **not** tag | student name or student ID |

Avoids collision with concurrent account work (`idem-eval-*`, `coldstart-study-*`, `sflad-*`, `ddbpk-*`).

## Lite plan vs full protocol

| | Full (`experiment.yaml`) | Lite (`experiment_lite_overhead.yaml`) |
|--|--|--|
| Conditions | full / policy / off | same |
| Minutes / condition | 30 | **5** |
| Steady RPS | 2 | **1** |
| Approx requests | ~10.8k | **~900** |
| Calibration / fault campaigns | required for full CA2 depth | **skipped** (overhead-only residual) |

Lite is directional measured evidence, not confirmatory 30-minute cells.

## Prerequisites

1. Account Lambda concurrency headroom (New accounts often have limit **10**).
   Do **not** apply while other campaigns hold most of the pool.
2. Packages: `make tf-package` → `build/*.zip`
3. `make tf-validate` then `cd terraform && terraform apply`

## Run (when concurrency is safe)

```bash
cd yashaswini-thesis/serverless-fault-localisation
make setup          # once
make tf-package && make tf-validate
cd terraform && terraform apply -auto-approve
# seed
python ../scripts/seed_inventory.py --table "$(terraform output -raw table_name)"
export API_URL="$(terraform output -raw api_url)"
cd ..

RUN=data/runs/live_lite_overhead
CFG=configs/experiment_lite_overhead.yaml

# For each condition: set tracing via terraform vars (or SAM param overrides), then:
# full:  -var='tracing_mode=Active' -var='log_level=INFO' -var='sampling_fixed_rate=1' -var='sampling_reservoir=1000'
# policy:-var='tracing_mode=Active' -var='log_level=ERROR' -var='sampling_fixed_rate=0.05' -var='sampling_reservoir=1'
# off:   -var='tracing_mode=PassThrough' -var='log_level=ERROR'

python scripts/campaign.py --phase overhead-full --url "$API_URL" --run "$RUN" --config "$CFG"
python scripts/collect_overhead.py --run "$RUN" --condition full --config "$CFG"
# ... overhead-policy, overhead-off ...
python scripts/collect_overhead.py --run "$RUN" --summarise --config "$CFG"
# writes results/live/overhead.json

cd terraform && terraform destroy -auto-approve
```

## Do not invent metrics

If apply is blocked (concurrency, missing packages, budget risk), document the
blocker in `_analysis_extract/reports/yashaswini_AWS_RESIDUAL.md` and stop.
Never fabricate overhead numbers.
