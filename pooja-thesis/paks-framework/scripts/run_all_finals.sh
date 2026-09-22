#!/usr/bin/env bash
# Chain Pooja final_1 → final_2 → final_3 (destroy each). Overnight driver.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
LOG=/tmp/pooja_finals.log
echo "POOJA_CHAIN_START $(date -u +%Y-%m-%dT%H:%M:%SZ) pid=$$" | tee -a "$LOG"
echo $$ > /tmp/pooja_finals.pid

cleanup_on_fail() {
  echo "POOJA_CHAIN_FAIL_CLEANUP $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG"
  (cd "$ROOT/terraform" && terraform destroy -auto-approve -input=false) >> "$LOG" 2>&1 || true
}

for r in 1 2 3; do
  echo "===== CHAIN final_$r $(date -u +%Y-%m-%dT%H:%M:%SZ) =====" >> "$LOG"
  if ! bash scripts/run_final_k3s.sh "$r" >> "$LOG" 2>&1; then
    echo "POOJA_FINAL_${r}_FAILED $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG"
    cleanup_on_fail
    exit 1
  fi
  echo "===== CHAIN final_$r OK $(date -u +%Y-%m-%dT%H:%M:%SZ) =====" >> "$LOG"
done
echo "POOJA_ALL_FINALS_DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG"
