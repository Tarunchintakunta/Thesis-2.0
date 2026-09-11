#!/usr/bin/env bash
# Phase A/B/C traffic + logs.
#   scripts/02_generate_traffic.sh                    emulator, configs/experiment.yaml (default)
#   CONFIG=configs/smoke.yaml scripts/02_generate_traffic.sh
#   MODE=live API_URL=https://... scripts/02_generate_traffic.sh   (LocalStack / own account)
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
CONFIG=${CONFIG:-configs/experiment.yaml}
MODE=${MODE:-emulator}

if [ "$MODE" = "emulator" ]; then
  NAME=$($PY -c "import yaml,sys; print(yaml.safe_load(open('$CONFIG'))['name'])")
  $PY -m logad.collect.generate --config "$CONFIG" --out "data/raw/$NAME"
else
  : "${API_URL:?set API_URL to the deployed HTTP API}"
  $PY -m logad.collect.live_traffic --config "${CONFIG/experiment/live}" --api-url "$API_URL" --out data/raw/live
fi
