variable "region" {
  type    = string
  default = "eu-west-1"
}

variable "name_prefix" {
  type    = string
  default = "coldstart-study"
}

variable "memory_mb" {
  type    = number
  default = 1024
}

variable "log_retention_days" {
  type    = number
  default = 7
}

variable "warming_schedule" {
  type    = string
  default = "rate(5 minutes)"
}

variable "enable_tracing" {
  type    = bool
  default = false
}

variable "python_default_package" {
  type    = string
  default = "../build/python-default.zip"
}

variable "python_optimised_package" {
  type    = string
  default = "../build/python-optimised.zip"
}

variable "nodejs_default_package" {
  type    = string
  default = "../build/nodejs-default.zip"
}

variable "nodejs_optimised_package" {
  type    = string
  default = "../build/nodejs-optimised.zip"
}

variable "java_default_package" {
  type    = string
  default = "../build/java-default/function.jar"
}

variable "java_optimised_package" {
  type    = string
  default = "../build/java-optimised/function.jar"
}
