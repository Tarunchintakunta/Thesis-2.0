#!/usr/bin/env bash
# final_1: ONE confirmatory matched-vCPU EC2 gate (eu-west-1).
# Topology: 1× t3.small (scale-up) vs 2× t3.micro (scale-out). Destroy after.
# Saves under results/live/final_1/. Does NOT start final-3.
set -euo pipefail

REGION="${REGION:-eu-west-1}"
MATRIX_SIZE="${MATRIX_SIZE:-250}"
BENCH_TIMEOUT="${BENCH_TIMEOUT:-600}"
SSM_TIMEOUT="${SSM_TIMEOUT:-720}"
AMI_ID="${AMI_ID:-ami-0ee768eb261a01ed2}"
NAME_PREFIX="${NAME_PREFIX:-matrix-scale-f1}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTDIR="${OUTDIR:-$ROOT/results/live/final_1}"
TFDIR="$ROOT/terraform"
mkdir -p "$OUTDIR"
LOG="$OUTDIR/run.log"
exec > >(tee -a "$LOG") 2>&1

need() { command -v "$1" >/dev/null || { echo "missing $1" >&2; exit 1; }; }
need aws
need terraform
need python3
need jq

# Prefer python3.11; fall back to python3 on the instance.
remote_py() {
  echo 'PYBIN=$(command -v python3.11 || command -v python3); echo PYBIN=$PYBIN; test -n "$PYBIN"'
}

DESTROYED=0
cleanup() {
  if [[ "$DESTROYED" -eq 1 ]]; then return 0; fi
  echo "=== CLEANUP: terraform destroy ==="
  cd "$TFDIR"
  terraform destroy -auto-approve \
    -var="ami_id=${AMI_ID}" \
    -var="name_prefix=${NAME_PREFIX}" \
    -var="region=${REGION}" || true
  ids=$(aws ec2 describe-instances --region "$REGION" \
    --filters "Name=tag:project,Values=distributed-matrix-scaling" \
              "Name=instance-state-name,Values=pending,running,stopping,stopped" \
    --query 'Reservations[].Instances[].InstanceId' --output text 2>/dev/null || true)
  if [[ -n "${ids:-}" && "$ids" != "None" ]]; then
    echo "force terminate: $ids"
    aws ec2 terminate-instances --region "$REGION" --instance-ids $ids >/dev/null || true
  fi
  DESTROYED=1
  mkdir -p "$OUTDIR"; echo "destroy_confirmed=yes" | tee "$OUTDIR/destroy_confirmed.txt"
}
trap cleanup EXIT

cd "$TFDIR"
terraform init -input=false
echo "=== APPLY ami=$AMI_ID prefix=$NAME_PREFIX size=$MATRIX_SIZE ==="
terraform apply -auto-approve \
  -var="ami_id=${AMI_ID}" \
  -var="name_prefix=${NAME_PREFIX}" \
  -var="region=${REGION}" \
  -var="scale_up_instance_type=t3.small" \
  -var="scale_out_instance_type=t3.micro" \
  -var="scale_out_count=2"

