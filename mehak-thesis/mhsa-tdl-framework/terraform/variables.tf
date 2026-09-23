variable "region" {
  type    = string
  default = "eu-west-1"
}

variable "name_prefix" {
  type    = string
  default = "mhsa-tdl"
}

variable "stream_name" {
  type    = string
  default = "ClusterTelemetryStream"
}

variable "function_name" {
  type    = string
  default = "MHSAPredictionFunction"
}

variable "lambda_package" {
  description = "Zip of src/lambda_handler/ (app.py + model/)."
  type        = string
  default     = "../build/lambda_handler.zip"
}
