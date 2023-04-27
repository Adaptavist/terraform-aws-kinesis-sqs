# AWS Lambda

This module creates a set of AWS resources that will pull data from a Kinesis data stream, put it onto an SQS queue and have a Lambda pick up the item and process it. 

## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | n/a |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_add_record_to_sqs"></a> [add\_record\_to\_sqs](#module\_add\_record\_to\_sqs) | ./modules/lambda | n/a |
| <a name="module_event_sources"></a> [event\_sources](#module\_event\_sources) | ./modules/lambda_event_sources | n/a |
| <a name="module_process_record"></a> [process\_record](#module\_process\_record) | ./modules/lambda | n/a |
| <a name="module_records_sqs"></a> [records\_sqs](#module\_records\_sqs) | ./modules/fifo_sqs | n/a |

## Resources

| Name | Type |
|------|------|
| [aws_kinesis_stream.kinesis_stream](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/kinesis_stream) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_data_primary_key"></a> [data\_primary\_key](#input\_data\_primary\_key) | the primary key for the json payload sent by the product that is to be processed. e.g account_id | `string` | n/a | yes |
| <a name="input_product"></a> [product](#input\_product) | the name of the product that is sending the data. e.g slack, salable | `string` | n/a | yes |
| <a name="input_record_type"></a> [record\_type](#input\_record\_type) | the type of record sent by the product that to be processed. e.g contact, account etc | `string` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | n/a | `string` | aws region | yes |
| <a name="input_stage"></a> [stage](#input\_stage) | the name stage of the development. e.g prod | `string` | n/a | yes |
| <a name="input_stage_type"></a> [stage\_type](#input\_stage\_type) | the type of the stage. e.g production | `string` | n/a | yes |
| <a name="input_stream_name"></a> [stream\_name](#input\_stream\_name) | the name of the kinesis stream that the json payload will be fulled from. e.g ingest-sendable-account | `string` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | n/a | `map(string)` | n/a | yes |
| <a name="input_sqs_event_filtering_pathr"></a> [sqs_event_filtering_path](#input\_sqs_event_filtering_path) | the relative path of the dig endpoint. Use this to filter the records coming from kinesis to only ones coming from this path | `string` | n/a | no |

## Outputs

No outputs.
