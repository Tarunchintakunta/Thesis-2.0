#!/usr/bin/env bash
# Faults are part of phase B.
#   emulator mode: nothing to do here - the schedule is applied inside
#                  logad.collect.generate (data/raw/<config>/seed_*/ground_truth.csv)
#   live mode:     logad.collect.live_traffic switches every fault on/off at the
#                  scheduled time through logad.inject.live.LiveFaultSwitch.
# This script prints the schedule and can flip one fault by hand for a demo:
#   scripts/03_inject_faults.sh show [seed]
#   ROLE=... scripts/03_inject_faults.sh on permission_denied
#   ROLE=... scripts/03_inject_faults.sh off
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
ACTION=${1:-show}

case "$ACTION" in
  show)
    SEED=${2:-2025}
    F=$(ls data/raw/*/seed_${SEED}/ground_truth.csv 2>/dev/null | head -1)
    [ -n "$F" ] || { echo "no ground truth yet - run scripts/02_generate_traffic.sh"; exit 1; }
    echo "$F"; head -13 "$F"; echo "..."; wc -l < "$F" | xargs echo "lines:"
    ;;
  on|off)
    : "${ROLE:?set ROLE to the function execution role name}"
    $PY - "$ACTION" "${2:-}" <<'EOF'
import os, sys, boto3
from logad.inject.live import LiveFaultSwitch
ep = os.environ.get("AWS_ENDPOINT_URL") or None
sw = LiveFaultSwitch(boto3.client("lambda", endpoint_url=ep), boto3.client("iam", endpoint_url=ep),
                     os.environ.get("FUNCTION", "kasireddy-orders"), os.environ["ROLE"],
                     os.environ.get("TABLE", "kasireddy-orders"))
if sys.argv[1] == "on":
    sw.on(sys.argv[2]); print("on:", sys.argv[2])
else:
    for cat in ("permission_denied", "config_error", "dependency_timeout", "resource_exhaustion"):
        sw.active = cat
        try:
            sw.off()
        except Exception as exc:  # nothing to undo for that category
            pass
    print("all faults off")
EOF
    ;;
  *) echo "usage: $0 show [seed] | on <category> | off"; exit 2 ;;
esac
