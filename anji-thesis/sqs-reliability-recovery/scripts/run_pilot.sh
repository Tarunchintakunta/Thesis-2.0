#!/usr/bin/env bash
# Pilot runs on live AWS (deployed stack required).
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
EXTRA=(--live)
$PY -m src.control.experiment_runner --config configs/pilot.yaml --out results/pilot "${EXTRA[@]}" "$@"
