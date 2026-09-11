output "table_names" {
  description = "configuration id (k1-ondemand ...) => table name"
  value       = { for k, t in module.tables : k => t.name }
}

output "results_bucket" {
  value = aws_s3_bucket.results.bucket
}

output "function_name" {
  value = module.lambda.function_name
}

output "dashboard" {
  value = module.monitoring.dashboard_name
}

output "operator_policy_json" {
  description = "Least-privilege policy for the person running scripts/run_matrix.py and collect_metrics.py"
  value       = module.iam.operator_policy_json
}
