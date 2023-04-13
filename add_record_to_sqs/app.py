import os
import logging
import boto3
import base64
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info('Loading function')

sqs = boto3.client('sqs')
queue_url = os.environ.get('SQS_QUEUE_URL')
is_fifo_queue = os.environ.get('IS_FIFO_QUEUE')
logger.info("Queue url : " + queue_url)
data_primary_key = os.environ.get('DATA_PRIMARY_KEY')

def lambda_handler(event, context):

    logger.info(event)

    for record in event['Records']:
        dataBase64 = record['kinesis']['data']
        dataJson = base64.b64decode(dataBase64)
        data = json.loads(dataJson)
        logger.info(data)
        groupId = ""
        
        if data[data_primary_key] :
            groupId = data[data_primary_key]
        else:
            groupId = dataBase64    

        sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=dataJson.decode("utf-8"),
                MessageDeduplicationId=dataBase64,
                MessageGroupId=groupId)      











