variable "region" {
  type        = string
  default     = "eu-west-1"
  description = ""
}

variable "name_prefix" {
  type        = string
  default     = "mqtt-qos"
  description = "Resource name prefix. Project slug only — never a personal name or student ID."

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.name_prefix)) && !can(regex("[0-9]{6,}", var.name_prefix))
    error_message = "name_prefix must be a lowercase project slug without long numeric IDs."
  }
}

variable "stage" {
  type    = string
  default = "lite"
}

variable "device_count" {
  type        = number
  default     = 5
  description = ""
}

variable "lambda_memory_mb" {
  type    = number
  default = 128
}

variable "lambda_timeout_s" {
  type    = number
  default = 10
}

variable "log_retention_days" {
  type    = number
  default = 7
}

variable "ttl_seconds" {
  type        = number
  default     = 1209600
  description = "DynamoDB TTL (14 days) so delivered rows expire after the campaign."
}

variable "enable_apply" {
  description = "Safety latch. Must be true to create resources; default false."
  type        = bool
  default     = false
}
