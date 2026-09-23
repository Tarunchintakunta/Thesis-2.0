# Defaults mirror config/versions.yaml and config/experiment.yaml
# (tests/test_infra.py fails if they drift apart).

variable "region" {
  type    = string
  default = "eu-west-1"
}

variable "table_name" {
  type    = string
  default = "idem-eval"
}

variable "function_name" {
  type    = string
  default = "idem-eval-fn"
}

variable "lambda_package" {
  description = "zip built by scripts/build_lambda.sh"
  type        = string
  default     = "../build/lambda.zip"
}

variable "memory_mb" {
  type    = number
  default = 256
}

variable "timeout_s" {
  description = "an injected timeout sleeps past this after the write has committed"
  type        = number
  default     = 2
}

variable "p3_key_ttl_s" {
  type    = number
  default = 3600
}

variable "reserved_concurrency" {
  description = "-1 = no reservation (new accounts often cannot reserve any)"
  type        = number
  default     = -1
}
