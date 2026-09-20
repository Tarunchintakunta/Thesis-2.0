# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: insecure | Module: log-050-log-msk-broker-i03 | Pattern: log-msk-broker

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
  region = "ap-southeast-1"
}

resource "aws_msk_cluster" "this" {
  cluster_name           = "eval-log-050-log-msk-broker-i03"
  kafka_version          = "3.5.1"
  number_of_broker_nodes = 3
  broker_node_group_info {
    instance_type   = "kafka.t3.small"
    client_subnets  = ["subnet-0evala", "subnet-0evalb", "subnet-0evalc"]
    security_groups = ["sg-0evalmsk"]
  }
  encryption_info {
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }

  logging_info {
    broker_logs {
      cloudwatch_logs {
        enabled = false
      }
    }
  }

}
