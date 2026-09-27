provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "eu-west-1"
}

module "webhook" {
  source      = "../../modules/webhook"
  project     = "webhook-reliability-eval"
  environment = "dev"
}

output "main_queue_url" { value = module.webhook.main_queue_url }
output "dlq_url" { value = module.webhook.dlq_url }
