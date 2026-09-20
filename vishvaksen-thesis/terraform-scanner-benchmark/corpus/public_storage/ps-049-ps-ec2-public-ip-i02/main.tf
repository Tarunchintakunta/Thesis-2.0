# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: public_storage | Label: insecure | Module: ps-049-ps-ec2-public-ip-i02 | Pattern: ps-ec2-public-ip

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
  region = "eu-central-1"
}

variable "associate_public_ip" {
  type    = bool
  default = true
}

resource "aws_instance" "this" {
  ami                         = "ami-0c1c8c9e0eval0001"
  instance_type               = "t3.micro"
  subnet_id                   = "subnet-0evali02"
  vpc_security_group_ids      = ["sg-0evali02"]
  associate_public_ip_address = var.associate_public_ip
  monitoring                  = true
  metadata_options {
    http_tokens = "required"
  }
  root_block_device {
    encrypted = true
  }
}
