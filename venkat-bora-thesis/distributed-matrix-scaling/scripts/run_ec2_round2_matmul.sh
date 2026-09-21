#!/usr/bin/env bash
# Round-2: multi-instance da.matmul on matched-vCPU EC2 (eu-west-1).
# Topology: 1× t3.small (scale-up) vs 2× t3.micro (scale-out). Destroy after.
set -euo pipefail

REGION="${REGION:-eu-west-1}"
MATRIX_SIZE="${MATRIX_SIZE:-250}"
BENCH_TIMEOUT="${BENCH_TIMEOUT:-600}"
SSM_TIMEOUT="${SSM_TIMEOUT:-720}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTDIR="${OUTDIR:-$ROOT/results/live}"
TFDIR="$ROOT/terraform"
mkdir -p "$OUTDIR"

need() { command -v "$1" >/dev/null || { echo "missing $1" >&2; exit 1; }; }
need aws
need terraform
need python3
need jq

cd "$TFDIR"
UP="$(terraform output -raw scale_up_instance_id)"
SCHED="$(terraform output -json scale_out_instance_ids | jq -r '.[0]')"
WORK="$(terraform output -json scale_out_instance_ids | jq -r '.[1]')"
SG="$(terraform output -raw security_group_id)"

echo "UP=$UP SCHED=$SCHED WORK=$WORK SG=$SG size=$MATRIX_SIZE"

# Ephemeral worker ports (Dask needs more than 8786/8787).
aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$SG" \
  --ip-permissions "IpProtocol=tcp,FromPort=0,ToPort=65535,UserIdGroupPairs=[{GroupId=$SG,Description=dask-ephemeral}]" \
  >/dev/null 2>&1 || true

wait_ssm() {
  local id=$1
  for i in $(seq 1 40); do
    ping="$(aws ssm describe-instance-information --region "$REGION" \
      --filters "Key=InstanceIds,Values=$id" \
      --query 'InstanceInformationList[0].PingStatus' --output text 2>/dev/null || true)"
    echo "ssm $id try=$i ping=${ping:-none}"
    [[ "$ping" == "Online" ]] && return 0
    sleep 15
  done
  return 1
}

wait_ready() {
  local id=$1
  for i in $(seq 1 40); do
    cid=$(aws ssm send-command --region "$REGION" --instance-ids "$id" \
      --document-name AWS-RunShellScript --timeout-seconds 60 \
      --parameters 'commands=["test -f /opt/matrix-scale/READY && python3.11 -c \"import dask,numpy; print(\\\"READY\\\")\" 2>/dev/null || (ls -la /opt/matrix-scale 2>/dev/null; python3.11 -c \"import dask,numpy\" 2>&1 | head -2; echo NOTREADY)"]' \
      --query Command.CommandId --output text)
    sleep 4
    out=$(aws ssm get-command-invocation --region "$REGION" --command-id "$cid" --instance-id "$id" \
      --query '[Status,StandardOutputContent]' --output text 2>&1 || true)
    echo "$id ready_try=$i ${out:0:180}"
    echo "$out" | grep -q READY && return 0
    # Bootstrap if user_data stalled
    if echo "$out" | grep -q NOTREADY; then
      aws ssm send-command --region "$REGION" --instance-ids "$id" \
        --document-name AWS-RunShellScript --timeout-seconds 600 \
        --parameters 'commands=["set -euxo pipefail","dnf -y install python3.11 python3.11-pip python3.11-devel gcc || yum -y install python3 python3-pip gcc || true","python3.11 -m pip install --upgrade pip","python3.11 -m pip install '\''numpy==2.1.3'\'' '\''dask[distributed]==2024.11.2'\'' psutil","mkdir -p /opt/matrix-scale","echo ready > /opt/matrix-scale/READY"]' \
        --query Command.CommandId --output text >/tmp/venkat_bootstrap_$id.txt || true
    fi
    sleep 20
  done
  return 1
}

wait_ssm "$UP"
wait_ssm "$SCHED"
wait_ssm "$WORK"
wait_ready "$UP"
wait_ready "$SCHED"
wait_ready "$WORK"

IPS=$(aws ec2 describe-instances --region "$REGION" --instance-ids "$SCHED" "$WORK" \
  --query 'Reservations[].Instances[].[InstanceId,PrivateIpAddress]' --output text)
SCHED_IP=$(echo "$IPS" | awk -v id="$SCHED" '$1==id{print $2}')
WORK_IP=$(echo "$IPS" | awk -v id="$WORK" '$1==id{print $2}')
echo "sched_ip=$SCHED_IP work_ip=$WORK_IP"

# Restart Dask cluster (scheduler + 2 workers across instances).
aws ssm send-command --region "$REGION" --instance-ids "$SCHED" "$WORK" \
  --document-name AWS-RunShellScript --timeout-seconds 60 \
  --parameters 'commands=["pkill -f dask-scheduler || true","pkill -f dask-worker || true"]' \
  --query Command.CommandId --output text >/dev/null
sleep 5

CID_S=$(aws ssm send-command --region "$REGION" --instance-ids "$SCHED" \
  --document-name AWS-RunShellScript --timeout-seconds 120 \
  --parameters 'commands=["nohup python3.11 -m distributed.cli.dask_scheduler --host 0.0.0.0 --port 8786 --dashboard-address :8787 >/tmp/dask-sched.log 2>&1 &","sleep 4","ss -ltn | grep 8786 || netstat -ltn | grep 8786","echo SCHED_UP"]' \
  --query Command.CommandId --output text)
