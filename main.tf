data "aws_kinesis_stream" "kinesis_stream" {
  name = var.stream_name
}

module "records_sqs" {
  source                = "./modules/fifo_sqs"
  dlq_max_receive_count = 10
  queue_name            = "${var.product}_${var.record_type}"
  tags                  = local.tags
  slack_sns_arn         = ""
}

module "add_record_to_sqs" {
  source                = "./modules/lambda"
  code_dir              = "add_record_to_sqs"
  description           = "A lambda that takes a record from kinesis and pushes it onto a SQS FIFO queue"
  function_name         = "add_${var.product}_${var.record_type}_record_to_sqs"
  kms_key_arn_list      = [module.records_sqs.kms_key_arn]
  namespace             = var.product
  sqs_write_arn_list    = [module.records_sqs.queue_arn]
  kinesis_read_arn_list = [data.aws_kinesis_stream.kinesis_stream.arn]
  stage                 = var.stage
  tags                  = local.tags
  slack_sns_arn         = ""

  environment_variables = {
    SQS_QUEUE_URL = module.records_sqs.queue_url
    IS_FIFO_QUEUE = "true",
    DATA_PRIMARY_KEY = var.data_primary_key
  }

  region = var.region
}

# module "process_record" {
#   source            = "./modules/lambda"
#   code_dir          = var.process_record_dir
#   description       = "A lambda that processes ${var.product} ${var.record_type} records"
#   function_name     = "process_${var.product}_${var.record_type}_record"
#   kms_key_arn_list  = [module.records_sqs.kms_key_arn]
#   namespace         = var.product
#   sqs_read_arn_list = [module.records_sqs.queue_arn]
#   stage             = var.stage
#   tags              = local.tags
#   region            = var.region
#   slack_sns_arn     = ""

#   environment_variables = {
#     HUBSPOT_ACCESS_TOKEN          = "data.aws_ssm_parameter.hubspot_access_token.value"
#     STITCH_LICENSE_OBJECT_TYPE_ID = "data.aws_ssm_parameter.stitch_account_hubspot_object_id.value"
#   }

# }


locals {
  service_name = "${var.product}-integration"
  tags = {
    "Avst:BusinessUnit" = "platforms"
    "Avst:Product"      = var.product
    "Avst:Stage:Name"   = var.stage
    "Avst:Stage:Type"   = var.stage_type
    "Avst:CostCenter"   = "platforms"
    "Avst:Project"      = "data-highway"
    "Avst:Team"         = "cloud-infra"
  }
}


module "event_sources" {
  source = "./modules/lambda_event_sources"

  kinesis_arn                    = data.aws_kinesis_stream.kinesis_stream.arn
  kinesis_processing_lambda_arn  = module.add_record_to_sqs.lambda_arn
  sqs_processing_lambda_arn      = var.process_record_lambda_arn
  sqs_queue_arn                  = module.records_sqs.queue_arn
  kinesis_processing_lambda_name = module.add_record_to_sqs.lambda_name
  sqs_processing_lambda_name     = var.process_record_lambda_name
}