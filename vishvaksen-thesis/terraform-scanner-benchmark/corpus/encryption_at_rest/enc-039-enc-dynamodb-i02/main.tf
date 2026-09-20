# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: insecure | Module: enc-039-enc-dynamodb-i02 | Pattern: enc-dynamodb

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

variable "sse_enabled" {
  type    = bool
  default = false
}

resource "aws_dynamodb_table" "this" {
  name           = "eval-enc-039-enc-dynamodb-i02"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  attribute {
    name = "id"
    type = "S"
  }
  point_in_time_recovery {
    enabled = true
  }
  server_side_encryption {
    enabled = var.sse_enabled
  }
}
