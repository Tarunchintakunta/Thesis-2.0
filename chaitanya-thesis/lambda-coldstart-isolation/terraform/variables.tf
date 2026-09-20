variable "region" {
  type    = string
  default = "eu-west-1"
}

variable "name_prefix" {
  type    = string
  default = "coldstart"
}

variable "memory_mb" {
  type    = number
  default = 1024
}

variable "lambda_package" {
  description = "Zip built by the project build scripts (python default)."
  type        = string
  default     = "../build/python-default.zip"
}