UP="$(terraform output -raw scale_up_instance_id)"
SCHED="$(terraform output -json scale_out_instance_ids | jq -r '.[0]')"
WORK="$(terraform output -json scale_out_instance_ids | jq -r '.[1]')"
SG="$(terraform output -raw security_group_id)"
mkdir -p "$OUTDIR"
echo "UP=$UP SCHED=$SCHED WORK=$WORK SG=$SG" | tee "$OUTDIR/topology.txt"

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
      --parameters 'commands=["PYBIN=$(command -v python3.11 || command -v python3); test -f /opt/matrix-scale/READY && test -n \"$PYBIN\" && $PYBIN -c \"import dask,numpy; print(\\\"READY\\\")\" 2>/dev/null || (ls -la /opt/matrix-scale 2>/dev/null; command -v python3.11; command -v python3; echo NOTREADY)"]' \
      --query Command.CommandId --output text)
    sleep 5
    out=$(aws ssm get-command-invocation --region "$REGION" --command-id "$cid" --instance-id "$id" \
      --query '[Status,StandardOutputContent]' --output text 2>&1 || true)
    echo "$id ready_try=$i ${out:0:180}"
    # Exact token READY only (NOTREADY must not match).
    echo "$out" | grep -E '(^|[[:space:]])READY($|[[:space:]])' >/dev/null && return 0
    if echo "$out" | grep -q NOTREADY; then
      bcid=$(aws ssm send-command --region "$REGION" --instance-ids "$id" \
        --document-name AWS-RunShellScript --timeout-seconds 900 \
        --parameters 'commands=["set -euxo pipefail","dnf -y install python3.11 python3.11-pip python3.11-devel gcc || yum -y install python3.11 python3.11-pip gcc","PYBIN=$(command -v python3.11 || command -v python3)","test -n \"$PYBIN\"","$PYBIN -m pip install --upgrade pip","$PYBIN -m pip install numpy==2.1.3 '''dask[distributed]==2024.11.2''' psutil","mkdir -p /opt/matrix-scale","$PYBIN -c \"import dask,numpy\"","echo ready > /opt/matrix-scale/READY","echo BOOTSTRAP_OK"]' \
        --query Command.CommandId --output text)
      echo "$bcid" > /tmp/venkat_ie1_bootstrap_$id.txt
      for _b in $(seq 1 45); do
        bst=$(aws ssm get-command-invocation --region "$REGION" --command-id "$bcid" --instance-id "$id" --query Status --output text 2>/dev/null || echo Pending)
        echo "bootstrap $id $_b $bst"
        case "$bst" in Success|Failed|Cancelled|TimedOut) break ;; esac
        sleep 15
      done
    fi
    sleep 5
  done
  return 1
}

poll_ssm() {
  local cid=$1 id=$2 outf=$3
  for i in $(seq 1 60); do
    st=$(aws ssm get-command-invocation --region "$REGION" --command-id "$cid" --instance-id "$id" --query Status --output text 2>/dev/null || echo Pending)
    echo "poll $id $i $st"
    case "$st" in
      Success|Failed|Cancelled|TimedOut)
        aws ssm get-command-invocation --region "$REGION" --command-id "$cid" --instance-id "$id" \
          --query StandardOutputContent --output text | tee "$outf"
        aws ssm get-command-invocation --region "$REGION" --command-id "$cid" --instance-id "$id" \
          --output json > "${outf%.out}_ssm.json" 2>/dev/null || true
        return 0
        ;;
    esac
    sleep 10
  done
  echo "poll exhausted $cid $id" >&2
  return 1
}

wait_ssm "$UP"
wait_ssm "$SCHED"
wait_ssm "$WORK"
wait_ready "$UP"
wait_ready "$SCHED"
wait_ready "$WORK"

# Ensure quick_bench.py exists on all nodes
QB64="aW1wb3J0IGpzb24sIHRpbWUsIG9zCmltcG9ydCBudW1weSBhcyBucApmcm9tIHBhdGhsaWIgaW1wb3J0IFBhdGgKc2l6ZSA9IGludChvcy5lbnZpcm9uLmdldCgiTUFUUklYX1NJWkUiLCAiMjUwIikpCndvcmtlcnMgPSBpbnQob3MuZW52aXJvbi5nZXQoIk5fV09SS0VSUyIsICIyIikpCnJvbGUgPSBvcy5lbnZpcm9uLmdldCgiTk9ERV9ST0xFIiwgInNjYWxlLXVwIikKb3V0ID0gUGF0aCgiL29wdC9tYXRyaXgtc2NhbGUvcmVzdWx0Lmpzb24iKQpBID0gbnAucmFuZG9tLnJhbmQoc2l6ZSwgc2l6ZSkKQiA9IG5wLnJhbmRvbS5yYW5kKHNpemUsIHNpemUpCnQwID0gdGltZS5wZXJmX2NvdW50ZXIoKQppZiByb2xlID09ICJzY2FsZS11cCI6CiAgICBDID0gQSBAIEIKICAgIG1vZGUgPSAibnVtcHlfbWF0bXVsIgplbHNlOgogICAgZnJvbSBkYXNrLmRpc3RyaWJ1dGVkIGltcG9ydCBDbGllbnQsIExvY2FsQ2x1c3RlcgogICAgY2x1c3RlciA9IExvY2FsQ2x1c3RlcihuX3dvcmtlcnM9d29ya2VycywgdGhyZWFkc19wZXJfd29ya2VyPTEsIHByb2Nlc3Nlcz1GYWxzZSwgZGFzaGJvYXJkX2FkZHJlc3M9Tm9uZSkKICAgIGNsaWVudCA9IENsaWVudChjbHVzdGVyKQogICAgaW1wb3J0IGRhc2suYXJyYXkgYXMgZGEKICAgIGEgPSBkYS5mcm9tX2FycmF5KEEsIGNodW5rcz0oc2l6ZSAvLyBtYXgod29ya2VycywgMSksIHNpemUpKQogICAgYiA9IGRhLmZyb21fYXJyYXkoQiwgY2h1bmtzPShzaXplLCBzaXplIC8vIG1heCh3b3JrZXJzLCAxKSkpCiAgICBDID0gKGEgQCBiKS5jb21wdXRlKCkKICAgIGNsaWVudC5jbG9zZSgpOyBjbHVzdGVyLmNsb3NlKCkKICAgIG1vZGUgPSAiZGFza19sb2NhbGNsdXN0ZXJfb25fbm9kZSIKZWxhcHNlZCA9IHRpbWUucGVyZl9jb3VudGVyKCkgLSB0MApvdXQud3JpdGVfdGV4dChqc29uLmR1bXBzKHsKICAgICJyb2xlIjogcm9sZSwgIm1vZGUiOiBtb2RlLCAic2l6ZSI6IHNpemUsICJ3b3JrZXJzIjogd29ya2VycywKICAgICJlbGFwc2VkX3MiOiBlbGFwc2VkLCAiY2hlY2tzdW0iOiBmbG9hdChDWzAsMF0pLAogICAgImhvc3RuYW1lIjogb3MudW5hbWUoKS5ub2RlbmFtZSwKfSwgaW5kZW50PTIpICsgIlxuIikKcHJpbnQob3V0LnJlYWRfdGV4dCgpKQo="
for ID in "$UP" "$SCHED" "$WORK"; do
  aws ssm send-command --region "$REGION" --instance-ids "$ID" \
    --document-name AWS-RunShellScript --timeout-seconds 60 \
    --parameters "commands=[\"mkdir -p /opt/matrix-scale\",\"echo $QB64 | base64 -d > /opt/matrix-scale/quick_bench.py\",\"ls -la /opt/matrix-scale/quick_bench.py\"]" \
    --query Command.CommandId --output text >/dev/null || true
done
sleep 6

echo "=== SCALE-UP n=$MATRIX_SIZE ==="
CID_UP=$(aws ssm send-command --region "$REGION" --instance-ids "$UP" \
  --document-name AWS-RunShellScript --timeout-seconds 300 \
  --parameters "commands=[\"export MATRIX_SIZE=${MATRIX_SIZE} N_WORKERS=2 NODE_ROLE=scale-up\",\"command -v python3.11\",\"python3.11 /opt/matrix-scale/quick_bench.py\"]" \
  --query Command.CommandId --output text)
poll_ssm "$CID_UP" "$UP" "$OUTDIR/scale_up.out"

echo "=== ON-NODE LocalCluster n=$MATRIX_SIZE ==="
for ID in "$SCHED" "$WORK"; do
  CID=$(aws ssm send-command --region "$REGION" --instance-ids "$ID" \
    --document-name AWS-RunShellScript --timeout-seconds 600 \
    --parameters "commands=[\"export MATRIX_SIZE=${MATRIX_SIZE} N_WORKERS=1 NODE_ROLE=scale-out\",\"command -v python3.11\",\"python3.11 /opt/matrix-scale/quick_bench.py\"]" \
    --query Command.CommandId --output text)
  poll_ssm "$CID" "$ID" "$OUTDIR/scale_out_onnode_${ID}.out"
done

IPS=$(aws ec2 describe-instances --region "$REGION" --instance-ids "$SCHED" "$WORK" \
  --query 'Reservations[].Instances[].[InstanceId,PrivateIpAddress]' --output text)
SCHED_IP=$(echo "$IPS" | awk -v id="$SCHED" '$1==id{print $2}')
WORK_IP=$(echo "$IPS" | awk -v id="$WORK" '$1==id{print $2}')
echo "sched_ip=$SCHED_IP work_ip=$WORK_IP"

aws ssm send-command --region "$REGION" --instance-ids "$SCHED" "$WORK" \
  --document-name AWS-RunShellScript --timeout-seconds 60 \
  --parameters 'commands=["pkill -9 -f dask-scheduler || true","pkill -9 -f dask-worker || true","pkill -9 -f distributed || true","sleep 2","echo CLEANED"]' \
  --query Command.CommandId --output text >/dev/null
sleep 5

CID_S=$(aws ssm send-command --region "$REGION" --instance-ids "$SCHED" \
  --document-name AWS-RunShellScript --timeout-seconds 120 \
  --parameters 'commands=["nohup python3.11 -m distributed.cli.dask_scheduler --host 0.0.0.0 --port 8786 --dashboard-address :8787 >/tmp/dask-sched.log 2>&1 &","sleep 4","ss -ltn | grep 8786 || true","echo SCHED_UP"]' \
  --query Command.CommandId --output text)
sleep 8
aws ssm get-command-invocation --region "$REGION" --command-id "$CID_S" --instance-id "$SCHED" \
  --query '[Status,StandardOutputContent]' --output text | tee "$OUTDIR/sched.out"

CID_W=$(aws ssm send-command --region "$REGION" --instance-ids "$WORK" \
  --document-name AWS-RunShellScript --timeout-seconds 120 \
  --parameters "commands=[\"nohup python3.11 -m distributed.cli.dask_worker tcp://${SCHED_IP}:8786 --nthreads 1 --memory-limit 0.8 --no-dashboard >/tmp/dask-worker.log 2>&1 &\",\"sleep 5\",\"tail -n 20 /tmp/dask-worker.log\",\"echo WORKER_UP\"]" \
  --query Command.CommandId --output text)
sleep 10
aws ssm get-command-invocation --region "$REGION" --command-id "$CID_W" --instance-id "$WORK" \
  --query '[Status,StandardOutputContent]' --output text | tee "$OUTDIR/worker.out"

# Advertise scheduler private IP so remote workers can gather deps (not 127.0.0.1).
aws ssm send-command --region "$REGION" --instance-ids "$SCHED" \
  --document-name AWS-RunShellScript --timeout-seconds 60 \
  --parameters "commands=[\"nohup python3.11 -m distributed.cli.dask_worker tcp://${SCHED_IP}:8786 --host ${SCHED_IP} --nthreads 1 --memory-limit 0.8 --no-dashboard >/tmp/dask-worker0.log 2>&1 &\",\"sleep 4\",\"tail -n 15 /tmp/dask-worker0.log\",\"echo W0_UP\"]" \
  --query Command.CommandId --output text >/dev/null
sleep 6

python3 - "$MATRIX_SIZE" "$BENCH_TIMEOUT" > /tmp/ssm_dist_params_ie1.json <<'PY'
import json, base64, textwrap, sys
size = int(sys.argv[1])
timeout = int(sys.argv[2])
py = textwrap.dedent(f'''
import json, time
import numpy as np
from dask.distributed import Client
import dask.array as da

size = {size}
print("connecting", flush=True)
client = Client("tcp://127.0.0.1:8786", timeout="60s")
info = client.scheduler_info()
nworkers = len(info.get("workers", {{}}))
print("workers", nworkers, flush=True)
futs = [client.submit(lambda x: x * x, i) for i in range(4)]
smoke = [f.result(timeout=60) for f in futs]
print("futures", smoke, flush=True)

A = np.random.rand(size, size).astype("float64")
B = np.random.rand(size, size).astype("float64")
w = max(nworkers, 1)
chunk = max(size // w, 1)
a = da.from_array(A, chunks=(chunk, size))
b = da.from_array(B, chunks=(size, chunk))
print("matmul_start", size, "chunk", chunk, flush=True)
t0 = time.perf_counter()
C = (a @ b).compute()
elapsed = time.perf_counter() - t0
print("matmul_done", elapsed, flush=True)
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
  f"echo {b64} | base64 -d > /tmp/dist_bench_ie1.py",
  f"timeout {timeout} python3.11 /tmp/dist_bench_ie1.py"
]}))
PY

