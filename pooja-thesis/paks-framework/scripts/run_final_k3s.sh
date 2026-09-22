#!/usr/bin/env bash
# One Pooja live k3s final round: apply → live HPA vs PAKS → destroy → park results.
set -euo pipefail
ROUND="${1:?round number}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT="results/live/final_${ROUND}"
LOG="/tmp/pooja_final_${ROUND}.log"
mkdir -p "$OUT"
# Plain redirect (no process-substitution tee) — survives nohup/SIGHUP better.
exec >>"$LOG" 2>&1
echo "=== POOJA FINAL_$ROUND START $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

PY=python3
# Prefer local venv if present
[[ -x .venv/bin/python ]] && PY=.venv/bin/python

# Vary seed slightly per round for independence (same protocol)
export PAKS_LIVE_SEED=$((40 + ROUND))

"$PY" scripts/run_live_aws_k8s.py --steps 16 --max-replicas 3

# Park artefacts
cp -f results/formal_k8s_live_aws.json "$OUT/"
cp -f results/aws_destroy_verify.json "$OUT/" 2>/dev/null || true
cp -f results/aws_live_run_summary.json "$OUT/" 2>/dev/null || true
echo "round=final_${ROUND}" > "$OUT/PROVENANCE.txt"
echo "protocol=1xt3.micro+k3s HPA vs PAKS; steps=16; destroy-after" >> "$OUT/PROVENANCE.txt"
date -u +%Y-%m-%dT%H:%M:%SZ >> "$OUT/PROVENANCE.txt"

# Annotate JSON with round
"$PY" - <<PY
import json
from pathlib import Path
p = Path("$OUT/formal_k8s_live_aws.json")
data = json.loads(p.read_text())
data["round"] = "final_$ROUND"
data["seed"] = int("$PAKS_LIVE_SEED")
p.write_text(json.dumps(data, indent=2, default=str) + "\n")
print("annotated", p)
PY

echo "POOJA_FINAL_${ROUND}_DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)"
