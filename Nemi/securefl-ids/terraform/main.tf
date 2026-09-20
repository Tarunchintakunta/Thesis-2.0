# Tags: project slug only — never personal name or personal ID.
# Lite live cloud FL: 1× t3.micro (Free Tier) + S3 artefacts + CloudWatch.
# In-process federated clients on the server node; client EC2 count defaults to 0.
# Do not use Lambda (shared-account ConcurrentExecutions=10; Vikas campaign owns it).

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      project    = "securefl-ids"
      managed_by = "terraform"
      purpose    = "research-eval"
      data       = "unsw-nb15-lite"
    }
  }
}

data "aws_caller_identity" "current" {}

data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

locals {
  ami_id    = var.ami_id != "" ? var.ami_id : data.aws_ssm_parameter.al2023.value
  user_data = <<-EOF
    #!/bin/bash
    set -euxo pipefail
    exec > /var/log/securefl-userdata.log 2>&1
    fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    grep -q '^/swapfile ' /etc/fstab || echo '/swapfile swap swap defaults 0 0' >> /etc/fstab
    dnf -y install python3.11 python3.11-pip python3.11-devel gcc tar gzip || yum -y install python3 python3-pip gcc tar gzip
    mkdir -p /opt/securefl-ids
    echo ready > /opt/securefl-ids/USERDATA_READY
  EOF
}

resource "aws_s3_bucket" "artifacts" {
  bucket_prefix = "${var.name_prefix}-artifacts-"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket                  = aws_s3_bucket.artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_cloudwatch_log_group" "fl" {
  name              = "/research/${var.name_prefix}"
  retention_in_days = 14
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
  name_prefix        = "${var.name_prefix}-node-"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume.json
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

data "aws_iam_policy_document" "fl_runtime" {
  statement {
    sid = "S3Artefacts"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket",
      "s3:DeleteObject",
    ]
    resources = [
      aws_s3_bucket.artifacts.arn,
      "${aws_s3_bucket.artifacts.arn}/*",
    ]
  }
  statement {
    sid = "CloudWatchLogs"
    actions = [
      "logs:CreateLogStream",
      "logs:DescribeLogStreams",
      "logs:PutLogEvents",
    ]
    resources = [
      aws_cloudwatch_log_group.fl.arn,
      "${aws_cloudwatch_log_group.fl.arn}:*",
    ]
  }
  statement {
    sid       = "CloudWatchMetrics"
    actions   = ["cloudwatch:PutMetricData"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "fl_runtime" {
  name   = "fl-runtime"
  role   = aws_iam_role.node.id
  policy = data.aws_iam_policy_document.fl_runtime.json
}

resource "aws_iam_instance_profile" "node" {
  name_prefix = "${var.name_prefix}-node-"
  role        = aws_iam_role.node.name
}

resource "aws_security_group" "fl" {
  name_prefix = "${var.name_prefix}-"
  vpc_id      = data.aws_vpc.default.id
  description = "SecureFL-IDS research nodes (egress only)"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "server" {
  count = var.create_server ? 1 : 0

  ami                         = local.ami_id
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.fl.id]
  iam_instance_profile        = aws_iam_instance_profile.node.name
  associate_public_ip_address = true
  user_data                   = local.user_data
  user_data_replace_on_change = true

  root_block_device {
    volume_size = 16
    volume_type = "gp3"
    encrypted   = true
  }

  metadata_options {
    http_tokens = "required"
  }

  tags = {
    Name = "${var.name_prefix}-server"
    role = "fl-server"
  }

  depends_on = [
    aws_iam_role_policy_attachment.ssm,
    aws_iam_role_policy.fl_runtime,
  ]
}

resource "aws_instance" "client" {
  count = var.create_server ? var.client_count : 0

  ami                         = local.ami_id
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.fl.id]
  iam_instance_profile        = aws_iam_instance_profile.node.name
  associate_public_ip_address = true
  user_data                   = local.user_data
  user_data_replace_on_change = true

  root_block_device {
    volume_size = 16
    volume_type = "gp3"
    encrypted   = true
  }

  metadata_options {
    http_tokens = "required"
  }

  tags = {
    Name = "${var.name_prefix}-client-${count.index}"
    role = "fl-client"
  }
}