python3 -c "
import json
params=json.load(open('/tmp/ssm_dist_params_ie1.json'))
json.dump({
  'DocumentName':'AWS-RunShellScript',
  'InstanceIds':['$SCHED'],
  'TimeoutSeconds': $SSM_TIMEOUT,
  'Parameters': params
}, open('/tmp/ssm_body_ie1.json','w'))
"

CID_B=$(aws ssm send-command --region "$REGION" --cli-input-json file:///tmp/ssm_body_ie1.json \
  --query Command.CommandId --output text)
echo "bench_cid=$CID_B"
: > "$OUTDIR/scale_out_distributed.out"
: > "$OUTDIR/scale_out_distributed.err"
for i in $(seq 1 72); do
  st=$(aws ssm get-command-invocation --region "$REGION" --command-id "$CID_B" --instance-id "$SCHED" --query Status --output text)
  echo "poll_dist=$i $st"
  case "$st" in
    Success|Failed|Cancelled|TimedOut)
      aws ssm get-command-invocation --region "$REGION" --command-id "$CID_B" --instance-id "$SCHED" \
        --query StandardOutputContent --output text | tee "$OUTDIR/scale_out_distributed.out"
      aws ssm get-command-invocation --region "$REGION" --command-id "$CID_B" --instance-id "$SCHED" \
        --query StandardErrorContent --output text | tee "$OUTDIR/scale_out_distributed.err"
      break
      ;;
  esac
  sleep 15
