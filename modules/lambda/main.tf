module "sqs_message_processor" {
  source                 = "Adaptavist/aws-lambda/module"
  version                = "1.13.0"
  name                   = var.function_name
  namespace              = var.namespace
  stage                  = var.stage
  tags                   = var.tags
  lambda_code_dir        = var.code_dir
  handler                = "app.lambda_handler"
  runtime                = "python3.8"
  timeout                = 60
  memory_size            = 512
  description            = var.description
  function_name          = var.function_name
  enable_cloudwatch_logs = true
  aws_region             = var.region
  disable_label_function_name_prefix = true
  enable_tracing = true
  tracing_mode = "Active"

  environment_variables = var.environment_variables
}

data "aws_iam_policy_document" "access_policy_document" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:DescribeLogStreams",
      "logs:PutLogEvents",
    ]
    resources = ["*"]
  }

  dynamic "statement" {
    for_each = length(var.sqs_write_arn_list) > 0 ? [1] : []
    content {
      effect = "Allow"
      actions = [
        "sqs:SendMessage",
        "sqs:ChangeMessageVisibility"
      ]
      resources = var.sqs_write_arn_list
    }
  }

  dynamic "statement" {
    for_each = length(var.sqs_read_arn_list) > 0 ? [1] : []
    content {
      effect = "Allow"
      actions = [
        "sqs:Get*",
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage"
      ]
      resources = var.sqs_read_arn_list
    }
  }

  dynamic "statement" {
    for_each = length(var.kinesis_read_arn_list) > 0 ? [1] : []
    content {
      effect = "Allow"
      actions = [
        "kinesis:Get*",
        "kinesis:List*",
        "kinesis:Describe*"
      ]
      resources = var.kinesis_read_arn_list
    }
  }


  statement {
    effect = "Allow"
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey"
    ]
    resources = var.kms_key_arn_list
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey*",
      "kms:DescribeKey"
    ]
    resources = ["*"] # need access to all KMS keys to decrypt data from all buckets in the account
  }
}

resource "aws_iam_policy" "access_policy" {
  name   = "${var.function_name}-process-data"
  policy = data.aws_iam_policy_document.access_policy_document.json
}

resource "aws_iam_role_policy_attachment" "access_policy_attach" {
  role       = module.sqs_message_processor.lambda_role_name
  policy_arn = aws_iam_policy.access_policy.arn
}


resource "aws_cloudwatch_metric_alarm" "error_alarm" {
  alarm_name          = module.sqs_message_processor.lambda_name
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  dimensions = {
    FunctionName = module.sqs_message_processor.lambda_name
  }
  period                    = "60"
  statistic                 = "Sum"
  alarm_actions             = [var.slack_sns_arn]
  threshold                 = "1"
  alarm_description         = "This metric monitors SQS message processors"
  insufficient_data_actions = []
  tags                      = var.tags
}
