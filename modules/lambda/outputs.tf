output "lambda_arn" {
  value = module.sqs_message_processor.lambda_arn
}

output "lambda_name" {
  value = module.sqs_message_processor.lambda_name
}

output "lambda_security_group_id" {
  value = aws_security_group.lambda_security_group.id
}