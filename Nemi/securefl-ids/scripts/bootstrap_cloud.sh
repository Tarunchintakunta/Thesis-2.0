#!/bin/bash
# On-instance lite FL bootstrap. Args: bucket region log_group run_id
set -euxo pipefail
BUCKET="${1:?bucket}"
REGION="${2:?region}"
LOG_GROUP="${3:?log_group}"
RUN_ID="${4:?run_id}"
export AWS_DEFAULT_REGION="$REGION"
export SECUREFL_BUCKET="$BUCKET"
export SECUREFL_LOG_GROUP="$LOG_GROUP"

swapon --show || true
free -m || true

aws s3 cp "s3://${BUCKET}/lite/${RUN_ID}/artefact.tgz" /tmp/securefl-artefact.tgz
rm -rf /opt/securefl-ids
mkdir -p /opt/securefl-ids
tar -xzf /tmp/securefl-artefact.tgz -C /opt/securefl-ids
cd /opt/securefl-ids

PY=python3.11
command -v python3.11 >/dev/null 2>&1 || PY=python3
$PY -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install 'numpy>=1.24,<2.3' 'pandas>=2.0' 'scikit-learn>=1.3' 'boto3>=1.34'
.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu

.venv/bin/python scripts/run_cloud_lite.py \
  --bucket "$BUCKET" \
  --region "$REGION" \
  --log-group "$LOG_GROUP" \
  --run-id "$RUN_ID" \
  --num-clients 2 \
  --num-rounds 3 \
  --sample-size 2500 \
  --out results/live/cloud_lite_summary.json

aws s3 cp results/live/cloud_lite_summary.json \
  "s3://${BUCKET}/lite/${RUN_ID}/cloud_lite_summary.json"
echo done > /opt/securefl-ids/DONE
