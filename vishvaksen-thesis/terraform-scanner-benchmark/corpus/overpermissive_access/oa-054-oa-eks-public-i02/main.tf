# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: overpermissive_access | Label: insecure | Module: oa-054-oa-eks-public-i02 | Pattern: oa-eks-public

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

variable "endpoint_public_access" {
  type    = bool
  default = true
}

variable "public_access_cidrs" {
  type    = list(string)
  default = ["0.0.0.0/0"]
}

resource "aws_eks_cluster" "this" {
  name     = "eval-oa-054-oa-eks-public-i02"
  role_arn = "arn:aws:iam::123456789012:role/eval-eks"
  vpc_config {
    subnet_ids              = ["subnet-0evala", "subnet-0evalb"]
    endpoint_public_access  = var.endpoint_public_access
    endpoint_private_access = true
    public_access_cidrs     = var.public_access_cidrs
  }
  enabled_cluster_log_types = ["api", "audit", "authenticator"]
}
