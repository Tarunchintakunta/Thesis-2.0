output "note" {
  value = var.enable_apply ? "Resources created — run scripts/destroy_stack.sh after campaign." : "Scaffold only; enable_apply=false (live AWS not applied)."
}

output "region" {
  value = var.region
}

output "name_prefix" {
  value = "${var.name_prefix}-${var.stage}"
}

output "enable_apply" {
  value = var.enable_apply
}

output "thing_names" {
  value = try(module.iot_core[0].thing_names, [])
}

output "iot_policy_name" {
  value = try(module.iot_core[0].policy_name, null)
}

output "topic_rule_name" {
  value = try(module.ingest[0].rule_name, null)
}

output "lambda_function_name" {
  value = try(module.ingest[0].lambda_function_name, null)
}

output "delivered_table_name" {
  value = try(module.ingest[0].table_name, null)
}

output "certs_dir" {
  value       = var.enable_apply ? "${path.module}/../.certs" : null
  description = "Device certs written on apply; gitignored; removed on destroy."
}

output "destroy_hook" {
  value = "scripts/destroy_stack.sh"
}

output "default_tags" {
  value = {
    Project     = "mqtt-qos-iot-core"
    Thesis      = "uday-mqtt-qos"
    Environment = "research"
    ManagedBy   = "terraform"
    Campaign    = "lite"
  }
}
