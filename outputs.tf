output "kms_key_arn" {
  value = module.records_sqs.kms_key_arn
}

output "queue_arn" {
  value = module.records_sqs.queue_arn
}

output "lambda_security_group_id" {
  value = module.add_record_to_sqs.lambda_security_group_id
}
