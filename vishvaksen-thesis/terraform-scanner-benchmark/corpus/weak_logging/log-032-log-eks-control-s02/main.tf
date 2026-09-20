# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: secure | Module: log-032-log-eks-control-s02 | Pattern: log-eks-control

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

resource "aws_eks_cluster" "this" {
  name     = "eval-log-032-log-eks-control-s02"
  role_arn = "arn:aws:iam::123456789012:role/eval-eks"
  vpc_config {
    subnet_ids             = ["subnet-0evala", "subnet-0evalb"]
    endpoint_public_access = false
  }
  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
}
