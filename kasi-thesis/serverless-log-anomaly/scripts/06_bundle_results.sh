#!/usr/bin/env bash
# Zip what the report needs (figures, tables, stats, fingerprint, certification)
# into dist/ so it can be attached to the submission or shared with the supervisor.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=${OUT:-results}
mkdir -p dist
STAMP=$(date -u +%Y%m%d)
ZIP="dist/results_bundle_${STAMP}.zip"
rm -f "$ZIP"
zip -qr "$ZIP" "$OUT/figures" "$OUT/tables" "$OUT/stats" "$OUT/metrics/summary.csv" \
  "$OUT/parser_fingerprint.json" "$OUT/certification" "$OUT/run_info.json" configs
echo "wrote $ZIP"
