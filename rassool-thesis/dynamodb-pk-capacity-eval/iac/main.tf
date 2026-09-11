# Six DynamoDB tables (3 key designs x 2 capacity modes), the load-generator
# Lambda, its IAM role, a results bucket and the monitoring. Everything carries
# the project / student tags. `terraform destroy` removes all of it.

provider "aws" {
  region = var.region

  default_tags {
    tags = local.tags
  }
}

locals {
  tags = {
    project = "dynamodb-pk-capacity"
    student = "24205478"
  }

  designs = {
    K1 = { hash_key = "orderId", range_key = null }
    K2 = { hash_key = "customerId", range_key = "orderTs" }
    K3 = { hash_key = "shardKey", range_key = null }
  }

  modes = {
    ondemand    = "PAY_PER_REQUEST"
    provisioned = "PROVISIONED"
  }

  # "k1-ondemand" => { design = "K1", mode = "ondemand" }, ... six in total
  configurations = {
    for pair in setproduct(keys(local.designs), keys(local.modes)) :
    "${lower(pair[0])}-${pair[1]}" => { design = pair[0], mode = pair[1] }
  }
}

module "tables" {
  source   = "./tables"
  for_each = local.configurations

  name                = "${var.table_prefix}-${each.key}"
  hash_key            = local.designs[each.value.design].hash_key
  range_key           = local.designs[each.value.design].range_key
  billing_mode        = local.modes[each.value.mode]
  capacity            = var.provisioned_capacity[each.value.design]
  target_utilisation  = var.target_utilisation
  seed_mode           = var.seed_mode
  seed_write_capacity = var.seed_write_capacity
}

resource "aws_s3_bucket" "results" {
  bucket_prefix = "${var.table_prefix}-results-"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "results" {
  bucket                  = aws_s3_bucket.results.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "results" {
  bucket = aws_s3_bucket.results.id

  rule {
    id     = "expire-raw"
    status = "Enabled"

    filter {
      prefix = "raw/"
    }

    expiration {
      days = 90
    }
  }
}

module "iam" {
  source = "./iam"

  table_arns         = [for t in module.tables : t.arn]
  results_bucket_arn = aws_s3_bucket.results.arn
  function_name      = var.function_name
}

module "lambda" {
  source = "./lambda"

  function_name  = var.function_name
  role_arn       = module.iam.driver_role_arn
  package        = var.lambda_package
  memory         = var.lambda_memory
  results_bucket = aws_s3_bucket.results.bucket
}

module "monitoring" {
  source = "./monitoring"

  tables             = { for k, t in module.tables : k => t.name }
  function_name      = module.lambda.function_name
  region             = var.region
  monthly_budget_usd = var.monthly_budget_usd
  budget_email       = var.budget_email
}
