output "instance_id" {
  description = "EC2 instance id for the single-node k3s host."
  value       = aws_instance.k3s.id
}

output "instance_private_ip" {
  value = aws_instance.k3s.private_ip
}

output "s3_bucket" {
  description = "Results / trace upload bucket."
  value       = aws_s3_bucket.results.bucket
}

output "cloudwatch_log_group" {
  value = aws_cloudwatch_log_group.paks.name
}

output "region" {
  value = var.region
}

output "project_tag" {
  value = "paks-k8s-live"
}

output "ami_id" {
  value = local.ami_id
}

output "destroy_hint" {
  value = "cd terraform && terraform destroy -auto-approve  # only destroys project=paks-k8s-live"
}
