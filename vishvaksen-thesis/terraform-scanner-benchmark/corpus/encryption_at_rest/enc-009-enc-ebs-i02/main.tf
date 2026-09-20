# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: insecure | Module: enc-009-enc-ebs-i02 | Pattern: enc-ebs

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

variable "encrypted" {
  type    = bool
  default = false
}

resource "aws_ebs_volume" "this" {
  availability_zone = "eu-central-1a"
  size              = 20
  type              = "gp3"
  encrypted         = var.encrypted
}
