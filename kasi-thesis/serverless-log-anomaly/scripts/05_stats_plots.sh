#!/usr/bin/env bash
# Metrics, H1-H3 (Holm), decision rule, tables and figures from the window CSVs.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=${OUT:-results}
.venv/bin/python -m logad.eval.report --results "$OUT"
