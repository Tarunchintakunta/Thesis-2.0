#!/usr/bin/env bash
# One Uday MQTT lite final: terraform apply → lite 16-cell → destroy → park.
set -euo pipefail
ROUND="${1:?}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT="results/live/final_${ROUND}"
LOG="/tmp/uday_final_${ROUND}.log"
mkdir -p "$OUT"
exec >>"$LOG" 2>&1
echo "=== UDAY FINAL_$ROUND START $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

PY=python3
[[ -x .venv/bin/python ]] && PY=.venv/bin/python

export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-eu-west-1}"
STAGE=lite
DEVICE_COUNT=5

"$PY" scripts/assert_free_tier_guard.py --mode lite
"$PY" scripts/check_ready_for_aws.py

# Ensure clean certs dir for this round
rm -rf .certs
mkdir -p .certs

cd terraform
terraform init -input=false
terraform apply -auto-approve -input=false \
  -var="enable_apply=true" \
  -var="device_count=${DEVICE_COUNT}" \
  -var="stage=${STAGE}" \
  -var="region=${AWS_DEFAULT_REGION}"
cd ..

[[ -f .certs/stack_meta.json ]] || { echo "missing stack_meta after apply"; exit 1; }

# Fresh live out for this round (keep archive/initial_eval)
mkdir -p results/live
rm -f results/live/LIVE_EVIDENCE.json
# Avoid mixing delivered/device_log across rounds in the shared tree
rm -rf results/live/delivered results/live/device_log results/live/manifests
mkdir -p results/live/delivered results/live/device_log results/live/manifests

"$PY" scripts/run_live.py --scale lite --out results/live

# Always destroy
bash scripts/destroy_stack.sh

mkdir -p "$OUT"
cp -f results/live/LIVE_EVIDENCE.json "$OUT/"
cp -R results/live/delivered "$OUT/" 2>/dev/null || true
cp -R results/live/device_log "$OUT/" 2>/dev/null || true
cp -R results/live/manifests "$OUT/" 2>/dev/null || true

"$PY" - <<PY
import json
from pathlib import Path
from datetime import datetime, timezone
p = Path("$OUT/LIVE_EVIDENCE.json")
data = json.loads(p.read_text())
data["round"] = "final_$ROUND"
data["collected_at"] = datetime.now(timezone.utc).isoformat()
# attach destroy confirmation from destroy_stack echo path if present
ds = data.get("destroy_status") or {}
ds.setdefault("round_script_destroy", True)
data["destroy_status"] = ds
p.write_text(json.dumps(data, indent=2) + "\n")
print("n_cells", data.get("n_cells"), "n_runs", data.get("n_runs"))
PY

echo "destroy_confirmed=yes" > "$OUT/destroy_confirmed.txt"
echo "round=final_${ROUND}" > "$OUT/PROVENANCE.txt"
echo "protocol=mqtt lite 16-cell device_count=5; destroy-after" >> "$OUT/PROVENANCE.txt"
date -u +%Y-%m-%dT%H:%M:%SZ >> "$OUT/PROVENANCE.txt"
echo "UDAY_FINAL_${ROUND}_DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)"
