module "records_sqs" {
  providers = {
    aws = aws.sqs
  }

  source                 = "./modules/fifo_sqs"

  dlq_max_receive_count  = 10
  queue_name             = coalesce(var.sqs_queue_name_override, "${var.product}-${var.record_type}")
  tags                   = local.tags
  slack_sns_arn          = local.is_multi_region ? var.slack_sns_arn_sqs : var.slack_sns_arn
  sqs_visibility_timeout = var.sqs_visibility_timeout
  lambda_execution_roles = var.lambda_execution_roles
}

module "add_record_to_sqs" {
  providers = {
    aws = aws.kinesis
  }

  source                 = "./modules/lambda"

  code_dir               = "${path.module}/add_record_to_sqs"
  description            = "A lambda that takes a record from kinesis and pushes it onto a SQS FIFO queue"
  function_name          = coalesce(var.lambda_function_name_override, "add_${var.product}_${var.record_type}_record_to_sqs")
  kms_key_arn_list       = [module.records_sqs.kms_key_arn]
  namespace              = var.product
  sqs_write_arn_list     = [module.records_sqs.queue_arn]
  kinesis_read_arn_list  = [var.stream_arn]
  stage                  = var.stage
  tags                   = local.tags
  slack_sns_arn          = var.slack_sns_arn
  enable_cloudwatch_logs = var.enable_cloudwatch_logs
  product                = var.product

  environment_variables = {
    SQS_REGION       = data.aws_region.sqs_region.name
    SQS_QUEUE_URL    = module.records_sqs.queue_url
    IS_FIFO_QUEUE    = "true",
    DATA_PRIMARY_KEY = var.data_primary_key
    REDIS_HASH_KEY   = var.redis_hash_key
    HOST             = var.cluster_id != null ? data.aws_elasticache_cluster.redis_cluster[0].cache_nodes[0].address : null
    PATH_VALUE_FILTER = var.path_value_filter
  }

  region         = data.aws_region.kinesis_region.name
  vpc_subnet_ids = var.vpc_id != null ? values(data.aws_subnet.private_subnets)[*].id : []
  vpc_id         = var.vpc_id
}

# Set the inbound rules for the security group, required for redis interaction
resource "aws_security_group_rule" "redis_security_group_rule" {
  provider                 = aws.kinesis
  count                    = var.cluster_id != null ? 1 : 0

  type                     = "ingress"
  from_port                = 6379
  to_port                  = 6379
  protocol                 = "tcp"
  source_security_group_id = module.add_record_to_sqs.lambda_security_group_id
  security_group_id        = var.redis_security_group_id
}


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

  is_multi_region = data.aws_region.kinesis_region.name != data.aws_region.sqs_region.name ? true : false

}


module "event_sources" {
  providers = {
    aws = aws.kinesis
  }

  source = "./modules/lambda_event_sources"

  kinesis_arn                    = var.stream_arn
  kinesis_processing_lambda_arn  = module.add_record_to_sqs.lambda_arn
  sqs_processing_lambda_arn      = var.process_record_lambda_arn
  sqs_queue_arn                  = module.records_sqs.queue_arn
  kinesis_processing_lambda_name = module.add_record_to_sqs.lambda_name
  sqs_processing_lambda_name     = var.process_record_lambda_name
  sqs_event_filtering_path       = var.sqs_event_filtering_path
  process_record_lambda_arn      = var.process_record_lambda_arn
  process_record_lambda_name     = var.process_record_lambda_name
  is_lambda_local                = var.is_lambda_local
}
