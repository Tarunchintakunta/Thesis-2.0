variable "region" {
  type    = string
  default = "eu-west-1"
}

variable "name_prefix" {
  type    = string
  default = "securefl-ids"
}

variable "ami_id" {
  type        = string
  default     = ""
  description = "Optional AMI override. Empty = latest AL2023 x86_64 from SSM."
}

variable "instance_type" {
  type        = string
  default     = "t3.micro"
  description = "Free Tier default. Do not raise without budget review."
}

variable "create_server" {
  type        = bool
  default     = true
  description = "Create the FL server EC2 node (lite round)."
}

variable "client_count" {
  type        = number
  default     = 0
  description = "Extra client EC2 nodes. Lite uses 0 (in-process clients on server)."
}
