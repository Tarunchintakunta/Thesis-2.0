variable "region" {
  type        = string
  description = ""
  default     = "eu-west-1"
}

variable "name_prefix" {
  type        = string
  description = "Resource name prefix. Must stay distinct from Venkat matrix-scale."
  default     = "paks-k8s-live"
}

variable "instance_type" {
  type        = string
  description = "Free-Tier-safe single-node type (avoid EKS)."
  default     = "t3.micro"
}

variable "ami_id" {
  type        = string
  description = "Amazon Linux 2023 AMI. Empty = look up latest AL2023 x86_64."
  default     = ""
}

variable "root_volume_gb" {
  type        = number
  description = "Root EBS size (keep small; Free Tier ~30 GiB total)."
  default     = 12
}
