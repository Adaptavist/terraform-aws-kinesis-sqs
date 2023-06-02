
provider "aws" {
  region = "us-west-2"
}

terraform {
  required_version = ">= 1.0.8"

  backend "s3" {
    region         = "us-east-1"
    bucket         = "platforms-stg-data-lake-437069093246-tf-state"
    key            = "module-aws-kinesis-to-sqs-test.tfstate"
    dynamodb_table = "platforms-stg-data-lake-437069093246-tf-state-lock"
    profile        = ""
    role_arn       = ""
    encrypt        = "true"
  }
}

module "example" {
  source         = "../"
  product        = "example-module-aws-kinesis-to-sqs"
  region         = "us-west-2"
  stage          = "stg"
  record_type    = "example"
  data_primary_key = "license_id"
  tags = {
    "Avst:BusinessUnit" = "platforms"
    "Avst:Stage:Type"   = "staging"
  }
  stage_type     = "staging"
  stream_name    = "ingest-veniture-licenses-events"
  sqs_event_filtering_path   = ""
  cluster_id     = "redis-shared-cluster"
  vpc_id         = "vpc-00f39bb7c588fc508"
  redis_hash_key = "data,app_id"
}

# stage             = var.stage
#   tags              = local.tags
#   region            = var.region
#   stage_type        = var.stage_type
#   data_primary_key       = "stitch_user_id"
#   sqs_event_filtering_path = ""
#   product                = "stitch-it"
#   record_type            = "contact"
#   process_record_lambda_arn     = module.process_contact_record.lambda_arn 
#   process_record_lambda_name     = module.process_contact_record.lambda_name
#   stream_name            = data.aws_kinesis_stream.kinesis_stream.name
#   lambda_function_name_override = "stitch-${var.stage}-addrecordtosqs-add_record_to_sqs"
#   sqs_queue_name_override = "stitch-contacts"