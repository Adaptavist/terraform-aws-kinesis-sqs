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