variable "product" {
  type        = string
  description = "Name of the product that is sending the data. e.g slack, salable "
}

variable "lambda_execution_roles" {
  type        = list(string)
  description = "List of ARNS of the lambdas execution roles that need to subscribe the SQS queue created by this module. The role can be in any AWS account."
}

variable "sqs_visibility_timeout" {
  type        = number
  description = "The SQS visibility timeout in seconds"
  default     = 60
}

variable "stage" {
  type        = string
  description = "Name stage of the development. e.g prod"
}

variable "record_type" {
  type        = string
  description = "The record type, used for naming resources"
}


variable "tags" {
  type        = map(string)
  description = "Tags to be added to the created resources"
}

variable "stage_type" {
  type        = string
  description = "The type of the stage. e.g production  "
}

variable "stream_arn" {
  type        = string
  description = "The kinesis stream to attach to"
}

variable "process_record_lambda_arn" {
  type        = string
  default     = ""
  description = "Optional lambda arn that will be used process the records on the SQS queue, this can only be used for lambdas that exist in the same AWS account. When supplying this variable the name of the lambda will also need to be included."
}

variable "process_record_lambda_name" {
  type        = string
  default     = ""
  description = "Optional lambda name that will be used process the records on the SQS queue, this can only be used for lambdas that exist in the same AWS account. When supplying this variable the arn of the lambda will also need to be included."
}

variable "sqs_event_filtering_path" {
  type        = string
  default     = null
  description = "The path to use to filter records off the kinesis stream, useful when dynamic endpoints have been used and only a subset of the records is required."
}

variable "cluster_id" {
  type        = string
  description = "The ID / name of the Redis cluster, if in use"
  default     = null
}

variable "vpc_id" {
  type        = string
  description = "Id of the VPC attached to the lambda, if in use"
  default     = null
}

variable "vpc_subnet_ids" {
  type        = list(string)
  description = "List of subnet IDs associated with the VPC, if in use"
  default     = null
}

variable "availability_zones" {
  type        = list(string)
  default     = []
  description = "List of availability zones if in use"
}

variable "redis_security_group_id" {
  type        = string
  description = "The security group id associated with the redis cluster"
  default     = null
}

variable "lambda_function_name_override" {
  type        = string
  default     = ""
  description = "Lambda function name override, used when migrating from older stacks as naming convention may not have been consistent"
}

variable "sqs_queue_name_override" {
  type        = string
  default     = ""
  description = "SQS queue name override, used when migrating from older stacks as naming convention may not have been consistent"
}

variable "enable_cloudwatch_logs" {
  type        = bool
  default     = true
  description = "Should cloudwatch logs be enabled for the lambda modules"
}

variable "slack_sns_arn" {
  type        = string
  description = "ARN of SNS topic to be used for alarms, alarms are triggered by lambda errors. SNS topic must be in same region as aws.kinesis provider alias"
  default     = null
}

variable "slack_sns_arn_sqs" {
  type        = string
  description = "ARN of SNS topic to be used for alarms if SQS is in a different region, alarms are triggered when messages end up on DLQ. SNS topic must be in same region as aws.sqs provider alias"
  default     = null
}

variable "is_lambda_local" {
  type        = bool
  description = "Do the attached lambdas reside in the same aws account as the rest of the stack"
  default     = true
}

variable "config" {
  description = "Provides a list of environment variables to pass to the lambda, which determine how the data should be filtered"
  type = list(object({
    path_value_filter = string
    redis_hash_keys   = list(string)
  }))
  default = []
}