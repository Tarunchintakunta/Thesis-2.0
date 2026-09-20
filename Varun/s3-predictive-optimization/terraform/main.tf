# Live S3 FinOps evaluation bucket + runner IAM for predictive storage-class study.
# Tags: project slug only — never personal name or personal ID.

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      project    = "s3-predictive-optimization"
      managed_by = "terraform"
      purpose    = "research-eval"
      data       = "synthetic"
    }
  }
}

resource "aws_s3_bucket" "eval" {
  bucket_prefix = "${var.name_prefix}-"
  force_destroy = var.force_destroy
}

resource "aws_s3_bucket_public_access_block" "eval" {
  bucket                  = aws_s3_bucket.eval.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "eval" {
  bucket = aws_s3_bucket.eval.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "eval" {
  bucket = aws_s3_bucket.eval.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_cloudwatch_log_group" "runner" {
  name              = "/research/${var.name_prefix}"
  retention_in_days = 14
}

data "aws_iam_policy_document" "assume_runner" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "runner" {
  name               = "${var.name_prefix}-runner"
  assume_role_policy = data.aws_iam_policy_document.assume_runner.json
}

data "aws_iam_policy_document" "runner" {
  statement {
    sid = "S3Eval"
    actions = [
      "s3:ListBucket",
      "s3:GetBucketLocation",
      "s3:GetBucketVersioning",
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:GetBucketLifecycleConfiguration",
      "s3:PutBucketLifecycleConfiguration",
      "s3:GetIntelligentTieringConfiguration",
      "s3:PutIntelligentTieringConfiguration",
      "s3:GetInventoryConfiguration",
      "s3:PutInventoryConfiguration",
    ]
    resources = [
      aws_s3_bucket.eval.arn,
      "${aws_s3_bucket.eval.arn}/*",
    ]
  }

  statement {
    sid       = "CloudWatchLogs"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.runner.arn}:*"]
  }

  statement {
    sid       = "PricingRead"
    actions   = ["pricing:GetProducts", "pricing:DescribeServices"]
    resources = ["*"]
  }

  statement {
    sid = "CostExplorerRead"
    actions = [
      "ce:GetCostAndUsage",
      "ce:GetCostForecast",
    ]
    resources = ["*"]
  }

  statement {
    sid = "CloudWatchMetrics"
    actions = [
      "cloudwatch:GetMetricData",
      "cloudwatch:GetMetricStatistics",
      "cloudwatch:ListMetrics",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "runner" {
  name   = "runner"
  role   = aws_iam_role.runner.id
  policy = data.aws_iam_policy_document.runner.json
}

resource "aws_iam_instance_profile" "runner" {
  name = "${var.name_prefix}-runner"
  role = aws_iam_role.runner.name
}
