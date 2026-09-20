# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: public_storage | Label: insecure | Module: ps-043-ps-ami-public-i01 | Pattern: ps-ami-public

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
  region = "us-east-1"
}

resource "aws_ebs_volume" "this" {
  availability_zone = "us-east-1a"
  size              = 10
  encrypted         = true
}

resource "aws_ebs_snapshot" "this" {
  volume_id   = aws_ebs_volume.this.id
  description = "eval snapshot ps-043-ps-ami-public-i01"
}

resource "aws_ami" "this" {
  name                = "eval-ps-043-ps-ami-public-i01"
  virtualization_type = "hvm"
  root_device_name    = "/dev/xvda"
  ebs_block_device {
    device_name = "/dev/xvda"
    snapshot_id = aws_ebs_snapshot.this.id
  }
}


resource "aws_ami_launch_permission" "this" {
  image_id = aws_ami.this.id
  group    = "all"
}
