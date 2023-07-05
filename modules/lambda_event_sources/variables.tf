variable "sqs_queue_arn" {
  type = string
}

variable "sqs_processing_lambda_arn" {
  type = string
}

variable "sqs_processing_lambda_name" {
  type = string
}

variable "kinesis_arn" {
  type = string
}

variable "kinesis_processing_lambda_arn" {
  type = string
}

variable "kinesis_processing_lambda_name" {
  type = string
}

variable "sqs_event_filtering_path" {
  type = string
}

variable "process_record_lambda_arn" {
  type        = string
  default = ""
  description = "Optional lambda arn that will be used process the records on the SQS queue, this can only be used for lambdas that exist in the same AWS account. When supplying this variable the name of the lambda will also need to be included."
}

variable "process_record_lambda_name" {
  type        = string
  default = ""
  description = "Optional lambda name that will be used process the records on the SQS queue, this can only be used for lambdas that exist in the same AWS account. When supplying this variable the arn of the lambda will also need to be included."
}

