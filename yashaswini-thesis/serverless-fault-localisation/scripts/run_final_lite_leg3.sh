#!/usr/bin/env bash
# One lite Leg-3 final round: apply → 3 overhead conditions → summarise → destroy.
set -euo pipefail
ROUND="${1:?round number}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
CFG=configs/experiment_lite_overhead.yaml
RUN="data/runs/live_final_${ROUND}"
OUT="results/live/final_${ROUND}"
LOG="/tmp/yash_final_${ROUND}.log"
mkdir -p "$RUN" "$OUT"
exec > >(tee -a "$LOG") 2>&1
echo "=== YASH FINAL_$ROUND START $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

python3() { "$ROOT/.venv/bin/python" "$@"; }
export -f python3 2>/dev/null || true
PY="$ROOT/.venv/bin/python"
bash scripts/package_terraform.sh
cd terraform
terraform init -input=false

apply_tracing() {
  local mode="$1" loglevel="$2" rate="$3" reservoir="$4"
  terraform apply -auto-approve -input=false \
    -var="tracing_mode=${mode}" \
    -var="log_level=${loglevel}" \
    -var="sampling_fixed_rate=${rate}" \
    -var="sampling_reservoir=${reservoir}"
}

# initial apply (full tracing)
apply_tracing Active INFO 1 1000
API_URL="$(terraform output -raw api_url)"
TABLE="$(terraform output -raw table_name)"
cd ..
"$PY" scripts/seed_inventory.py --table "$TABLE" || true
export API_URL

# full
"$PY" scripts/campaign.py --phase overhead-full --url "$API_URL" --run "$RUN" --config "$CFG"
"$PY" scripts/collect_overhead.py --run "$RUN" --condition full --config "$CFG"

# policy
cd terraform
apply_tracing Active ERROR 0.05 1
API_URL="$(terraform output -raw api_url)"
cd ..
export API_URL
"$PY" scripts/campaign.py --phase overhead-policy --url "$API_URL" --run "$RUN" --config "$CFG"
"$PY" scripts/collect_overhead.py --run "$RUN" --condition policy --config "$CFG"

# off
cd terraform
apply_tracing PassThrough ERROR 0.05 1
API_URL="$(terraform output -raw api_url)"
cd ..
export API_URL
"$PY" scripts/campaign.py --phase overhead-off --url "$API_URL" --run "$RUN" --config "$CFG"
"$PY" scripts/collect_overhead.py --run "$RUN" --condition off --config "$CFG"
"$PY" scripts/collect_overhead.py --run "$RUN" --summarise --config "$CFG"

# park summary into final_$ROUND
cp -f results/live/overhead.json "$OUT/overhead.json" 2>/dev/null || true
cp -f results/live/learned_lower_bound.csv "$OUT/" 2>/dev/null || true
"$PY" - <<PY
import json, pathlib, datetime
out=pathlib.Path("$OUT")
src=pathlib.Path("results/live/overhead.json")
if src.exists():
    data=json.loads(src.read_text())
    data["round"]=f"final_$ROUND"
    data["collected_at"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (out/"summary.json").write_text(json.dumps(data, indent=2)+"\n")
print("wrote", out)
PY

cd terraform
terraform destroy -auto-approve -input=false
cd ..
echo "YASH_FINAL_${ROUND}_DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)"
