# Tags: project slug only — never personal name or personal ID.
provider "aws" {
  region = var.region
  default_tags {
    tags = {
      project    = "securefl-ids"
      managed_by = "terraform"
      purpose    = "research-eval"
      data       = "synthetic"
    }
  }
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

resource "aws_security_group" "fl" {
  name_prefix = "${var.name_prefix}-"
  vpc_id      = data.aws_vpc.default.id
  description = "SecureFL-IDS research nodes"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "server" {
  count = var.ami_id == "" ? 0 : 1

  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.fl.id]

  tags = {
    Name = "${var.name_prefix}-server"
    role = "fl-server"
  }
}

resource "aws_instance" "client" {
  count = var.ami_id == "" ? 0 : var.client_count

  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.fl.id]

  tags = {
    Name = "${var.name_prefix}-client-${count.index}"
    role = "fl-client"
  }
}
