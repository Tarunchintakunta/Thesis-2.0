# MQTT QoS reliability stack: IoT Core things + rule → Lambda → DynamoDB.
# Tags and names use the project slug only. Do not apply in this pass.

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      project    = "mqtt-qos-iot-core"
      managed_by = "terraform"
      purpose    = "research-eval"
      data       = "synthetic"
      stage      = var.stage
    }
  }
}

locals {
  prefix = "${var.name_prefix}-${var.stage}"
}

data "archive_file" "ingest" {
  type        = "zip"
  source_dir  = "${path.module}/../src/lambda_ingest"
  output_path = "${path.module}/../build/ingest.zip"
  excludes    = ["__pycache__", "*.pyc"]
}

module "iot_core" {
  source       = "./modules/iot_core"
  prefix       = local.prefix
  device_count = var.device_count
  region       = var.region
}

module "ingest" {
  source             = "./modules/ingest"
  prefix             = local.prefix
  region             = var.region
  lambda_zip         = data.archive_file.ingest.output_path
  lambda_zip_hash    = data.archive_file.ingest.output_base64sha256
  lambda_memory_mb   = var.lambda_memory_mb
  lambda_timeout_s   = var.lambda_timeout_s
  log_retention_days = var.log_retention_days
  ttl_seconds        = var.ttl_seconds
  telemetry_topic    = "devices/+/telemetry"
}
