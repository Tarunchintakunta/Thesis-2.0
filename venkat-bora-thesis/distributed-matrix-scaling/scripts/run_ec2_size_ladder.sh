#!/usr/bin/env bash
# CA2 multi-order size ladder on matched Free-Tier EC2.
# CA2 §3: growing matrix orders at fixed aggregate vCPU; record time/RSS/CPU;
# timeouts are valid outcomes (not failures to hide).
# Default Free-Tier live subset: 100,250,500 (local suite already covers 200–2000).
# Usage: bash scripts/run_ec2_size_ladder.sh [tag]
set -euo pipefail

TAG="${1:-ladder1}"
REGION="${REGION:-eu-west-1}"
SIZES="${SIZES:-100,250,500}"
BENCH_TIMEOUT="${BENCH_TIMEOUT:-600}"
SSM_TIMEOUT="${SSM_TIMEOUT:-720}"
AMI_ID="${AMI_ID:-ami-0ee768eb261a01ed2}"
NAME_PREFIX="${NAME_PREFIX:-matrix-ladder-${TAG}}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTDIR="${OUTDIR:-$ROOT/results/live/size_ladder_${TAG}}"
TFDIR="$ROOT/terraform"

QB_B64="$(base64 < "$ROOT/scripts/quick_bench.py" | tr -d '\n')"
DB_B64="$(base64 < "$ROOT/scripts/dist_bench.py" | tr -d '\n')"

mkdir -p "$OUTDIR"
LOG="$OUTDIR/run.log"
exec > >(tee -a "$LOG") 2>&1

need() { command -v "$1" >/dev/null || { echo "missing $1" >&2; exit 1; }; }
need aws; need terraform; need python3; need jq

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
  echo "destroy_confirmed=yes" | tee "$OUTDIR/destroy_confirmed.txt"
}
trap cleanup EXIT

