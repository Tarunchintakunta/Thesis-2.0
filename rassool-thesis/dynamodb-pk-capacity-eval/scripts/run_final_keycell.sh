#!/usr/bin/env bash
# Rasool final round: W3/W4 key-cells, seed 100k, unique table prefix, destroy trap.
set -euo pipefail
ROUND="${1:?}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY=.venv/bin/python
OUT="results/final_${ROUND}"
PREF="ddbpkf${ROUND}"
LOG="/tmp/rasool_final_${ROUND}.log"
mkdir -p "$OUT"
exec > >(tee -a "$LOG") 2>&1
echo "=== RASOOL FINAL_$ROUND START $(date -u +%Y-%m-%dT%H:%M:%SZ) prefix=$PREF ==="

DESTROYED=0
cleanup() {
  if [[ "$DESTROYED" -eq 1 ]]; then return 0; fi
  echo "=== CLEANUP destroy ==="
  cd "$ROOT/iac"
  terraform destroy -auto-approve -input=false || true
  DESTROYED=1
  mkdir -p "$ROOT/$OUT"
  echo "destroy_confirmed=yes" > "$ROOT/$OUT/destroy_confirmed.txt"
  cd "$ROOT"
  python3 - <<'PY'
from pathlib import Path
import re
p = Path("config/experiment.yaml")
t = p.read_text()
p.write_text(re.sub(r"table_prefix:.*", "table_prefix: ddbpk", t, count=1))
print("restored table_prefix=ddbpk")
PY
}
trap cleanup EXIT

python3 - <<PY
from pathlib import Path
import re
p = Path("config/experiment.yaml")
t = p.read_text()
p.write_text(re.sub(r"table_prefix:.*", "table_prefix: ${PREF}", t, count=1))
print("set table_prefix=${PREF}")
PY

"$PY" scripts/render_tfvars.py
bash scripts/build_lambda.sh
cd iac
terraform init -input=false
terraform apply -auto-approve -input=false -var seed_mode=true
cd ..

for t in ${PREF}-k1-ondemand ${PREF}-k1-provisioned ${PREF}-k2-ondemand ${PREF}-k2-provisioned ${PREF}-k3-ondemand ${PREF}-k3-provisioned; do
  for i in $(seq 1 36); do
    st=$(aws dynamodb describe-table --region eu-west-1 --table-name "$t" --query 'Table.TableStatus' --output text 2>/dev/null || echo MISSING)
    echo "table $t $st"
    [[ "$st" == "ACTIVE" ]] && break
    sleep 5
  done
done

# DESIGNS includes K4 but terraform only creates K1–K3
for design in K1 K2 K3; do
  d=$(echo "$design" | tr '[:upper:]' '[:lower:]')
  for mode in ondemand provisioned; do
    "$PY" -m workloads.seed.seed --table "${PREF}-${d}-${mode}" --design "$design" --orders 100000 --threads 4
  done
done
cd iac
terraform apply -auto-approve -input=false -var seed_mode=false
BUCKET="$(terraform output -raw results_bucket)"
cd ..

rm -rf "$OUT"
mkdir -p "$OUT"
"$PY" scripts/run_matrix.py --results-bucket "$BUCKET" --out "$OUT" \
  --blocks 1 --workloads W3,W4 --orders 100000

"$PY" scripts/collect_metrics.py --results "$OUT" || true
"$PY" analysis/analyse_keycell_n1.py --results "$OUT" --out "$OUT" || true

cleanup
trap - EXIT
echo "RASOOL_FINAL_${ROUND}_DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)"
