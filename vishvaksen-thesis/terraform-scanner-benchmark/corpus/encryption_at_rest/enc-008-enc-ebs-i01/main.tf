# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: insecure | Module: enc-008-enc-ebs-i01 | Pattern: enc-ebs

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
  size              = 20
  type              = "gp3"
  encrypted         = false
}
