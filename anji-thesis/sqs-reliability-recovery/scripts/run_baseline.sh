#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
$PY -m src.control.experiment_runner --live --config configs/baseline_kyrchenko.yaml --out results/baseline "$@"
