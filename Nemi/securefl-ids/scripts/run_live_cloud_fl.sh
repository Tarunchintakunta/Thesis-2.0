#!/usr/bin/env bash
# Apply lite cloud FL (EC2 t3.micro + S3 + CloudWatch), collect metrics, destroy.
# Never uses Lambda (Vikas campaign_r5 occupies ConcurrentExecutions).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TF_DIR="${ROOT}/terraform"
REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-eu-west-1}}"
export AWS_DEFAULT_REGION="$REGION"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="${OUT_DIR:-${ROOT}/results/live}"
mkdir -p "$OUT_DIR"
APPLY_OK=0
DESTROY_OK=0
INSTANCE_ID=""
BUCKET=""
LOG_GROUP=""

log() { printf '[live-fl] %s\n' "$*"; }

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "missing $1" >&2; exit 2; }
}
need_cmd aws
need_cmd terraform
need_cmd python3
need_cmd tar

check_vikas_lambda() {
  log "Checking Vikas campaign_r5 Lambda use (idem-eval-fn) before apply"
  local end start stats conc
  end="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  if date -u -v-10M +%Y-%m-%dT%H:%M:%SZ >/dev/null 2>&1; then
    start="$(date -u -v-10M +%Y-%m-%dT%H:%M:%SZ)"
  else
    start="$(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%SZ)"
  fi
  stats="$(aws cloudwatch get-metric-statistics \
    --region "$REGION" \
    --namespace AWS/Lambda \
    --metric-name Invocations \
    --dimensions Name=FunctionName,Value=idem-eval-fn \
    --start-time "$start" --end-time "$end" \
    --period 60 --statistics Sum \
    --query 'sum(Datapoints[].Sum)' --output text 2>/dev/null || echo 0)"
  conc="$(aws cloudwatch get-metric-statistics \
    --region "$REGION" \
    --namespace AWS/Lambda \
    --metric-name ConcurrentExecutions \
    --start-time "$start" --end-time "$end" \
    --period 60 --statistics Maximum \
    --query 'max(Datapoints[].Maximum)' --output text 2>/dev/null || echo 0)"
  log "idem-eval-fn Invocations(10m sum)=${stats} ConcurrentExecutions(max)=${conc}"
  log "Nemi path is EC2+S3+CW only — Lambda not used, apply may proceed"
  printf '%s\n' "$stats" > "${OUT_DIR}/vikas_lambda_invocations_10m.txt"
  printf '%s\n' "$conc" > "${OUT_DIR}/lambda_conc_max_10m.txt"
}

prepare_lite_csv() {
  local dest="${ROOT}/data/unsw_lite_cloud.csv"
  python3 - "$dest" <<'PY'
import os, sys
from pathlib import Path
dest = Path(sys.argv[1])
dest.parent.mkdir(parents=True, exist_ok=True)
candidates = [
    dest.parent / "UNSW_NB15_training-set.csv",
    Path("/Users/valletivarish/Documents/Thesis-2.0/Nemi/securefl-ids/data/UNSW_NB15_training-set.csv"),
]
src = next((p for p in candidates if p.exists()), None)
if src is None:
    import numpy as np, pandas as pd
    n = 2500
    rng = np.random.default_rng(42)
    df = pd.DataFrame({f"f{i}": rng.normal(size=n) for i in range(20)})
    df["label"] = np.concatenate([np.zeros(int(n * 0.8), dtype=int), np.ones(n - int(n * 0.8), dtype=int)])
    df = df.sample(frac=1.0, random_state=42)
    df.to_csv(dest, index=False)
    print(f"synthetic lite csv -> {dest} rows={len(df)}")
else:
    import pandas as pd
    df = pd.read_csv(src)
    label = "label" if "label" in df.columns else df.columns[-1]
    parts = []
    for _, g in df.groupby(label):
        n = min(len(g), 1250)
        parts.append(g.sample(n=n, random_state=42) if n else g)
    out = pd.concat(parts, ignore_index=True).sample(frac=1.0, random_state=42)
    out.to_csv(dest, index=False)
    print(f"real-lite csv from {src} -> {dest} rows={len(out)} cols={out.shape[1]}")
PY
}

