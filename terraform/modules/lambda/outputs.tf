output "lambda_arn" {
  value = module.sqs_message_processor.lambda_arn
}

output "lambda_name" {
  value = module.sqs_message_processor.lambda_name
}