# mqtt-qos-iot-core

Formal CA2 artefact for Uday: **MQTT QoS 0 vs 1 loss under controlled disconnect on AWS IoT Core**.

Binding contract: `../CA2_COMMITMENTS.md`. Status: `STATUS.md`.

## Quick start (no AWS)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make test
make dry-run      # local mock factorial + Holm analysis
make plan-ft      # formal vs lite vs smoke free-tier reconciliation
make ready        # READY_FOR_AWS gate check
make live-dry     # gates + expand smoke specs; no AWS publish
```

## Live (lite/smoke only, after READY_FOR_AWS)

```bash
make ready
# terraform apply with -var=enable_apply=true -var=device_count=2 -var=stage=smoke
make live         # smoke campaign → results/live/
make destroy      # mandatory after campaign
```

Formal scale remains **blocked** (exceeds monthly IoT free tier).

## Layout

- `src/simulator/` — synthetic devices, disconnect windows, mock + live publishers
- `src/matching/` — device-log ↔ delivered match (loss/dup/latency)
- `src/analysis/` — cost surface, confirmatory stats (Holm), plots
- `src/lambda_ingest/` — IoT rule Lambda (stdlib + boto3)
- `configs/experiment.yaml` — dry_run / lite / smoke / formal
- `terraform/` — IoT Core + rule + Lambda + DynamoDB (`enable_apply=false` default)
- `scripts/run_live.py` — smoke/lite after gates; formal blocked

## Honesty

Mock results are **not** AWS measurements. Live smoke evidence (if present under `results/live/`) is a Free-Tier pilot, **not** formal-scale CA2 completion. Destroy after every apply.