done

python3 - "$OUTDIR" "$UP" "$SCHED" "$WORK" "$SCHED_IP" "$WORK_IP" "$MATRIX_SIZE" "$AMI_ID" "$REGION" <<'PY'
import json, sys
from pathlib import Path
from datetime import datetime, timezone

outdir = Path(sys.argv[1])
up, sched, work = sys.argv[2], sys.argv[3], sys.argv[4]
sched_ip, work_ip = sys.argv[5], sys.argv[6]
size = int(sys.argv[7])
ami, region = sys.argv[8], sys.argv[9]

def last_json(path: Path):
    text = path.read_text() if path.exists() else ""
    objs = []
    buf, depth = [], 0
    for ch in text:
        if ch == "{":
            depth += 1
        if depth:
            buf.append(ch)
        if ch == "}":
            depth -= 1
            if depth == 0 and buf:
                try:
                    objs.append(json.loads("".join(buf)))
                except Exception:
                    pass
                buf = []
    return objs[-1] if objs else None

scale_up = last_json(outdir / "scale_up.out")
on_nodes = []
for iid in (sched, work):
    j = last_json(outdir / f"scale_out_onnode_{iid}.out")
    if j:
        on_nodes.append(j)

dist_raw = last_json(outdir / "scale_out_distributed.out")
multi = {
    "status": "ok" if dist_raw and dist_raw.get("elapsed_s") is not None else "failed",
    "workers_registered": (dist_raw or {}).get("workers"),
    "futures_smoke": (dist_raw or {}).get("futures_smoke"),
    "dask_array_matmul": "ok" if dist_raw and "elapsed_s" in (dist_raw or {}) else "failed",
    "mode": "dask_multi_instance_matmul",
    "size": size,
    "elapsed_s": (dist_raw or {}).get("elapsed_s"),
    "checksum": (dist_raw or {}).get("checksum"),
    "scheduler": f"tcp://{sched_ip}:8786",
    "hostname": (dist_raw or {}).get("hostname"),
    "worker_addrs": (dist_raw or {}).get("worker_addrs"),
    "note": "Scheduler on scale-out-0; one dask-worker per t3.micro (2 workers total); final_1 gate.",
}
if dist_raw is None:
    err = (outdir / "scale_out_distributed.err").read_text() if (outdir / "scale_out_distributed.err").exists() else ""
    out = (outdir / "scale_out_distributed.out").read_text() if (outdir / "scale_out_distributed.out").exists() else ""
    if "timed_out" in out.lower() or "Timeout" in err:
        multi["status"] = "timed_out"
        multi["dask_array_matmul"] = "timed_out"

