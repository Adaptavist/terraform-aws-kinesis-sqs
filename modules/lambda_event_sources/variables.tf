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

