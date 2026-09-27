# Stub only — illustrates intended AWS resources for live phase.
terraform {
  required_version = ">= 1.5.0"
}
# aws_db_instance.postgres, aws_elasticache_replication_group.redis,
# aws_apigatewayv2_api.api — omitted until live gate.
output "note" { value = "Stub — local docker-compose / in-memory used for floor." }
