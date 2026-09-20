# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: insecure | Module: enc-054-enc-glue-i02 | Pattern: enc-glue

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

variable "sse_at_rest" {
  type    = bool
  default = false
}

resource "aws_glue_data_catalog_encryption_settings" "this" {
  data_catalog_encryption_settings {
    encryption_at_rest {
      catalog_encryption_mode = "DISABLED"
      sse_aws_kms_key_id      = null
    }
    connection_password_encryption {
      return_connection_password_encrypted = var.sse_at_rest
    }
  }
}
