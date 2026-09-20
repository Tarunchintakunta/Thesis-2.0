# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: public_storage | Label: secure | Module: ps-041-ps-ami-public-s01 | Pattern: ps-ami-public

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-west-1"
}

resource "aws_ebs_volume" "this" {
  availability_zone = "eu-west-1a"
  size              = 10
  encrypted         = true
}

resource "aws_ebs_snapshot" "this" {
  volume_id   = aws_ebs_volume.this.id
  description = "eval snapshot ps-041-ps-ami-public-s01"
}

resource "aws_ami" "this" {
  name                = "eval-ps-041-ps-ami-public-s01"
  virtualization_type = "hvm"
  root_device_name    = "/dev/xvda"
  ebs_block_device {
    device_name = "/dev/xvda"
    snapshot_id = aws_ebs_snapshot.this.id
  }
}


resource "aws_snapshot_create_volume_permission" "this" {
  snapshot_id = aws_ebs_snapshot.this.id
  account_id  = "123456789012"
}
