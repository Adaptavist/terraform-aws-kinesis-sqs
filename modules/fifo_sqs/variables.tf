variable "queue_name" {
  type = string
}

variable "dlq_max_receive_count" {
  type = number
}

variable "slack_sns_arn" {
  type = string
}

variable "lambda_execution_roles" {
  type = list(string)
}

variable "tags" {
  type = map(string)
}

variable "sqs_visibility_timeout" {
  type        = number
  description = "The SQS visibility timeout in seconds"
  default     = 60
}