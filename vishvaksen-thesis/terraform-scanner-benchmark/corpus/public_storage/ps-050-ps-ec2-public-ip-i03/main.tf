# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: public_storage | Label: insecure | Module: ps-050-ps-ec2-public-ip-i03 | Pattern: ps-ec2-public-ip

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
  region = "ap-southeast-1"
}

resource "aws_instance" "this" {
  ami                         = "ami-0c1c8c9e0eval0001"
  instance_type               = "t3.micro"
  subnet_id                   = "subnet-0evali03"
  vpc_security_group_ids      = ["sg-0evali03"]
  associate_public_ip_address = true
  monitoring                  = true
  metadata_options {
    http_tokens = "required"
  }
  root_block_device {
    encrypted = true
  }
}