cd "$TFDIR"
terraform init -input=false
echo "=== APPLY ami=$AMI_ID prefix=$NAME_PREFIX sizes=$SIZES ==="
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
echo "UP=$UP SCHED=$SCHED WORK=$WORK" | tee "$OUTDIR/topology.txt"

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
      --parameters 'commands=["PYBIN=$(command -v python3.11 || command -v python3); test -f /opt/matrix-scale/READY && test -n \"$PYBIN\" && $PYBIN -c \"import dask,numpy,psutil; print(\\\"READY\\\")\" 2>/dev/null || (ls -la /opt/matrix-scale 2>/dev/null; command -v python3.11; command -v python3; echo NOTREADY)"]' \
      --query Command.CommandId --output text)
    sleep 5
    out=$(aws ssm get-command-invocation --region "$REGION" --command-id "$cid" --instance-id "$id" \
      --query '[Status,StandardOutputContent]' --output text 2>&1 || true)
    echo "$id ready_try=$i ${out:0:180}"
    echo "$out" | grep -E '(^|[[:space:]])READY($|[[:space:]])' >/dev/null && return 0
    if echo "$out" | grep -q NOTREADY; then
      bcid=$(aws ssm send-command --region "$REGION" --instance-ids "$id" \
        --document-name AWS-RunShellScript --timeout-seconds 900 \
        --parameters 'commands=["set -euxo pipefail","dnf -y install python3.11 python3.11-pip python3.11-devel gcc || yum -y install python3.11 python3.11-pip gcc","PYBIN=$(command -v python3.11 || command -v python3)","test -n \"$PYBIN\"","$PYBIN -m pip install --upgrade pip","$PYBIN -m pip install numpy==2.1.3 '''dask[distributed]==2024.11.2''' psutil","mkdir -p /opt/matrix-scale","$PYBIN -c \"import dask,numpy,psutil\"","echo ready > /opt/matrix-scale/READY","echo BOOTSTRAP_OK"]' \
        --query Command.CommandId --output text)
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

ensure_dask_cluster() {
  local sched_ip=$1 work_ip=$2
  aws ssm send-command --region "$REGION" --instance-ids "$SCHED" "$WORK" \
    --document-name AWS-RunShellScript --timeout-seconds 60 \
    --parameters 'commands=["pkill -9 -f dask-scheduler || true","pkill -9 -f dask-worker || true","pkill -9 -f distributed || true","sleep 2","echo CLEANED"]' \
    --query Command.CommandId --output text >/dev/null
  sleep 4
  aws ssm send-command --region "$REGION" --instance-ids "$SCHED" \
    --document-name AWS-RunShellScript --timeout-seconds 120 \
    --parameters 'commands=["nohup python3.11 -m distributed.cli.dask_scheduler --host 0.0.0.0 --port 8786 --dashboard-address :8787 >/tmp/dask-sched.log 2>&1 &","sleep 4","ss -ltn | grep 8786 || true","echo SCHED_UP"]' \
    --query Command.CommandId --output text >/dev/null
  sleep 6
  aws ssm send-command --region "$REGION" --instance-ids "$WORK" \
    --document-name AWS-RunShellScript --timeout-seconds 120 \
    --parameters "commands=[\"nohup python3.11 -m distributed.cli.dask_worker tcp://${sched_ip}:8786 --nthreads 1 --memory-limit 0.8 --no-dashboard >/tmp/dask-worker.log 2>&1 &\",\"sleep 5\",\"tail -n 10 /tmp/dask-worker.log\",\"echo WORKER_UP\"]" \
    --query Command.CommandId --output text >/dev/null
  sleep 8
  aws ssm send-command --region "$REGION" --instance-ids "$SCHED" \
    --document-name AWS-RunShellScript --timeout-seconds 60 \
    --parameters "commands=[\"nohup python3.11 -m distributed.cli.dask_worker tcp://${sched_ip}:8786 --host ${sched_ip} --nthreads 1 --memory-limit 0.8 --no-dashboard >/tmp/dask-worker0.log 2>&1 &\",\"sleep 4\",\"echo W0_UP\"]" \
    --query Command.CommandId --output text >/dev/null
  sleep 5
}

run_one_size() {
  local size=$1
  local sdir="$OUTDIR/n_${size}"
  mkdir -p "$sdir"
  echo "=== SIZE n=$size ==="

  echo "--- scale-up n=$size ---"
  CID_UP=$(aws ssm send-command --region "$REGION" --instance-ids "$UP" \
    --document-name AWS-RunShellScript --timeout-seconds 300 \
    --parameters "commands=[\"export MATRIX_SIZE=${size} N_WORKERS=2 NODE_ROLE=scale-up\",\"python3.11 /opt/matrix-scale/quick_bench.py\"]" \
    --query Command.CommandId --output text)
  poll_ssm "$CID_UP" "$UP" "$sdir/scale_up.out" || true

  echo "--- on-node LocalCluster n=$size ---"
  for ID in "$SCHED" "$WORK"; do
    CID=$(aws ssm send-command --region "$REGION" --instance-ids "$ID" \
      --document-name AWS-RunShellScript --timeout-seconds 600 \
      --parameters "commands=[\"export MATRIX_SIZE=${size} N_WORKERS=1 NODE_ROLE=scale-out\",\"python3.11 /opt/matrix-scale/quick_bench.py\"]" \
      --query Command.CommandId --output text)
    poll_ssm "$CID" "$ID" "$sdir/scale_out_onnode_${ID}.out" || true
  done

  echo "--- multi-instance da.matmul n=$size (timeout=${BENCH_TIMEOUT}s as outcome) ---"
  ensure_dask_cluster "$SCHED_IP" "$WORK_IP"

  python3 - "$size" "$BENCH_TIMEOUT" > /tmp/ssm_dist_params_ladder.json <<'PY'
import json, sys
size = int(sys.argv[1]); timeout = int(sys.argv[2])
print(json.dumps({"commands": [
  f"export MATRIX_SIZE={size} BENCH_TIMEOUT={timeout} SCHEDULER_URL=tcp://127.0.0.1:8786",
  f"timeout {timeout} python3.11 /opt/matrix-scale/dist_bench.py"
]}))
PY
  python3 -c "
import json
params=json.load(open('/tmp/ssm_dist_params_ladder.json'))
json.dump({
  'DocumentName':'AWS-RunShellScript',
  'InstanceIds':['$SCHED'],
  'TimeoutSeconds': $SSM_TIMEOUT,
  'Parameters': params
}, open('/tmp/ssm_body_ladder.json','w'))
"
  CID_B=$(aws ssm send-command --region "$REGION" --cli-input-json file:///tmp/ssm_body_ladder.json \
    --query Command.CommandId --output text)
  echo "bench_cid=$CID_B n=$size"
  : > "$sdir/scale_out_distributed.out"
  : > "$sdir/scale_out_distributed.err"
  for i in $(seq 1 72); do
    st=$(aws ssm get-command-invocation --region "$REGION" --command-id "$CID_B" --instance-id "$SCHED" --query Status --output text 2>/dev/null || echo Pending)
    echo "poll_dist n=$size $i $st"
    case "$st" in
      Success|Failed|Cancelled|TimedOut)
        aws ssm get-command-invocation --region "$REGION" --command-id "$CID_B" --instance-id "$SCHED" \
          --query StandardOutputContent --output text | tee "$sdir/scale_out_distributed.out"
        aws ssm get-command-invocation --region "$REGION" --command-id "$CID_B" --instance-id "$SCHED" \
          --query StandardErrorContent --output text | tee "$sdir/scale_out_distributed.err"
        break
        ;;
    esac
    sleep 15
  done

  python3 - "$sdir" "$UP" "$SCHED" "$WORK" "$SCHED_IP" "$WORK_IP" "$size" "$AMI_ID" "$REGION" "$TAG" <<'PY'
import json, sys
from pathlib import Path
from datetime import datetime, timezone

outdir = Path(sys.argv[1])
up, sched, work = sys.argv[2], sys.argv[3], sys.argv[4]
sched_ip, work_ip = sys.argv[5], sys.argv[6]
size = int(sys.argv[7])
ami, region, tag = sys.argv[8], sys.argv[9], sys.argv[10]

def last_json(path: Path):
    text = path.read_text() if path.exists() else ""
    objs, buf, depth = [], [], 0
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
    "status": (dist_raw or {}).get("status") or ("ok" if dist_raw and dist_raw.get("elapsed_s") is not None else "failed"),
    "workers_registered": (dist_raw or {}).get("workers"),
    "futures_smoke": (dist_raw or {}).get("futures_smoke"),
    "dask_array_matmul": (dist_raw or {}).get("status") or ("ok" if dist_raw and "elapsed_s" in (dist_raw or {}) else "failed"),
    "mode": "dask_multi_instance_matmul",
    "size": size,
    "elapsed_s": (dist_raw or {}).get("elapsed_s"),
    "peak_rss_mb": (dist_raw or {}).get("peak_rss_mb"),
    "avg_cpu_percent": (dist_raw or {}).get("avg_cpu_percent"),
    "checksum": (dist_raw or {}).get("checksum"),
    "error": (dist_raw or {}).get("error"),
    "scheduler": f"tcp://{sched_ip}:8786",
    "hostname": (dist_raw or {}).get("hostname"),
    "worker_addrs": (dist_raw or {}).get("worker_addrs"),
    "note": f"size_ladder_{tag} n={size}; timeouts are outcomes.",
}
if dist_raw is None:
    err = (outdir / "scale_out_distributed.err").read_text() if (outdir / "scale_out_distributed.err").exists() else ""
    out = (outdir / "scale_out_distributed.out").read_text() if (outdir / "scale_out_distributed.out").exists() else ""
    if "timed_out" in out.lower() or "Timeout" in err or "timeout" in err.lower():
        multi["status"] = "timed_out"
        multi["dask_array_matmul"] = "timed_out"
    elif "124" in err or "killed" in err.lower():
        multi["status"] = "timed_out"
        multi["dask_array_matmul"] = "timed_out"

on_mean = None
if on_nodes:
    on_mean = sum(x["elapsed_s"] for x in on_nodes) / len(on_nodes)

summary = {
    "collected_at": datetime.now(timezone.utc).isoformat(),
    "region": region,
    "pack": f"size_ladder_{tag}",
    "protocol_note": "CA2 growing-order limb on Free-Tier matched vCPU; timeouts-as-outcomes.",
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
        "scale_up_peak_rss_mb": (scale_up or {}).get("peak_rss_mb"),
        "scale_out_on_node_mean_elapsed_s": on_mean,
        "scale_out_multi_instance_elapsed_s": multi.get("elapsed_s"),
        "scale_out_multi_instance_status": multi.get("status"),
        "scale_out_multi_peak_rss_mb": multi.get("peak_rss_mb"),
        "scale_out_multi_avg_cpu_percent": multi.get("avg_cpu_percent"),
    },
    "ami_id": ami,
    "destroy_after_campaign": True,
}
(outdir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({"n": size, "multi_status": multi["status"], "elapsed": multi.get("elapsed_s")}, indent=2))
PY
}

wait_ssm "$UP"
wait_ssm "$SCHED"
wait_ssm "$WORK"
wait_ready "$UP"
wait_ready "$SCHED"
wait_ready "$WORK"

for ID in "$UP" "$SCHED" "$WORK"; do
  aws ssm send-command --region "$REGION" --instance-ids "$ID" \
    --document-name AWS-RunShellScript --timeout-seconds 60 \
    --parameters "commands=[\"mkdir -p /opt/matrix-scale\",\"echo $QB_B64 | base64 -d > /opt/matrix-scale/quick_bench.py\",\"echo $DB_B64 | base64 -d > /opt/matrix-scale/dist_bench.py\",\"ls -la /opt/matrix-scale/*.py\"]" \
    --query Command.CommandId --output text >/dev/null || true
done
sleep 6

IPS=$(aws ec2 describe-instances --region "$REGION" --instance-ids "$SCHED" "$WORK" \
  --query 'Reservations[].Instances[].[InstanceId,PrivateIpAddress]' --output text)
SCHED_IP=$(echo "$IPS" | awk -v id="$SCHED" '$1==id{print $2}')
WORK_IP=$(echo "$IPS" | awk -v id="$WORK" '$1==id{print $2}')
echo "sched_ip=$SCHED_IP work_ip=$WORK_IP" | tee -a "$OUTDIR/topology.txt"

IFS=',' read -r -a SIZE_ARR <<< "$SIZES"
for size in "${SIZE_ARR[@]}"; do
  size="$(echo "$size" | tr -d '[:space:]')"
  [[ -n "$size" ]] || continue
  run_one_size "$size" || echo "WARN: size $size cell returned non-zero; continuing ladder" >&2
done

python3 - "$OUTDIR" "$SIZES" "$TAG" "$REGION" <<'PY'
import json, sys
from pathlib import Path
from datetime import datetime, timezone

outdir = Path(sys.argv[1])
sizes = [int(x.strip()) for x in sys.argv[2].split(",") if x.strip()]
tag, region = sys.argv[3], sys.argv[4]
rows = []
for n in sizes:
    p = outdir / f"n_{n}" / "summary.json"
    if not p.exists():
        rows.append({"matrix_size": n, "status": "missing"})
        continue
    s = json.loads(p.read_text())
    c = s.get("comparison", {})
    m = s.get("scale_out_multi_instance", {})
    rows.append({
        "matrix_size": n,
        "scale_up_elapsed_s": c.get("scale_up_elapsed_s"),
        "scale_up_peak_rss_mb": c.get("scale_up_peak_rss_mb"),
        "multi_status": m.get("status"),
        "multi_elapsed_s": c.get("scale_out_multi_instance_elapsed_s"),
        "multi_peak_rss_mb": c.get("scale_out_multi_peak_rss_mb"),
        "multi_avg_cpu_percent": c.get("scale_out_multi_avg_cpu_percent"),
    })

# CA2 crossover: smallest order where multi is significantly faster and stays faster.
# On Free-Tier descriptive: report whether any order has multi_elapsed < scale_up_elapsed with status ok.
crossover = None
anti = True
for r in rows:
    su, mu, st = r.get("scale_up_elapsed_s"), r.get("multi_elapsed_s"), r.get("multi_status")
    if su is None or mu is None or st != "ok":
        continue
    if mu < su:
        crossover = r["matrix_size"]
        anti = False
        break
    # else scale-up still faster → anti-crossover continues

campaign = {
    "collected_at": datetime.now(timezone.utc).isoformat(),
    "pack": f"size_ladder_{tag}",
    "region": region,
    "ca2_alignment": {
        "objective": "growing matrix orders at matched aggregate vCPU (1xt3.small vs 2xt3.micro)",
        "live_subset": sizes,
        "local_full_range_note": "local Dask suite covers 200–2000; this pack is Free-Tier live limb",
        "timeouts_as_outcomes": True,
        "metrics": ["elapsed_s", "peak_rss_mb", "avg_cpu_percent"],
    },
    "sizes": sizes,
    "rows": rows,
    "crossover_order_descriptive": crossover,
    "anti_crossover_retained": anti and crossover is None,
    "destroy_after": True,
}
(outdir / "campaign_summary.json").write_text(json.dumps(campaign, indent=2) + "\n")
print(json.dumps(campaign, indent=2))
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
echo "VENKAT_SIZE_LADDER_${TAG}_DONE $(date -u +%Y-%m-%dT%H:%M:%SZ); destroy confirmed"