package_artefact() {
  local tgz="${OUT_DIR}/artefact-${RUN_ID}.tgz"
  tar -C "$ROOT" -czf "$tgz" \
    --exclude '.venv' --exclude '.pytest_cache' --exclude 'terraform/.terraform' \
    --exclude 'results' --exclude 'figures' --exclude '__pycache__' \
    src scripts/run_cloud_lite.py scripts/bootstrap_cloud.sh data/unsw_lite_cloud.csv
  echo "$tgz"
}

wait_ssm() {
  local id="$1"
  local i
  for i in $(seq 1 36); do
    local ping
    ping="$(aws ssm describe-instance-information --region "$REGION" \
      --filters "Key=InstanceIds,Values=${id}" \
      --query 'InstanceInformationList[0].PingStatus' --output text 2>/dev/null || echo None)"
    log "SSM ping=${ping} (try ${i}/36)"
    if [[ "$ping" == "Online" ]]; then
      return 0
    fi
    sleep 10
  done
  echo "SSM never Online for $id" >&2
  return 1
}

destroy_stack() {
  log "terraform destroy"
  if terraform -chdir="$TF_DIR" destroy -auto-approve -input=false; then
    DESTROY_OK=1
  else
    DESTROY_OK=0
    log "WARN terraform destroy failed — attempting targeted cleanup"
  fi
}

verify_gone() {
  local leftover_ec2 leftover_bucket
  leftover_ec2="$(aws ec2 describe-instances --region "$REGION" \
    --filters "Name=tag:project,Values=securefl-ids" "Name=instance-state-name,Values=pending,running,stopping" \
    --query 'Reservations[].Instances[].InstanceId' --output text)"
  leftover_bucket="$(aws s3api list-buckets --query 'Buckets[?starts_with(Name, `securefl-ids-artifacts-`)].Name' --output text)"
  if [[ -n "${leftover_ec2// /}" ]]; then
    log "WARN leftover EC2: $leftover_ec2"
    return 1
  fi
  if [[ -n "${leftover_bucket// /}" ]]; then
    log "WARN leftover buckets: $leftover_bucket"
    return 1
  fi
  log "destroy verify: no securefl-ids EC2/S3 leftovers"
  return 0
}

patch_destroy_status() {
  local summary="$1"
  local verify_ok="$2"
  python3 - "$summary" "$DESTROY_OK" "$verify_ok" <<'PY'
import json, sys
from datetime import datetime, timezone
path, destroy_ok, verify_ok = sys.argv[1], sys.argv[2] == "1", sys.argv[3] == "1"
with open(path) as f:
    data = json.load(f)
data["destroy_after"] = True
data["destroy_status"] = {
    "terraform_destroy": "complete" if destroy_ok else "failed",
    "verified_absent": bool(verify_ok),
    "destroyed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "lambda_used": False,
}
with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
print(f"patched destroy_status into {path}")
PY
}

trap 'if [[ "$APPLY_OK" == "1" && "$DESTROY_OK" == "0" ]]; then log "trap: destroying leftover stack"; destroy_stack || true; fi' EXIT

check_vikas_lambda
prepare_lite_csv
TGZ="$(package_artefact)"

log "terraform init/apply (region=$REGION run_id=$RUN_ID)"
terraform -chdir="$TF_DIR" init -input=false
terraform -chdir="$TF_DIR" apply -auto-approve -input=false \
  -var="region=${REGION}" \
  -var="instance_type=t3.micro" \
  -var="client_count=0" \
  -var="create_server=true"
APPLY_OK=1

INSTANCE_ID="$(terraform -chdir="$TF_DIR" output -raw server_id)"
BUCKET="$(terraform -chdir="$TF_DIR" output -raw artifacts_bucket)"
LOG_GROUP="$(terraform -chdir="$TF_DIR" output -raw log_group)"
log "server=$INSTANCE_ID bucket=$BUCKET log_group=$LOG_GROUP"

aws s3 cp "$TGZ" "s3://${BUCKET}/lite/${RUN_ID}/artefact.tgz"
wait_ssm "$INSTANCE_ID"

