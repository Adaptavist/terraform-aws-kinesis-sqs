data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

resource "aws_sqs_queue" "sqs_queue" {
  name                       = "${var.queue_name}.fifo"
  fifo_queue                 = true
  deduplication_scope        = "messageGroup"
  fifo_throughput_limit      = "perMessageGroupId"
  visibility_timeout_seconds = 60
  message_retention_seconds  = 1209600 # 14 days which is the max
  kms_master_key_id          = aws_kms_key.kms_key.key_id
  policy                     = data.aws_iam_policy_document.sqs_policy.json
  kms_data_key_reuse_period_seconds = 300

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq_sqs_queue.arn
    maxReceiveCount     = var.dlq_max_receive_count
  })

  tags = var.tags
}

resource "aws_sqs_queue" "dlq_sqs_queue" {
  name                      = "${var.queue_name}-dlq.fifo"
  kms_master_key_id         = aws_kms_key.kms_key.key_id
  fifo_queue                = true
  deduplication_scope       = "messageGroup"
  fifo_throughput_limit     = "perMessageGroupId"
  message_retention_seconds = 1209600 # 14 days which is the max
  policy                    = data.aws_iam_policy_document.dlq_sqs_policy.json
  kms_data_key_reuse_period_seconds = 300

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = ["arn:aws:sqs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:${var.queue_name}.fifo"] // We have to build arn like this or we get a cycle
  })

  tags = var.tags
}

resource "aws_kms_key" "kms_key" {
  description            = "Key used for the SQS queue ${var.queue_name}"
  policy                 = data.aws_iam_policy_document.kms_policy.json
  tags                   = var.tags
  is_enabled             = true
  enable_key_rotation    = true
}

resource "aws_kms_alias" "kms_alias" {
  name          = "alias/${var.queue_name}"
  target_key_id = aws_kms_key.kms_key.key_id
}

resource "aws_cloudwatch_metric_alarm" "dlq_alarm" {
  alarm_name                = "${var.queue_name}-dlq"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = "ApproximateNumberOfMessagesVisible"
  namespace                 = "AWS/SQS"
  period                    = "60"
  statistic                 = "Sum"
  alarm_actions             = [var.slack_sns_arn]
  threshold                 = "1"
  alarm_description         = "This metric monitors DLQ length"
  insufficient_data_actions = []
  tags                      = var.tags

  dimensions = {
    QueueName = aws_sqs_queue.dlq_sqs_queue.name
  }
}

data "aws_iam_policy_document" "sqs_policy" {

  statement {
    sid    = "lambda_receive"
    effect = "Allow"
    actions = [
      "sqs:ReceiveMessage",
      "sqs:Get*",
      "sqs:Delete*"
    ]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    resources = ["*"]
  }

  statement {
    sid    = "lambda_send_message"
    effect = "Allow"
    actions = [
      "sqs:SendMessage"
    ]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    resources = ["*"]
  }
}

data "aws_iam_policy_document" "dlq_sqs_policy" {

  statement {
    sid    = "lambda_receive"
    effect = "Allow"
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage"
    ]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }

    resources = ["*"]
  }
}

data "aws_iam_policy_document" "kms_policy" {

  statement {
    sid     = "s3_access"
    effect  = "Allow"
    actions = ["kms:*"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    resources = ["*"]
  }

  statement {
    sid     = "account_access"
    effect  = "Allow"
    actions = ["kms:*"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    resources = ["*"]
  }
}