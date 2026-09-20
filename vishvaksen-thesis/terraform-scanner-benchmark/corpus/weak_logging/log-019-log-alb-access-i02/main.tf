# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: insecure | Module: log-019-log-alb-access-i02 | Pattern: log-alb-access

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

variable "access_logs_enabled" {
  type    = bool
  default = false
}

resource "aws_lb" "this" {
  name               = "eval-log-019-log-alb-access-i02"
  internal           = true
  load_balancer_type = "application"
  subnets            = ["subnet-0evala", "subnet-0evalb"]
  security_groups    = ["sg-0evallb"]

  access_logs {
    bucket  = "eval-tf-log-019-log-alb-access-i02-alblogs"
    enabled = var.access_logs_enabled
  }
  drop_invalid_header_fields = true
}
