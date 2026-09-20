# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: secure | Module: enc-007-enc-ebs-s02 | Pattern: enc-ebs

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
  region = "eu-west-2"
}

resource "aws_ebs_volume" "this" {
  availability_zone = "eu-west-2a"
  size              = 20
  type              = "gp3"
  encrypted         = true
}
