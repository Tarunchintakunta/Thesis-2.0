# mqtt-qos-iot-core

Formal CA2 artefact for Uday: **MQTT QoS 0 vs 1 loss under controlled disconnect on AWS IoT Core**.

Binding contract: `../CA2_COMMITMENTS.md`. Status: `STATUS.md`.

## Quick start (no AWS)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make test
make dry-run      # local mock factorial + Holm analysis
make analyse     # re-analyse results/mock
make live        # exits BLOCKED (intentional)
```

## Layout

- `src/simulator/` — synthetic devices, disconnect windows, mock broker/DDB
- `src/matching/` — device-log ↔ delivered match (loss/dup/latency)
- `src/analysis/` — cost surface, confirmatory stats (Holm), plots
- `src/lambda_ingest/` — IoT rule Lambda (stdlib + boto3)
- `configs/experiment.yaml` — dry_run vs formal factorial
- `terraform/` — IoT Core + rule + Lambda + DynamoDB (`enable_apply=false` default)
- `scripts/run_dry_run.py`, `analyse.py`, `run_live.py` (blocked), `plan_free_tier.py`

## Honesty

Mock results are **not** AWS measurements. Live apply is gated on `STATUS.md` → `READY_FOR_AWS`.
