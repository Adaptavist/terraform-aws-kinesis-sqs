data "aws_kinesis_stream" "kinesis_stream" {
  name = "ingest" + var.app_name
}

module "records_sqs" {
  source                = "../fifo_sqs"
  dlq_max_receive_count = 10
  queue_name            = var.app_name + "_" + var.record_type
  tags                  = local.tags
}

module "add_record_to_sqs" {
  source                = "../lambda"
  code_dir              = "../../../lambda/add_record_to_sqs"
  description           = "A lambda that takes a record from kinesis and pushes it onto a SQS FIFO queue"
  function_name         = "add_record_to_sqs"
  kms_key_arn_list      = [module.records_sqs.kms_key_arn]
  namespace             = local.namespace
  sqs_write_arn_list    = [module.records_sqs.queue_arn]
  kinesis_read_arn_list = [data.aws_kinesis_stream.kinesis_stream.arn]
  stage                 = var.stage
  tags                  = local.tags

  environment_variables = {
    SQS_QUEUE_URL = module.records_sqs.queue_url
    IS_FIFO_QUEUE = "true",
    DATA_PRIMARY_KEY = var.data_primary_key
  }

  region = var.region
}
