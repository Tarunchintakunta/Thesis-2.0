#!/usr/bin/env bash
# Phase A clean train -> phase B inject + eval -> phase C elasticity, for every seed.
#   scripts/04_train_eval.sh
#   CONFIG=configs/smoke.yaml OUT=results_smoke scripts/04_train_eval.sh
set -euo pipefail
cd "$(dirname "$0")/.."
CONFIG=${CONFIG:-configs/experiment.yaml}
OUT=${OUT:-results}
.venv/bin/python -m logad.pipeline --config "$CONFIG" --out "$OUT"
