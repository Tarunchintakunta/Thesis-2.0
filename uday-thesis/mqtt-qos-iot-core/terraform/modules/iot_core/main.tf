variable "prefix" {
  type        = string
  description = "Name prefix (project slug + stage)."
}

variable "device_count" {
  type = number
}

variable "region" {
  type = string
}

data "aws_caller_identity" "current" {}

locals {
  account = data.aws_caller_identity.current.account_id
  # Client id and publish topic are bound to the thing name.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["iot:Connect"]
        Resource = "arn:aws:iot:${var.region}:${local.account}:client/$${iot:Connection.Thing.ThingName}"
      },
      {
        Effect   = "Allow"
        Action   = ["iot:Publish"]
        Resource = "arn:aws:iot:${var.region}:${local.account}:topic/devices/$${iot:Connection.Thing.ThingName}/telemetry"
      }
    ]
  })
}

resource "aws_iot_thing_type" "device" {
  name = "${var.prefix}-device"
}

resource "aws_iot_thing" "device" {
  count           = var.device_count
  name            = format("%s-device-%02d", var.prefix, count.index + 1)
  thing_type_name = aws_iot_thing_type.device.name
}

resource "aws_iot_certificate" "device" {
  count  = var.device_count
  active = true
}

resource "aws_iot_policy" "publish" {
  name   = "${var.prefix}-publish"
  policy = local.policy
}

resource "aws_iot_policy_attachment" "device" {
  count  = var.device_count
  policy = aws_iot_policy.publish.name
  target = aws_iot_certificate.device[count.index].arn
}

resource "aws_iot_thing_principal_attachment" "device" {
  count     = var.device_count
  thing     = aws_iot_thing.device[count.index].name
  principal = aws_iot_certificate.device[count.index].arn
}

output "thing_names" {
  value = [for t in aws_iot_thing.device : t.name]
}

output "policy_name" {
  value = aws_iot_policy.publish.name
}

output "certificate_arns" {
  value     = [for c in aws_iot_certificate.device : c.arn]
  sensitive = true
}
