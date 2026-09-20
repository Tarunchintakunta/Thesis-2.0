# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: secure | Module: log-051-log-waf-s01 | Pattern: log-waf

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

resource "aws_wafv2_web_acl" "this" {
  name  = "eval-log-051-log-waf-s01"
  scope = "REGIONAL"
  default_action {
    allow {}
  }
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "evals01"
    sampled_requests_enabled   = true
  }
}


resource "aws_wafv2_web_acl_logging_configuration" "this" {
  resource_arn            = aws_wafv2_web_acl.this.arn
  log_destination_configs = ["arn:aws:logs:eu-west-1:123456789012:log-group:aws-waf-logs-eval"]
}
