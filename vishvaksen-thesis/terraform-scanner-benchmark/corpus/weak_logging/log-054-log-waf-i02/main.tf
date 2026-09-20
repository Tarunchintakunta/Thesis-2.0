# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: insecure | Module: log-054-log-waf-i02 | Pattern: log-waf

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

variable "enable_waf_logging" {
  type    = bool
  default = false
}

resource "aws_wafv2_web_acl" "this" {
  name  = "eval-log-054-log-waf-i02"
  scope = "REGIONAL"
  default_action {
    allow {}
  }
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "evali02"
    sampled_requests_enabled   = true
  }
}
