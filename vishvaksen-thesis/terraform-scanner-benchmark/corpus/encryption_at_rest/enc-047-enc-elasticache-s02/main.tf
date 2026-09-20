# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: secure | Module: enc-047-enc-elasticache-s02 | Pattern: enc-elasticache

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

resource "aws_elasticache_replication_group" "this" {
  replication_group_id       = "eval-enc-047-enc-elasticache-s02"
  description                = "eval enc-047-enc-elasticache-s02"
  node_type                  = "cache.t3.micro"
  num_cache_clusters         = 1
  automatic_failover_enabled = false
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
}