sleep 8
aws ssm get-command-invocation --region "$REGION" --command-id "$CID_S" --instance-id "$SCHED" \
  --query '[Status,StandardOutputContent]' --output text | tee "$OUTDIR/round2_sched.out"

CID_W=$(aws ssm send-command --region "$REGION" --instance-ids "$WORK" \
  --document-name AWS-RunShellScript --timeout-seconds 120 \
  --parameters "commands=[\"nohup python3.11 -m distributed.cli.dask_worker tcp://${SCHED_IP}:8786 --nthreads 1 --memory-limit 0.8 --no-dashboard >/tmp/dask-worker.log 2>&1 &\",\"sleep 5\",\"tail -n 30 /tmp/dask-worker.log\",\"echo WORKER_UP\"]" \
  --query Command.CommandId --output text)
sleep 10
aws ssm get-command-invocation --region "$REGION" --command-id "$CID_W" --instance-id "$WORK" \
  --query '[Status,StandardOutputContent]' --output text | tee "$OUTDIR/round2_worker.out"

CID_W0=$(aws ssm send-command --region "$REGION" --instance-ids "$SCHED" \
  --document-name AWS-RunShellScript --timeout-seconds 60 \
  --parameters 'commands=["nohup python3.11 -m distributed.cli.dask_worker tcp://127.0.0.1:8786 --nthreads 1 --memory-limit 0.8 --no-dashboard >/tmp/dask-worker0.log 2>&1 &","sleep 4","echo W0_UP"]' \
  --query Command.CommandId --output text)
sleep 6
aws ssm get-command-invocation --region "$REGION" --command-id "$CID_W0" --instance-id "$SCHED" \
  --query Status --output text

# Futures smoke + da.matmul with configurable size/timeout
python3 - "$MATRIX_SIZE" "$BENCH_TIMEOUT" > /tmp/ssm_dist_params_r2.json <<'PY'
import json, base64, textwrap, sys
size = int(sys.argv[1])
timeout = int(sys.argv[2])
py = textwrap.dedent(f'''
import json, time
import numpy as np
from dask.distributed import Client
import dask.array as da

size = {size}
client = Client("tcp://127.0.0.1:8786", timeout="60s")
info = client.scheduler_info()
nworkers = len(info.get("workers", {{}}))
print("workers", nworkers, flush=True)
# futures smoke
futs = [client.submit(lambda x: x * x, i) for i in range(4)]
smoke = [f.result(timeout=60) for f in futs]
print("futures", smoke, flush=True)

A = np.random.rand(size, size).astype("float64")
B = np.random.rand(size, size).astype("float64")
w = max(nworkers, 1)
a = da.from_array(A, chunks=(size // w, size))
b = da.from_array(B, chunks=(size, size // w))
# warm-up
_ = (a @ b).compute()
t0 = time.perf_counter()
C = (a @ b).compute()
elapsed = time.perf_counter() - t0
payload = {{
  "role": "scale-out",
  "mode": "dask_multi_instance",
  "size": size,
  "workers": nworkers,
  "elapsed_s": elapsed,
  "checksum": float(C[0, 0]),
  "futures_smoke": smoke,
  "worker_addrs": list(info.get("workers", {{}}).keys()),
}}
print(json.dumps(payload), flush=True)
client.close()
''').strip()
b64 = base64.b64encode(py.encode()).decode()
print(json.dumps({"commands": [
  f"echo {b64} | base64 -d > /tmp/dist_bench_r2.py",
  f"timeout {timeout} python3.11 /tmp/dist_bench_r2.py"
]}))
PY

python3 -c "
import json
params=json.load(open('/tmp/ssm_dist_params_r2.json'))
json.dump({
  'DocumentName':'AWS-RunShellScript',
  'InstanceIds':['$SCHED'],
  'TimeoutSeconds': $SSM_TIMEOUT,
  'Parameters': params
}, open('/tmp/ssm_body_r2.json','w'))
"

CID_B=$(aws ssm send-command --region "$REGION" --cli-input-json file:///tmp/ssm_body_r2.json \
  --query Command.CommandId --output text)
echo "bench_cid=$CID_B"
: > "$OUTDIR/scale_out_distributed_r2.out"
: > "$OUTDIR/scale_out_distributed_r2.err"
for i in $(seq 1 48); do
  st=$(aws ssm get-command-invocation --region "$REGION" --command-id "$CID_B" --instance-id "$SCHED" --query Status --output text)
  echo "poll=$i $st"
  case "$st" in
    Success|Failed|Cancelled|TimedOut)
      out=$(aws ssm get-command-invocation --region "$REGION" --command-id "$CID_B" --instance-id "$SCHED" --query StandardOutputContent --output text)
      err=$(aws ssm get-command-invocation --region "$REGION" --command-id "$CID_B" --instance-id "$SCHED" --query StandardErrorContent --output text)
      printf '%s\n' "$out" | tee "$OUTDIR/scale_out_distributed_r2.out"
      printf '%s\n' "$err" | tee "$OUTDIR/scale_out_distributed_r2.err"
      exit 0
      ;;
  esac
  sleep 15
done
echo "bench poll exhausted" >&2
exit 1
