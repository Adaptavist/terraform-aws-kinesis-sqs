output "kms_key_arn" {
  value = module.records_sqs.kms_key_arn
}

output "lambda_security_group_id" {
  value = module.add_record_to_sqs.lambda_security_group_id
}

output "sqs_queue_arn" {
  value = module.records_sqs.queue_arn
}
