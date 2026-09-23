# MHSA-TDL Cluster Health Prediction Pipeline - Kinesis and Lambda
# Tags: project slug only — never personal name or personal ID.

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      project    = "mhsa-tdl-framework"
      managed_by = "terraform"
      purpose    = "research-eval"
      data       = "synthetic"
    }
  }
}

data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "inference" {
  name               = "${var.name_prefix}-inference"
  assume_role_policy = data.aws_iam_policy_document.assume.json
}

resource "aws_iam_role_policy_attachment" "kinesis" {
  role       = aws_iam_role.inference.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaKinesisExecutionRole"
}

resource "aws_iam_role_policy_attachment" "basic" {
  role       = aws_iam_role.inference.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_kinesis_stream" "telemetry" {
  name             = var.stream_name
  shard_count      = 1
  retention_period = 24
}

resource "aws_lambda_function" "prediction" {
  count = fileexists(var.lambda_package) ? 1 : 0

  function_name    = var.function_name
  role             = aws_iam_role.inference.arn
  runtime          = "python3.9"
  handler          = "app.lambda_handler"
  filename         = var.lambda_package
  source_code_hash = filebase64sha256(var.lambda_package)
  timeout          = 30
  memory_size      = 1024
}

resource "aws_lambda_event_source_mapping" "stream" {
  count = fileexists(var.lambda_package) ? 1 : 0

  event_source_arn  = aws_kinesis_stream.telemetry.arn
  function_name     = aws_lambda_function.prediction[0].arn
  starting_position = "LATEST"
  batch_size        = 100
}
