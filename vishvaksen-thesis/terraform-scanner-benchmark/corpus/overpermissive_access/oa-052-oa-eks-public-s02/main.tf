# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: overpermissive_access | Label: secure | Module: oa-052-oa-eks-public-s02 | Pattern: oa-eks-public

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
  name     = "eval-oa-052-oa-eks-public-s02"
  role_arn = "arn:aws:iam::123456789012:role/eval-eks"
  vpc_config {
    subnet_ids              = ["subnet-0evala", "subnet-0evalb"]
    endpoint_public_access  = false
    endpoint_private_access = true
    public_access_cidrs     = ["10.0.0.0/16"]
  }
  enabled_cluster_log_types = ["api", "audit", "authenticator"]
}
