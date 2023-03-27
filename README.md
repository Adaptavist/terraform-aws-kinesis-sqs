# AWS Lambda

This module creates a set of AWS resources that will pull data from a Kinesis data stream, put it onto an SQS queue and have a Lambda pick up the item and process it. 

## Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| source |the path to the terraform module (github or local)| `string` | `null` | yes |
| stage |the name stage of the development. e.g prod| `string` | `null` | yes |
| stage_type |the type of the stage. e.g production| `string` | `null` | yes |
| data_primary_key |the primary key for the json payload sent by the product that is to be processed. e.g account_id| `string` | `null` | yes |
| product |the name of the product that is sending the data. e.g slack, salable| `string` | `null` | yes |
| record_type |the type of record sent by the product that to be processed. e.g contact, account etc| `string` | `null` | yes |
| process_redcord_dir |the path to the folder containing the code for the lambda that will process the record. e.g ./process_account_record| `string` | `null` | yes |
| stream_name |the name of the kinesis stream that the json payload will be fulled from. e.g ingest-sendable-account | `string` | `null` | yes |

## Outputs

| Name                    | Description                                                       |
| ----------------------- | ----------------------------------------------------------------- |
| lambda_name             | The name of the Lambda Function                                   |
