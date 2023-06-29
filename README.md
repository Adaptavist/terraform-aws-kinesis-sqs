# AWS Lambda

This module creates a set of AWS resources that will pull data from a Kinesis data stream, put it onto an SQS queue and have a Lambda pick up the item and process it.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| availability\_zones | List of availability zones if in use | `list(string)` | `[]` | no |
| cluster\_id | The ID / name of the Redis cluster, if in use | `string` | `null` | no |
| data\_primary\_key | The primary data key, this is used as the group id of the underlying SQS FIFO queue | `string` | `null` | no |
| enable\_cloudwatch\_logs | Should cloudwatch logs be enabled for the lambda modules | `bool` | `true` | no |
| lambda\_execution\_roles | List of ARNS of the lambdas that need to subscribe the SQS queue created by this module | `list(string)` | n/a | yes |
| lambda\_function\_name\_override | Lambda function name override, used when migrating from older stacks as naming convention may not have been consistent | `string` | `""` | no |
| process\_record\_lambda\_arn | The lambda arn that will be used process the records on the SQS queue | `string` | n/a | yes |
| process\_record\_lambda\_name | The lambda name that will be used process the records on the SQS queue | `string` | n/a | yes |
| product | Name of the product that is sending the data. e.g slack, salable | `string` | n/a | yes |
| record\_type | The record type, used for naming resources | `string` | n/a | yes |
| redis\_hash\_key | The key used to extract a value from the data and create a distinct record on | `string` | `null` | no |
| redis\_security\_group\_id | The security group id associated with the redis cluster | `string` | `null` | no |
| region | The region used, used for naming global resources like IAM roles | `string` | n/a | yes |
| sqs\_event\_filtering\_path | The path to use to filter records off the kinesis stream, useful when dynamic endpoints have been used and only a subset of the records is required. | `string` | `null` | no |
| sqs\_queue\_name\_override | SQS queue name override, used when migrating from older stacks as naming convention may not have been consistent | `string` | `""` | no |
| stage | Name stage of the development. e.g prod | `string` | n/a | yes |
| stage\_type | The type of the stage. e.g production | `string` | n/a | yes |
| stream\_name | The kinesis stream to attach to | `string` | n/a | yes |
| tags | Tags to be added to the created resources | `map(string)` | n/a | yes |
| vpc\_id | Id of the VPC attached to the lambda, if in use | `string` | `null` | no |
| vpc\_subnet\_ids | List of subnet IDs associated with the VPC, if in use | `list(string)` | `null` | no |

