output "kms_key_arn" {
  value = aws_kms_key.kms_key.arn
}

output "queue_arn" {
  value = aws_sqs_queue.sqs_queue.arn
}

output "dlq_queue_arn" {
  value = aws_sqs_queue.dlq_sqs_queue.arn
}

output "queue_url" {
  value = aws_sqs_queue.sqs_queue.url
}