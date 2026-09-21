# Free-Tier-leaning AWS IoT Core + Rules + Lambda + DynamoDB.
# Project tags only (no personal IDs). Default enable_apply=false.
# Apply only for lite/smoke after READY_FOR_AWS gates; destroy after campaign.

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = "mqtt-qos-iot-core"
      Thesis      = "uday-mqtt-qos"
      Environment = "research"
      ManagedBy   = "terraform"
      Campaign    = "lite"
    }
  }
}

locals {
  prefix          = "${var.name_prefix}-${var.stage}"
  telemetry_topic = "devices/+/telemetry"
  apply           = var.enable_apply
}

data "archive_file" "ingest_zip" {
  type        = "zip"
  source_file = "${path.module}/../src/lambda_ingest/handler.py"
  output_path = "${path.module}/build/ingest.zip"
}

module "iot_core" {
  count  = local.apply ? 1 : 0
  source = "./modules/iot_core"

  prefix       = local.prefix
  device_count = var.device_count
  region       = var.region
}

module "ingest" {
  count  = local.apply ? 1 : 0
  source = "./modules/ingest"

  prefix             = local.prefix
  region             = var.region
  lambda_zip         = data.archive_file.ingest_zip.output_path
  lambda_zip_hash    = data.archive_file.ingest_zip.output_base64sha256
  lambda_memory_mb   = var.lambda_memory_mb
  lambda_timeout_s   = var.lambda_timeout_s
  log_retention_days = var.log_retention_days
  ttl_seconds        = var.ttl_seconds
  telemetry_topic    = local.telemetry_topic
}

# Materialise device certs for the live publisher (gitignored .certs/).
resource "local_file" "device_cert" {
  count = local.apply ? var.device_count : 0

  content         = module.iot_core[0].certificate_pems[count.index]
  filename        = "${path.module}/../.certs/device-${format("%02d", count.index + 1)}/cert.pem"
  file_permission = "0600"
}

resource "local_file" "device_key" {
  count = local.apply ? var.device_count : 0

  content         = module.iot_core[0].private_keys[count.index]
  filename        = "${path.module}/../.certs/device-${format("%02d", count.index + 1)}/private.key"
  file_permission = "0600"
}

resource "local_file" "stack_meta" {
  count = local.apply ? 1 : 0

  content = jsonencode({
    region              = var.region
    name_prefix         = local.prefix
    thing_names         = module.iot_core[0].thing_names
    delivered_table     = module.ingest[0].table_name
    lambda_function     = module.ingest[0].lambda_function_name
    rule_name           = module.ingest[0].rule_name
    telemetry_topic_tpl = "devices/{thing_name}/telemetry"
    destroy_hook        = "scripts/destroy_stack.sh"
    tags = {
      Project     = "mqtt-qos-iot-core"
      Thesis      = "uday-mqtt-qos"
      Environment = "research"
      ManagedBy   = "terraform"
      Campaign    = "lite"
    }
  })
  filename        = "${path.module}/../.certs/stack_meta.json"
  file_permission = "0644"
}
