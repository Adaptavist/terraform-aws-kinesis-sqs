data "aws_kinesis_stream" "kinesis_stream" {
  name = var.stream_name
}

data "aws_elasticache_cluster" "redis_cluster" {
  count      = var.cluster_id != null ? 1 : 0
  cluster_id = var.cluster_id
}

data "aws_subnet" "private_subnets" {
  for_each = var.vpc_id != null ? toset(var.availability_zones) : toset([])

  vpc_id = var.vpc_id

  filter {
    name   = "tag:Avst:Service:Component"
    values = ["private-subnet"]
  }

  availability_zone = each.value
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
  code_dir              = "./add_record_to_sqs"
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
    REDIS_HASH_KEY = var.redis_hash_key
    HOST = var.cluster_id != null ? data.aws_elasticache_cluster.redis_cluster[0].cache_nodes[0].address : null
  }

  region = var.region
  vpc_subnet_ids = var.vpc_id != null ? values(data.aws_subnet.private_subnets)[*].id : []
  vpc_id          = var.vpc_id
}

# Set the inbound rules for the security group, required for redis interaction
resource "aws_security_group_rule" "redis_security_group_rule" {
  type              = "ingress"
  from_port         = 6379
  to_port           = 6379
  protocol          = "tcp"
  source_security_group_id = module.add_record_to_sqs.lambda_security_group_id
  security_group_id = var.redis_security_group_id
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
}


module "event_sources" {
  source = "./modules/lambda_event_sources"

  kinesis_arn                    = data.aws_kinesis_stream.kinesis_stream.arn
  kinesis_processing_lambda_arn  = module.add_record_to_sqs.lambda_arn
  sqs_processing_lambda_arn      = var.process_record_lambda_arn
  sqs_queue_arn                  = module.records_sqs.queue_arn
  kinesis_processing_lambda_name = module.add_record_to_sqs.lambda_name
  sqs_processing_lambda_name     = var.process_record_lambda_name
  sqs_event_filtering_path       = var.sqs_event_filtering_path
}
