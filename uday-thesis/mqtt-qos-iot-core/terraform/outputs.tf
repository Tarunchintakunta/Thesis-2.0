output "region" {
  value = var.region
}

output "name_prefix" {
  value = var.name_prefix
}

output "thing_names" {
  value = module.iot_core.thing_names
}

output "iot_policy_name" {
  value = module.iot_core.policy_name
}

output "iot_endpoint_need" {
  value       = "iot:DescribeEndpoint (iot:Data-ATS) — resolved after apply; not queried this pass"
  description = "Live simulator would read the ATS endpoint from AWS; this pass does not apply."
}

output "topic_rule_name" {
  value = module.ingest.rule_name
}

output "lambda_function_name" {
  value = module.ingest.lambda_function_name
}

output "delivered_table_name" {
  value = module.ingest.table_name
}

output "certificate_pems_in_state" {
  value       = "certificates are created on apply and stored in terraform state — destroy after the campaign"
  description = "Honesty: apply produces device certs. This pass does not apply."
}
