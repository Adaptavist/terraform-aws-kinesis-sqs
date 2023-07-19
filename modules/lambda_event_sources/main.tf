resource "aws_lambda_event_source_mapping" "sqs_source_mapping" {
  count  = var.is_lambda_local ? 1 : var.process_record_lambda_arn != "" && var.process_record_lambda_name != "" ? 1 : 0
  event_source_arn        = var.sqs_queue_arn
  function_name           = var.sqs_processing_lambda_arn
  function_response_types = ["ReportBatchItemFailures"]
}

resource "aws_lambda_event_source_mapping" "kinesis_source_mapping" {
  event_source_arn               = var.kinesis_arn
  function_name                  = var.kinesis_processing_lambda_arn
  starting_position              = "LATEST"
  bisect_batch_on_function_error = true
  maximum_retry_attempts         = 3
  dynamic "filter_criteria" {
    for_each = var.sqs_event_filtering_path != "" ? [1] : []
    content {
      filter {
        pattern = jsonencode({
          data : { path : [{"prefix": var.sqs_event_filtering_path}] }
        })
      }
    }
  }
}

resource "aws_lambda_permission" "allow_sqs" {
  count  = var.is_lambda_local ? 1 : var.process_record_lambda_arn != "" && var.process_record_lambda_name != "" ? 1 : 0
  statement_id  = "AllowExecutionSqs"
  action        = "lambda:InvokeFunction"
  function_name = var.sqs_processing_lambda_name
  principal     = "sqs.amazonaws.com"
  source_arn    = var.sqs_queue_arn
}

resource "aws_lambda_permission" "allow_kinesis" {
  statement_id  = "AllowExecutionKinesis"
  action        = "lambda:InvokeFunction"
  function_name = var.kinesis_processing_lambda_name
  principal     = "kinesis.amazonaws.com"
  source_arn    = var.kinesis_arn
}