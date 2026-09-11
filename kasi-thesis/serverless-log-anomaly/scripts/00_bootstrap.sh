#!/usr/bin/env bash
# One-time setup: virtualenv, pinned dependencies, the package itself, Loghub sample.
#   scripts/00_bootstrap.sh              (python3.11 or python3.12)
set -euo pipefail
cd "$(dirname "$0")/.."

PY=${PYTHON:-$(command -v python3.11 || command -v python3.12 || command -v python3)}
[ -d .venv ] || "$PY" -m venv .venv
.venv/bin/pip install -q -U pip
.venv/bin/pip install -q -r requirements-dev.txt
.venv/bin/pip install -q -e .
mkdir -p data/raw data/interim data/processed results
scripts/fetch_loghub.sh
echo "bootstrap done - next: make test && make smoke"
