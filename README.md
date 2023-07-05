# AWS Lambda

This module creates a set of AWS resources that will pull data from a Kinesis data stream, put it onto an SQS queue and have a Lambda pick up the item and process it. 
This module is designed to work with DIG.
The module allows for consumers of the module to supply their own lambda to process the records that are fed into the underlying SQS queue. 
This module also supports using a Redis cluster for long term deduplication as FIFO queues only offer a 5 minute dedup window.

The lambdas that consume data from the SQS queue can reside in the same account at the SQS queue but also a different account. 
In the case the lambda is in another account, there are two steps that need to be taken. Firstly, The execution role of the lambda will need to include the following permissions.

```
Statement": [
        {
            "Action": [
                "sqs:*"
                
            ],
            "Effect": "Allow",
            "Resource": [*]
        },
        {
            "Action": [
                "kms:Decrypt",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey*",
                "kms:DescribeKey"                
            ],
            "Effect": "Allow",
            "Resource": [*]
        }
```

The resource blocks should be tightened down as you see fit, these can be adjusted to the arn of the SQS queue or can use something like ```arn:aws:sqs:*:123456789012:*```.

Secondly, the lambda will need to have a trigger setup to enable the event sourcing using the SQS queue as the source. This can be done using IaC or using the AWS UI. IaC is the preferred choice. 

![Infra layout](doc/architecture.png)

See the above diagram. This module creates the resources numbered 9 and 8. 

The consumer supplied lambda is at number 10. 

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| availability\_zones | List of availability zones if in use | `list(string)` | `[]` | no |
| cluster\_id | The ID / name of the Redis cluster, if in use | `string` | `null` | no |
| data\_primary\_key | The primary data key, this is used as the group id of the underlying SQS FIFO queue | `string` | `null` | no |
| enable\_cloudwatch\_logs | Should cloudwatch logs be enabled for the lambda modules | `bool` | `true` | no |
| lambda\_execution\_roles | List of ARNS of the lambdas execution roles that need to subscribe the SQS queue created by this module. The role can be in any AWS account. | `list(string)` | n/a | yes |
| lambda\_function\_name\_override | Lambda function name override, used when migrating from older stacks as naming convention may not have been consistent | `string` | `""` | no |
| process\_record\_lambda\_arn | Optional lambda arn that will be used process the records on the SQS queue, this can only be used for lambdas that exist in the same AWS account. When supplying this variable the name of the lambda will also need to be included. | `string` | `""` | no |
| process\_record\_lambda\_name | Optional lambda name that will be used process the records on the SQS queue, this can only be used for lambdas that exist in the same AWS account. When supplying this variable the arn of the lambda will also need to be included. | `string` | `""` | no |
| product | Name of the product that is sending the data. e.g slack, salable | `string` | n/a | yes |
| record\_type | The record type, used for naming resources | `string` | n/a | yes |
| redis\_hash\_key | The key used to extract a value from the data and create a distinct record on | `string` | `null` | no |
| redis\_security\_group\_id | The security group id associated with the redis cluster | `string` | `null` | no |
| region | The region used, used for naming global resources like IAM roles | `string` | n/a | yes |
| slack\_sns\_arn | ARN of SNS topic to be used for alarms, alarms are trigger when messages end up on DQL | `string` | `null` | no |
| sqs\_event\_filtering\_path | The path to use to filter records off the kinesis stream, useful when dynamic endpoints have been used and only a subset of the records is required. | `string` | `null` | no |
| sqs\_queue\_name\_override | SQS queue name override, used when migrating from older stacks as naming convention may not have been consistent | `string` | `""` | no |
| sqs\_visibility\_timeout | The SQS visibility timeout in seconds | `number` | `60` | no |
| stage | Name stage of the development. e.g prod | `string` | n/a | yes |
| stage\_type | The type of the stage. e.g production | `string` | n/a | yes |
| stream\_name | The kinesis stream to attach to | `string` | n/a | yes |
| tags | Tags to be added to the created resources | `map(string)` | n/a | yes |
| vpc\_id | Id of the VPC attached to the lambda, if in use | `string` | `null` | no |
| vpc\_subnet\_ids | List of subnet IDs associated with the VPC, if in use | `list(string)` | `null` | no |
