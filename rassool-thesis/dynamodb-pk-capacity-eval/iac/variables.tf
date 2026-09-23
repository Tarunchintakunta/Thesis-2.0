variable "region" {
  description = "One region for everything (external validity is stated as single-region)."
  type        = string
  default     = "eu-west-1"
}

variable "table_prefix" {
  type    = string
  default = "ddbpk"
}

variable "provisioned_capacity" {
  description = "Auto-scaling bounds per key design for the PROVISIONED tables (written by scripts/render_tfvars.py)."
  type = map(object({
    read_min  = number
    read_max  = number
    write_min = number
    write_max = number
  }))
}

variable "target_utilisation" {
  description = "Auto-scaling target utilisation in percent."
  type        = number
  default     = 70
}

variable "seed_mode" {
  description = "true while loading the 1M items: raises the write floor of the provisioned tables."
  type        = bool
  default     = false
}

variable "seed_write_capacity" {
  type    = number
  default = 2000
}

variable "function_name" {
  type    = string
  default = "ddbpk-driver"
}

variable "lambda_package" {
  description = "Zip built by scripts/build_lambda.sh."
  type        = string
  default     = "build/driver.zip"
}

variable "lambda_memory" {
  type    = number
  default = 1769
}
