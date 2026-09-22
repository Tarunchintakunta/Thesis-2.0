#!/usr/bin/env bash
# Chain Uday final_1 → final_2 → final_3.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
LOG=/tmp/uday_finals.log
echo "UDAY_CHAIN_START $(date -u +%Y-%m-%dT%H:%M:%SZ) pid=$$" | tee -a "$LOG"
echo $$ > /tmp/uday_finals.pid

cleanup_on_fail() {
  echo "UDAY_CHAIN_FAIL_CLEANUP $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG"
  bash "$ROOT/scripts/destroy_stack.sh" >> "$LOG" 2>&1 || true
}

for r in 1 2 3; do
  echo "===== CHAIN final_$r $(date -u +%Y-%m-%dT%H:%M:%SZ) =====" >> "$LOG"
  if ! bash scripts/run_final_lite.sh "$r" >> "$LOG" 2>&1; then
    echo "UDAY_FINAL_${r}_FAILED $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG"
    cleanup_on_fail
    exit 1
  fi
  echo "===== CHAIN final_$r OK $(date -u +%Y-%m-%dT%H:%M:%SZ) =====" >> "$LOG"
done
echo "UDAY_ALL_FINALS_DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG"