# IAM instance-profile attach can lag a few seconds after SSM is Online.
sleep 15

SSM_PARAMS="${OUT_DIR}/ssm_params_${RUN_ID}.json"
python3 - "$SSM_PARAMS" "$BUCKET" "$REGION" "$LOG_GROUP" "$RUN_ID" <<'PY'
import json, sys
path, bucket, region, log_group, run_id = sys.argv[1:]
payload = {
    "commands": [
        "set -euxo pipefail",
        f"aws s3 cp s3://{bucket}/lite/{run_id}/artefact.tgz /tmp/securefl-artefact.tgz",
        "rm -rf /opt/securefl-ids",
        "mkdir -p /opt/securefl-ids",
        "tar -xzf /tmp/securefl-artefact.tgz -C /opt/securefl-ids",
        "chmod +x /opt/securefl-ids/scripts/bootstrap_cloud.sh",
        f"/opt/securefl-ids/scripts/bootstrap_cloud.sh {bucket} {region} {log_group} {run_id}",
    ]
}
with open(path, "w", encoding="utf-8") as fh:
    json.dump(payload, fh)
PY

CMD_ID="$(aws ssm send-command --region "$REGION" \
  --instance-ids "$INSTANCE_ID" \
  --document-name "AWS-RunShellScript" \
  --comment "securefl-ids lite cloud FL ${RUN_ID}" \
  --timeout-seconds 2400 \
  --parameters "file://${SSM_PARAMS}" \
  --query 'Command.CommandId' --output text)"
log "ssm command=$CMD_ID"

for i in $(seq 1 80); do
  STATUS="$(aws ssm get-command-invocation --region "$REGION" \
    --command-id "$CMD_ID" --instance-id "$INSTANCE_ID" \
    --query 'Status' --output text 2>/dev/null || echo Pending)"
  log "ssm status=${STATUS} (${i}/80)"
  case "$STATUS" in
    Success) break ;;
    Failed|Cancelled|TimedOut) 
      aws ssm get-command-invocation --region "$REGION" \
        --command-id "$CMD_ID" --instance-id "$INSTANCE_ID" \
        --query '{Status:Status,Stdout:StandardOutputContent,Stderr:StandardErrorContent}' \
        --output json | tee "${OUT_DIR}/ssm_failure_${RUN_ID}.json"
      echo "SSM command $STATUS" >&2
      destroy_stack
      verify_gone || true
      exit 1
      ;;
  esac
  sleep 15
done

SUMMARY_S3="s3://${BUCKET}/lite/${RUN_ID}/cloud_lite_summary.json"
aws s3 cp "$SUMMARY_S3" "${OUT_DIR}/cloud_lite_summary.json"
aws s3 cp "$SUMMARY_S3" "${OUT_DIR}/cloud_lite_summary_${RUN_ID}.json"
cp "${OUT_DIR}/cloud_lite_summary.json" "${OUT_DIR}/cloud_lite_raw.json" || true

# Capture a few S3 keys and CW confirmation before destroy.
aws s3 ls "s3://${BUCKET}/lite/${RUN_ID}/" --recursive > "${OUT_DIR}/s3_listing_${RUN_ID}.txt" || true

destroy_stack
VERIFY=1
verify_gone || VERIFY=0
patch_destroy_status "${OUT_DIR}/cloud_lite_summary.json" "$VERIFY"
cp "${OUT_DIR}/cloud_lite_summary.json" "${OUT_DIR}/cloud_lite_summary_${RUN_ID}.json"

python3 - "${OUT_DIR}/cloud_lite_summary.json" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
arms = d.get("arms") or {}
print("METRICS_PATH", p)
print("MODE", d.get("mode"), "ELAPSED_S", round(float(d.get("elapsed_s", 0)), 2))
for name, arm in arms.items():
    s = arm.get("summary") or {}
    print(f"ARM {name} acc={s.get('accuracy')} f1={s.get('f1_score')} comm={s.get('avg_communication_cost')}")
ds = d.get("destroy_status") or {}
print("DESTROY", ds.get("terraform_destroy"), "VERIFIED_ABSENT", ds.get("verified_absent"))
PY

log "lite cloud FL complete"
