variable "region" {
  type    = string
  default = "eu-west-1"
}

variable "name_prefix" {
  description = "Resource name prefix (project slug only; never a personal name or ID)."
  type        = string
  default     = "s3-pred-opt"
}

variable "force_destroy" {
  description = "Allow terraform destroy to empty the evaluation bucket."
  type        = bool
  default     = true
}
