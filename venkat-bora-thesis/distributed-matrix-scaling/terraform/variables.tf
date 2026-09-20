variable "region" {
  type    = string
  default = "eu-west-1"
}

variable "name_prefix" {
  description = "Resource name prefix (project slug only; never a personal name or ID)."
  type        = string
  default     = "matrix-scale"
}

variable "ami_id" {
  description = "Empty = plan-only (no instances). Set to a Linux AMI to apply."
  type        = string
  default     = ""
}

variable "scale_up_instance_type" {
  description = "Single-node multi-threaded arm (aggregate vCPUs must match scale-out)."
  type        = string
  default     = "t3.small"
}

variable "scale_out_instance_type" {
  description = "Per-node type for distributed arm."
  type        = string
  default     = "t3.micro"
}

variable "scale_out_count" {
  description = "Worker/scheduler nodes for distributed arm; aggregate vCPUs should match scale-up."
  type        = number
  default     = 2
}

variable "key_name" {
  description = "Optional EC2 key pair for SSH; empty = no key."
  type        = string
  default     = ""
}
