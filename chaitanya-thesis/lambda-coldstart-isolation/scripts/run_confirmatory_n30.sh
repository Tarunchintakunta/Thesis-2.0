#!/usr/bin/env bash
# Chaitanya confirmatory full-scale (n>=30): baseline=default package vs proposed=optimised.
# Also H1 runtime_compare on proposed (optimised) only. Destroy-after. Uses credits usefully.
# Usage: bash scripts/run_confirmatory_n30.sh [round]
set -euo pipefail
ROUND="${1:-1}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT="results/live/confirmatory_n30/round_${ROUND}"
RAW="data/raw/live_conf_n30_r${ROUND}"
PROC="$OUT/processed"
LOG="/tmp/chaitanya_conf_n30_r${ROUND}.log"
mkdir -p "$OUT" "$RAW" "$PROC"
exec >>"$LOG" 2>&1
echo "=== CHAITANYA CONF_N30 ROUND_$ROUND START $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

PY=.venv/bin/python
[[ -x $PY ]] || PY=python3
export DATA_MODE=live PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export PATH="$ROOT/.venv/bin:$PATH"

cleanup() {
  echo "=== teardown $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  bash scripts/teardown.sh || true
}
trap cleanup EXIT

# Clean orphans from prior coldstart stacks
REGION=eu-west-1
for lg in $(aws logs describe-log-groups --region $REGION --log-group-name-prefix /aws/lambda/coldstart-study --query 'logGroups[].logGroupName' --output text 2>/dev/null); do
  aws logs delete-log-group --log-group-name "$lg" --region $REGION 2>/dev/null || true
done

bash scripts/deploy.sh

# H2: package_size — baseline=default, proposed=optimised (drop bytecode)
# reps=30 satisfies analysis_plan min_n_per_cell
echo "=== package_size reps=30 (baseline=default vs proposed=optimised) ==="
DATA_MODE=live "$PY" scripts/invoke_idle.py \
  --phase package_size --reps 30 \
  --variant default,optimised \
  --out "$RAW"

# H1: runtime_compare on proposed (optimised) only
echo "=== runtime_compare reps=30 (proposed=optimised across runtimes) ==="
DATA_MODE=live "$PY" scripts/invoke_idle.py \
  --phase runtime_compare --reps 30 \
  --variant optimised \
  --out "$RAW"

echo "=== collect/parse/cost/analyse ==="
DATA_MODE=live "$PY" scripts/collect_logs.py --runs "$RAW"
DATA_MODE=live "$PY" scripts/parse_report_metrics.py --in "$RAW" --out "$PROC/metrics.csv"
DATA_MODE=live "$PY" scripts/cost_model.py --in "$PROC/metrics.csv" --out "$PROC/costs.csv"
DATA_MODE=live "$PY" scripts/analyse.py --in "$PROC" --out "$OUT/figures" "$OUT/tables" || true

echo "baseline=default package; proposed=optimised package; H1 on proposed runtimes" > "$OUT/PROVENANCE.txt"
echo "reps=30; destroy-after; round=$ROUND" >> "$OUT/PROVENANCE.txt"
date -u +%Y-%m-%dT%H:%M:%SZ >> "$OUT/PROVENANCE.txt"
echo "destroy_confirmed=pending_trap" > "$OUT/destroy_confirmed.txt"

# teardown via trap
echo "CHAITANYA_CONF_N30_R${ROUND}_DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)"
