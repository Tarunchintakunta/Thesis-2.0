# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: public_storage | Label: secure | Module: ps-051-ps-opensearch-public-s01 | Pattern: ps-opensearch-public

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

resource "aws_opensearch_domain" "this" {
  domain_name    = "eval-ps-051-ps-opensearch-public-"
  engine_version = "OpenSearch_2.11"

  vpc_options {
    subnet_ids         = ["subnet-0evala", "subnet-0evalb"]
    security_group_ids = ["sg-0evalos"]
  }

  encrypt_at_rest {
    enabled = true
  }
  node_to_node_encryption {
    enabled = true
  }
  ebs_options {
    ebs_enabled = true
    volume_size = 10
  }
  cluster_config {
    instance_type = "t3.small.search"
  }
  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = "arn:aws:iam::123456789012:root"
      Action    = "es:*"
      Resource  = "*"
    }]
  })
}