on_mean = None
if on_nodes:
    on_mean = sum(x["elapsed_s"] for x in on_nodes) / len(on_nodes)

summary = {
    "collected_at": datetime.now(timezone.utc).isoformat(),
    "region": region,
    "round": "final_1",
    "protocol_note": "ONE confirmatory matched Free-Tier gate after CA2 100% (post ec2_round2). Same topology 1xt3.small vs 2xt3.micro; destroy-after. Final-3 not started.",
    "topology": {
        "scale_up": {"instance_id": up, "instance_type": "t3.small", "vcpus": 2, "count": 1},
        "scale_out": {
            "instance_ids": [sched, work],
            "instance_type": "t3.micro",
            "vcpus": 1,
            "count": 2,
            "aggregate_vcpus": 2,
            "private_ips": [sched_ip, work_ip],
            "scheduler_private_ip": sched_ip,
        },
    },
    "matrix_size": size,
    "scale_up": scale_up,
    "scale_out_on_node": on_nodes,
    "scale_out_multi_instance": multi,
    "comparison": {
        "scale_up_elapsed_s": (scale_up or {}).get("elapsed_s"),
        "scale_out_on_node_mean_elapsed_s": on_mean,
        "scale_out_multi_instance_elapsed_s": multi.get("elapsed_s"),
    },
    "ami_id": ami,
    "name_prefix": "matrix-scale-f1",
    "destroy_after": True,
}
(outdir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
print("multi_status=", multi["status"], "elapsed=", multi.get("elapsed_s"))
PY

echo "=== DESTROY ==="
cleanup
trap - EXIT

left=$(aws ec2 describe-instances --region "$REGION" \
  --filters "Name=tag:project,Values=distributed-matrix-scaling" \
            "Name=instance-state-name,Values=pending,running" \
  --query 'length(Reservations[].Instances[])' --output text)
echo "remaining_running_project_instances=$left"
[[ "$left" == "0" ]] || { echo "WARN: instances still running" >&2; exit 2; }
echo "final_1 complete; destroy confirmed"
