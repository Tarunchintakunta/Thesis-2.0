# Matched-vCPU EC2 topologies for matrix scaling (scale-up vs scale-out).
# Tags: project slug only — never personal name or personal ID.
# Instances are created only when ami_id is set; terraform destroy removes them.
# SSM Session Manager: no SSH key required for a short budget-capped round.

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      project    = "distributed-matrix-scaling"
      managed_by = "terraform"
      purpose    = "research-eval"
      data       = "synthetic"
    }
  }
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_iam_policy_document" "ec2_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "node" {
  name               = "${var.name_prefix}-node"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume.json
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "node" {
  name = "${var.name_prefix}-node"
  role = aws_iam_role.node.name
}

resource "aws_security_group" "cluster" {
  name_prefix = "${var.name_prefix}-"
  vpc_id      = data.aws_vpc.default.id
  description = "Matrix scaling research cluster (Dask scheduler/workers)"

  # Dask scheduler/dashboard plus worker ephemeral ports (intra-SG only).
  ingress {
    description = "Dask cluster (scheduler, dashboard, worker)"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    self        = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

locals {
  user_data = <<-EOF
    #!/bin/bash
    set -euxo pipefail
    dnf -y update || yum -y update || true
    dnf -y install python3.11 python3.11-pip python3.11-devel gcc || yum -y install python3.11 python3.11-pip gcc
    python3.11 -m pip install --upgrade pip
    python3.11 -m pip install 'numpy==2.1.3' 'dask[distributed]==2024.11.2' psutil
    mkdir -p /opt/matrix-scale
    cat > /opt/matrix-scale/quick_bench.py <<'PY'
import json, time, os
import numpy as np
from pathlib import Path
size = int(os.environ.get("MATRIX_SIZE", "250"))
workers = int(os.environ.get("N_WORKERS", "2"))
role = os.environ.get("NODE_ROLE", "scale-up")
out = Path("/opt/matrix-scale/result.json")
A = np.random.rand(size, size)
B = np.random.rand(size, size)
t0 = time.perf_counter()
if role == "scale-up":
    C = A @ B
    mode = "numpy_matmul"
else:
    from dask.distributed import Client, LocalCluster
    cluster = LocalCluster(n_workers=workers, threads_per_worker=1, processes=False, dashboard_address=None)
    client = Client(cluster)
    import dask.array as da
    a = da.from_array(A, chunks=(size // max(workers, 1), size))
    b = da.from_array(B, chunks=(size, size // max(workers, 1)))
    C = (a @ b).compute()
    client.close(); cluster.close()
    mode = "dask_localcluster_on_node"
elapsed = time.perf_counter() - t0
out.write_text(json.dumps({
    "role": role, "mode": mode, "size": size, "workers": workers,
    "elapsed_s": elapsed, "checksum": float(C[0,0]),
    "hostname": os.uname().nodename,
}, indent=2) + "\n")
print(out.read_text())
PY
    echo ready > /opt/matrix-scale/READY
  EOF
}

resource "aws_instance" "scale_up" {
  count = var.ami_id == "" ? 0 : 1

  ami                    = var.ami_id
  instance_type          = var.scale_up_instance_type
  subnet_id              = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.cluster.id]
  iam_instance_profile   = aws_iam_instance_profile.node.name
  key_name               = var.key_name == "" ? null : var.key_name
  user_data              = local.user_data

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
  }

  metadata_options {
    http_tokens = "required"
  }

  tags = {
    Name = "${var.name_prefix}-scale-up"
    role = "scale-up"
  }
}

resource "aws_instance" "scale_out" {
  count = var.ami_id == "" ? 0 : var.scale_out_count

  ami                    = var.ami_id
  instance_type          = var.scale_out_instance_type
  subnet_id              = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.cluster.id]
  iam_instance_profile   = aws_iam_instance_profile.node.name
  key_name               = var.key_name == "" ? null : var.key_name
  user_data              = local.user_data

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  metadata_options {
    http_tokens = "required"
  }

  tags = {
    Name = "${var.name_prefix}-scale-out-${count.index}"
    role = count.index == 0 ? "dask-scheduler" : "dask-worker"
  }
}
