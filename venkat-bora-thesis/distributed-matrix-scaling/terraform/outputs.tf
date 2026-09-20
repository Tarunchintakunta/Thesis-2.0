output "security_group_id" { value = aws_security_group.cluster.id }
output "instance_profile" { value = aws_iam_instance_profile.node.name }
output "scale_up_instance_id" {
  value = try(aws_instance.scale_up[0].id, null)
}
output "scale_up_private_ip" {
  value = try(aws_instance.scale_up[0].private_ip, null)
}
output "scale_out_instance_ids" {
  value = [for i in aws_instance.scale_out : i.id]
}
output "scale_out_private_ips" {
  value = [for i in aws_instance.scale_out : i.private_ip]
}
