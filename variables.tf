variable "product" {
  type = string
}

variable "region" {
  type = string
}

variable "stage" {
  type = string
}

variable "record_type" {
  type = string
}

variable "data_primary_key" {
  type = string
}

variable "tags" {
  type = map(string)
}

variable "stage_type" {
  type = string
}

variable "stream_name" {
  type = string
}

variable "process_record_lambda_arn" {
  type = string
}

variable "process_record_lambda_name" {
  type = string
}

variable "sqs_event_filtering_path" {
  type = string
}
