# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: insecure | Module: log-020-log-alb-access-i03 | Pattern: log-alb-access

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

resource "aws_lb" "this" {
  name               = "eval-log-020-log-alb-access-i03"
  internal           = true
  load_balancer_type = "application"
  subnets            = ["subnet-0evala", "subnet-0evalb"]
  security_groups    = ["sg-0evallb"]

  access_logs {
    bucket  = "eval-tf-log-020-log-alb-access-i03-alblogs"
    enabled = false
  }
  drop_invalid_header_fields = true
}
