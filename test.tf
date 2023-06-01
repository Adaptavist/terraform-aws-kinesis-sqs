
provider "aws" {
  region = "us-west-2"
}

terraform {
  required_version = ">= 1.0.8"

  backend "s3" {
    region         = "us-east-1"
    bucket         = "platforms-stg-data-lake-437069093246-tf-state"
    key            = "module-aws-kinesis-to-sqs-test.tfstate"
    dynamodb_table = "module-aws-kinesis-to-sqs-test-437069093246-tf-state-lock"
    profile        = ""
    role_arn       = ""
    encrypt        = "true"
  }
}

module "example" {
  source         = "./main.tf"
  product        = "example-module-aws-kinesis-to-sqs"
  region         = "us-west-2"
  stage          = "stg"
  record_type    = "example"
  data_primary_key = null
  tags = {
    "Avst:BusinessUnit" = "platforms"
    "Avst:Stage:Type"   = "example"
  }
  stage_type     = "example"
  stream_name    = "example-stream"
  process_record_lambda_arn = "arn:aws:lambda:us-west-2:1234567890:function:example-lambda"
  process_record_lambda_name = "example-lambda"
  sqs_event_filtering_path   = "example/path"
  cluster_id     = null
  vpc_id         = null
  redis_hash_key = null
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