# Terraform stub — webhook reliability stack (API GW + SQS + DLQ + Lambda + ElastiCache)
# NOT applied in local floor evaluation. No secrets committed.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "project" {
  type    = string
  default = "webhook-reliability-eval"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "hmac_secret_param" {
  type        = string
  description = "SSM/Secrets Manager name for HMAC secret — never commit the value"
  default     = "/webhook-reliability/hmac_secret"
}

resource "aws_sqs_queue" "dlq" {
  name                      = "${var.project}-${var.environment}-dlq"
  message_retention_seconds = 1209600
}

resource "aws_sqs_queue" "main" {
  name                       = "${var.project}-${var.environment}-main"
  visibility_timeout_seconds = 60
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })
}

# Placeholders — wire Lambda, API Gateway HTTP API, ElastiCache Redis in live phase.
output "main_queue_url" { value = aws_sqs_queue.main.id }
output "dlq_url" { value = aws_sqs_queue.dlq.id }
output "note" {
  value = "Stub only — apply only with student AWS account; destroy after campaigns; never commit secrets."
}
