output "artifacts_bucket" { value = aws_s3_bucket.artifacts.id }
output "log_group" { value = aws_cloudwatch_log_group.fl.name }
output "server_id" { value = try(aws_instance.server[0].id, null) }
output "client_ids" { value = [for i in aws_instance.client : i.id] }
