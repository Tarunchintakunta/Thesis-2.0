# One DynamoDB table. Key schema and billing mode are parameters, so the six
# configurations are built by the same code. PROVISIONED tables get target
# tracking auto-scaling on reads and writes.

variable "name" {
  type = string
}

variable "hash_key" {
  type = string
}

variable "range_key" {
  type    = string
  default = null
}

variable "billing_mode" {
  type = string

  validation {
    condition     = contains(["PAY_PER_REQUEST", "PROVISIONED"], var.billing_mode)
    error_message = "billing_mode must be PAY_PER_REQUEST or PROVISIONED."
  }
}

variable "capacity" {
  type = object({
    read_min  = number
    read_max  = number
    write_min = number
    write_max = number
  })
}

variable "target_utilisation" {
  type = number
}

variable "seed_mode" {
  type    = bool
  default = false
}

variable "seed_write_capacity" {
  type    = number
  default = 2000
}

locals {
  provisioned = var.billing_mode == "PROVISIONED"
  write_floor = var.seed_mode ? max(var.seed_write_capacity, var.capacity.write_min) : var.capacity.write_min
}

resource "aws_dynamodb_table" "this" {
  name           = var.name
  billing_mode   = var.billing_mode
  hash_key       = var.hash_key
  range_key      = var.range_key
  table_class    = "STANDARD"
  read_capacity  = local.provisioned ? var.capacity.read_min : null
  write_capacity = local.provisioned ? var.capacity.write_min : null

  attribute {
    name = var.hash_key
    type = "S"
  }

  dynamic "attribute" {
    for_each = var.range_key == null ? [] : [var.range_key]
    content {
      name = attribute.value
      type = "S"
    }
  }

  point_in_time_recovery {
    enabled = false
  }

  lifecycle {
    # auto-scaling owns the numbers once the table exists
    ignore_changes = [read_capacity, write_capacity]
  }
}

resource "aws_appautoscaling_target" "read" {
  count              = local.provisioned ? 1 : 0
  service_namespace  = "dynamodb"
  resource_id        = "table/${aws_dynamodb_table.this.name}"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  min_capacity       = var.capacity.read_min
  max_capacity       = var.capacity.read_max
}

resource "aws_appautoscaling_policy" "read" {
  count              = local.provisioned ? 1 : 0
  name               = "${var.name}-read"
  policy_type        = "TargetTrackingScaling"
  service_namespace  = aws_appautoscaling_target.read[0].service_namespace
  resource_id        = aws_appautoscaling_target.read[0].resource_id
  scalable_dimension = aws_appautoscaling_target.read[0].scalable_dimension

  target_tracking_scaling_policy_configuration {
    target_value = var.target_utilisation

    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }
  }
}

resource "aws_appautoscaling_target" "write" {
  count              = local.provisioned ? 1 : 0
  service_namespace  = "dynamodb"
  resource_id        = "table/${aws_dynamodb_table.this.name}"
  scalable_dimension = "dynamodb:table:WriteCapacityUnits"
  min_capacity       = local.write_floor
  max_capacity       = max(var.capacity.write_max, local.write_floor)
}

resource "aws_appautoscaling_policy" "write" {
  count              = local.provisioned ? 1 : 0
  name               = "${var.name}-write"
  policy_type        = "TargetTrackingScaling"
  service_namespace  = aws_appautoscaling_target.write[0].service_namespace
  resource_id        = aws_appautoscaling_target.write[0].resource_id
  scalable_dimension = aws_appautoscaling_target.write[0].scalable_dimension

  target_tracking_scaling_policy_configuration {
    target_value = var.target_utilisation

    predefined_metric_specification {
      predefined_metric_type = "DynamoDBWriteCapacityUtilization"
    }
  }
}

output "name" {
  value = aws_dynamodb_table.this.name
}

output "arn" {
  value = aws_dynamodb_table.this.arn
}

output "billing_mode" {
  value = aws_dynamodb_table.this.billing_mode
}
