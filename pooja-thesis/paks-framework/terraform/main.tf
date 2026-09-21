# Free-Tier-safe PAKS live K8s: 1× t3.micro + k3s + S3 + CloudWatch.
# Tags: project=paks-k8s-live only — NEVER touch project=distributed-matrix-scaling.
# Destroy after eval. No EKS.

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      project     = "paks-k8s-live"
      managed_by  = "terraform"
      purpose     = "research-eval"
      thesis      = "pooja-paks"
      destroy_after = "true"
    }
  }
}

data "aws_caller_identity" "current" {}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_ssm_parameter" "al2023" {
  count = var.ami_id == "" ? 1 : 0
  name  = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

locals {
  ami_id    = var.ami_id != "" ? var.ami_id : data.aws_ssm_parameter.al2023[0].value
  subnet_id = sort(data.aws_subnets.default.ids)[0]
  # Harden: no public kube-apiserver; all control via SSM Session Manager.
  user_data = <<-EOF
#!/bin/bash
set -euxo pipefail
exec > >(tee /var/log/paks-k3s-bootstrap.log | logger -t paks-k3s -s 2>/dev/console) 2>&1

dnf -y update || true
# AL2023 ships curl-minimal; do not install conflicting `curl` package.
dnf -y install python3 python3-pip python3-numpy jq tar gzip || true
command -v aws >/dev/null 2>&1 || pip3 install --quiet awscli || true
command -v curl >/dev/null 2>&1 || dnf -y install curl-minimal || true

# Lightweight single-node k3s (no traefik / servicelb — save RAM on t3.micro).
export INSTALL_K3S_SKIP_SELINUX_RPM=true
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server --write-kubeconfig-mode=644 --disable=traefik --disable=servicelb --disable=metrics-server" sh -
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
ln -sf /usr/local/bin/kubectl /usr/bin/kubectl || true

# Wait for node Ready
for i in $(seq 1 60); do
  if kubectl get nodes --no-headers 2>/dev/null | grep -q Ready; then
    break
  fi
  sleep 5
done

mkdir -p /opt/paks
# Prefer imperative create (no fragile YAML heredoc under cloud-init).
kubectl delete deploy paks-demo --ignore-not-found || true
kubectl create deployment paks-demo --image=registry.k8s.io/pause:3.9 --replicas=1
kubectl label deploy paks-demo app=paks-demo project=paks-k8s-live --overwrite
kubectl patch deploy paks-demo --type=strategic -p '{"spec":{"template":{"metadata":{"labels":{"app":"paks-demo"}},"spec":{"containers":[{"name":"pause","image":"registry.k8s.io/pause:3.9","resources":{"requests":{"cpu":"10m","memory":"16Mi"},"limits":{"cpu":"50m","memory":"32Mi"}}}]}}}}'
kubectl rollout status deployment/paks-demo --timeout=180s || true

# Marker for SSM wait loops
echo "$(date -Is) k3s+paks-demo ready" > /opt/paks/READY
chmod 644 /opt/paks/READY /etc/rancher/k3s/k3s.yaml
  EOF
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

data "aws_iam_policy_document" "node_extra" {
  statement {
    sid = "S3Results"
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:DeleteObject",
    ]
    resources = [
      aws_s3_bucket.results.arn,
      "${aws_s3_bucket.results.arn}/*",
    ]
  }
  statement {
    sid = "CloudWatchMetricsLogs"
    actions = [
      "cloudwatch:PutMetricData",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "node_extra" {
  name   = "${var.name_prefix}-node-extra"
  role   = aws_iam_role.node.id
  policy = data.aws_iam_policy_document.node_extra.json
}

resource "aws_iam_instance_profile" "node" {
  name = "${var.name_prefix}-node"
  role = aws_iam_role.node.name
}

resource "aws_security_group" "node" {
  name_prefix = "${var.name_prefix}-"
  vpc_id      = data.aws_vpc.default.id
  description = "PAKS single-node k3s (SSM only; no public kube API)"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.name_prefix}-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "results" {
  bucket        = "${var.name_prefix}-${data.aws_caller_identity.current.account_id}-${random_id.bucket_suffix.hex}"
  force_destroy = true

  tags = {
    Name = "${var.name_prefix}-results"
  }
}

resource "aws_s3_bucket_public_access_block" "results" {
  bucket                  = aws_s3_bucket.results.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_cloudwatch_log_group" "paks" {
  name              = "/paks-k8s-live/${var.name_prefix}"
  retention_in_days = 3
}

resource "aws_instance" "k3s" {
  ami                         = local.ami_id
  instance_type               = var.instance_type
  subnet_id                   = local.subnet_id
  vpc_security_group_ids      = [aws_security_group.node.id]
  iam_instance_profile        = aws_iam_instance_profile.node.name
  associate_public_ip_address = true

  root_block_device {
    volume_size = var.root_volume_gb
    volume_type = "gp3"
    encrypted   = true
  }

  metadata_options {
    http_tokens = "required"
  }

  user_data = local.user_data

  tags = {
    Name = "${var.name_prefix}-k3s"
    role = "k3s-single"
  }
}
