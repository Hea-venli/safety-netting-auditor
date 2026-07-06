terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-west-2"
}

# --- Package the code ---
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/auditor.py"
  output_path = "${path.module}/auditor.zip"
}

# --- IAM: least privilege ---
resource "aws_iam_role" "auditor_role" {
  name = "safety-netting-auditor-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.auditor_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "invoke_bedrock" {
  name = "invoke-bedrock"
  role = aws_iam_role.auditor_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "bedrock:InvokeModel"
      Resource = "*"
    }]
  })
}

# --- The Lambda ---
resource "aws_lambda_function" "auditor" {
  function_name    = "safety-netting-auditor"
  role             = aws_iam_role.auditor_role.arn
  runtime          = "python3.12"
  handler          = "auditor.lambda_handler"
  timeout          = 30
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
}

# --- The front door ---
resource "aws_lambda_function_url" "auditor_url" {
  function_name      = aws_lambda_function.auditor.function_name
  authorization_type = "AWS_IAM"
}

output "auditor_url" {
  value = aws_lambda_function_url.auditor_url.function_url
}

# --- Monitoring: email me if the Lambda errors ---
resource "aws_sns_topic" "auditor_alerts" {
  name = "safety-netting-auditor-alerts"
}

resource "aws_sns_topic_subscription" "email_me" {
  topic_arn = aws_sns_topic.auditor_alerts.arn
  protocol  = "email"
  endpoint  = "heavenegho@hotmail.com"
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "safety-netting-auditor-errors"
  alarm_description   = "Fires if the auditor Lambda records any errors"
  namespace           = "AWS/Lambda"
  metric_name         = "Errors"
  dimensions          = { FunctionName = aws_lambda_function.auditor.function_name }
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 0
  comparison_operator = "GreaterThanThreshold"
  alarm_actions       = [aws_sns_topic.auditor_alerts.arn]
}
